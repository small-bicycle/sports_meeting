<template>
  <div class="registration-manage">
    <div class="page-header">
      <h3>报名管理</h3>
      <div class="header-actions">
        <el-button @click="showImportDialog = true"><el-icon><Upload /></el-icon>批量导入</el-button>
        <el-button type="primary" @click="handleAdd"><el-icon><Plus /></el-icon>新增报名</el-button>
      </div>
    </div>

    <SearchForm v-model="searchForm" :loading="loading" @search="handleSearch" @reset="handleReset">
      <el-form-item label="项目">
        <el-select v-model="searchForm.event_id" placeholder="全部项目" clearable filterable style="width: 150px">
          <el-option v-for="e in events" :key="e.id" :label="e.name" :value="e.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="班级">
        <el-select v-model="searchForm.class_id" placeholder="全部班级" clearable filterable style="width: 150px">
          <el-option v-for="c in classes" :key="c.id" :label="`${c.grade?.name || ''} ${c.name}`" :value="c.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="学生">
        <el-input v-model="searchForm.student_name" placeholder="学生姓名" clearable style="width: 120px" />
      </el-form-item>
    </SearchForm>

    <DataTable :data="registrations" :loading="loading" :total="total" v-model:current-page="currentPage" v-model:page-size="pageSize" @page-change="handlePageChange">
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column label="学生" width="150">
        <template #default="{ row }">{{ row.student?.name }} ({{ row.student?.student_no }})</template>
      </el-table-column>
      <el-table-column label="班级" width="150">
        <template #default="{ row }">{{ row.student?.class_info?.grade?.name }} {{ row.student?.class_info?.name }}</template>
      </el-table-column>
      <el-table-column label="项目" width="120">
        <template #default="{ row }">{{ row.event?.name }}</template>
      </el-table-column>
      <el-table-column label="组别" width="100">
        <template #default="{ row }">{{ row.group?.name || '-' }}</template>
      </el-table-column>
      <el-table-column prop="lane_no" label="道次" width="70" />
      <el-table-column prop="created_at" label="报名时间" width="160">
        <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
          <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </DataTable>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑报名' : '新增报名'" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="学生" prop="student_id">
          <el-select v-model="form.student_id" placeholder="请选择学生" filterable remote :remote-method="searchStudents" style="width: 100%">
            <el-option v-for="s in studentOptions" :key="s.id" :label="`${s.name} (${s.student_no})`" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="项目" prop="event_id">
          <el-select v-model="form.event_id" placeholder="请选择项目" style="width: 100%" @change="onEventChange">
            <el-option v-for="e in events" :key="e.id" :label="e.name" :value="e.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="组别" prop="group_id">
          <el-select v-model="form.group_id" placeholder="请选择组别" style="width: 100%">
            <el-option v-for="g in groupOptions" :key="g.id" :label="g.name" :value="g.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="道次">
          <el-input-number v-model="form.lane_no" :min="0" :max="20" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <ImportDialog v-model="showImportDialog" title="批量导入报名" @import="handleImport" @success="handleImportSuccess" />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/api/request'
import DataTable from '@/components/common/DataTable.vue'
import SearchForm from '@/components/common/SearchForm.vue'
import ImportDialog from '@/components/common/ImportDialog.vue'

const loading = ref(false)
const events = ref([])
const classes = ref([])
const registrations = ref([])
const studentOptions = ref([])
const groupOptions = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const dialogVisible = ref(false)
const showImportDialog = ref(false)
const isEdit = ref(false)
const submitLoading = ref(false)
const formRef = ref(null)
const currentId = ref(null)

const searchForm = reactive({ event_id: null, class_id: null, student_name: '' })
const form = reactive({ student_id: null, event_id: null, group_id: null, lane_no: 0 })

const rules = {
  student_id: [{ required: true, message: '请选择学生', trigger: 'change' }],
  event_id: [{ required: true, message: '请选择项目', trigger: 'change' }]
}

const formatDate = (date) => date ? new Date(date).toLocaleString('zh-CN') : '-'

const loadEvents = async () => { events.value = (await request.get('/events')).data || [] }
const loadClasses = async () => { classes.value = (await request.get('/classes')).data || [] }

const loadData = async () => {
  loading.value = true
  try {
    const params = { page: currentPage.value, page_size: pageSize.value, ...searchForm }
    Object.keys(params).forEach(k => { if (!params[k]) delete params[k] })
    const res = await request.get('/registrations', { params })
    registrations.value = res.data || res.items || []
    total.value = res.total || registrations.value.length
  } finally { loading.value = false }
}

const searchStudents = async (query) => {
  if (!query) return
  const res = await request.get('/students', { params: { name: query, page_size: 20 } })
  studentOptions.value = res.data || res.items || []
}

const onEventChange = async () => {
  form.group_id = null
  if (form.event_id) {
    const res = await request.get(`/events/${form.event_id}/groups`)
    groupOptions.value = res.data || res || []
  } else {
    groupOptions.value = []
  }
}

const handleSearch = () => { currentPage.value = 1; loadData() }
const handleReset = () => { Object.assign(searchForm, { event_id: null, class_id: null, student_name: '' }) }
const handlePageChange = () => loadData()

const resetForm = () => { Object.assign(form, { student_id: null, event_id: null, group_id: null, lane_no: 0 }); currentId.value = null }
const handleAdd = () => { isEdit.value = false; resetForm(); dialogVisible.value = true }

const handleEdit = async (row) => {
  isEdit.value = true
  currentId.value = row.id
  form.student_id = row.student_id
  form.event_id = row.event_id
  form.group_id = row.group_id
  form.lane_no = row.lane_no || 0
  studentOptions.value = row.student ? [row.student] : []
  await onEventChange()
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该报名记录吗？', '提示', { type: 'warning' })
    await request.delete(`/registrations/${row.id}`)
    ElMessage.success('删除成功')
    await loadData()
  } catch (e) { if (e !== 'cancel') ElMessage.error(e.message || '删除失败') }
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitLoading.value = true
  try {
    if (isEdit.value) {
      await request.put(`/registrations/${currentId.value}`, form)
      ElMessage.success('更新成功')
    } else {
      await request.post('/registrations', form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    await loadData()
  } catch (e) { ElMessage.error(e.response?.data?.detail || e.message || '操作失败') }
  finally { submitLoading.value = false }
}

const handleImport = async (file, { resolve, reject }) => {
  try {
    const formData = new FormData()
    formData.append('file', file)
    const result = await request.post('/registrations/import', formData)
    resolve(result)
  } catch (e) { reject(e) }
}

const handleImportSuccess = () => loadData()

onMounted(() => { loadEvents(); loadClasses(); loadData() })
</script>

<style scoped>
.registration-manage { padding: 20px; background: #fff; border-radius: 4px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h3 { margin: 0; }
.header-actions { display: flex; gap: 10px; }
</style>
