<template>
  <div class="registration-manage">
    <div class="page-header">
      <h3>报名管理</h3>
      <div class="header-actions">
        <el-button type="danger" @click="handleClearAll"><el-icon><Delete /></el-icon>清空所有</el-button>
        <el-button @click="showImportDialog = true"><el-icon><Upload /></el-icon>批量导入</el-button>
        <el-button type="primary" @click="handleAdd"><el-icon><Plus /></el-icon>新增报名</el-button>
      </div>
    </div>

    <SearchForm v-model="searchForm" :loading="loading" @search="handleSearch" @reset="handleReset">
      <el-form-item label="项目">
        <el-select v-model="searchForm.event_id" placeholder="全部项目" clearable filterable style="width: 150px" @change="onSearchEventChange">
          <el-option v-for="e in events" :key="e.id" :label="e.name" :value="e.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="组别">
        <el-select v-model="searchForm.group_name" placeholder="全部组别" clearable filterable style="width: 120px">
          <el-option v-for="g in searchGroupOptions" :key="g.name" :label="g.name" :value="g.name" />
        </el-select>
      </el-form-item>
      <el-form-item label="年级">
        <el-select v-model="searchForm.grade_id" placeholder="全部年级" clearable filterable style="width: 120px" @change="onGradeChange">
          <el-option v-for="g in grades" :key="g.id" :label="g.name" :value="g.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="班级">
        <el-select v-model="searchForm.class_id" placeholder="全部班级" clearable filterable style="width: 120px">
          <el-option v-for="c in filteredClasses" :key="c.id" :label="searchForm.grade_id ? c.name : `${c.grade_name || ''} ${c.name}`" :value="c.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="学生">
        <el-input v-model="searchForm.student_name" placeholder="学生姓名" clearable style="width: 120px" />
      </el-form-item>
    </SearchForm>

    <DataTable :data="registrations" :loading="loading" :total="total" v-model:current-page="currentPage" v-model:page-size="pageSize" @page-change="handlePageChange">
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column label="学生" width="150">
        <template #default="{ row }">{{ row.student_name }} ({{ row.student_no }})</template>
      </el-table-column>
      <el-table-column label="班级" width="150">
        <template #default="{ row }">{{ row.grade_name }} {{ row.class_name }}</template>
      </el-table-column>
      <el-table-column label="项目" width="120">
        <template #default="{ row }">{{ row.event_name }}</template>
      </el-table-column>
      <el-table-column label="组别" width="100">
        <template #default="{ row }">{{ row.group_name || '-' }}</template>
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
          <el-select v-model="form.event_id" placeholder="请选择项目" style="width: 100%" @change="onFormEventChange">
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

    <ImportDialog v-model="showImportDialog" title="批量导入报名" :multiple="true" @import="handleImport" @success="handleImportSuccess" />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/api/request'
import DataTable from '@/components/common/DataTable.vue'
import SearchForm from '@/components/common/SearchForm.vue'
import ImportDialog from '@/components/common/ImportDialog.vue'

const loading = ref(false)
const events = ref([])
const grades = ref([])
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

const searchForm = reactive({ event_id: null, group_name: null, grade_id: null, class_id: null, student_name: '' })
const form = reactive({ student_id: null, event_id: null, group_id: null, lane_no: 0 })

const searchGroupOptions = ref([])

const rules = {
  student_id: [{ required: true, message: '请选择学生', trigger: 'change' }],
  event_id: [{ required: true, message: '请选择项目', trigger: 'change' }]
}

const formatDate = (date) => date ? new Date(date).toLocaleString('zh-CN') : '-'

const loadEvents = async () => { 
  const res = await request.get('/events')
  events.value = res.data || res || [] 
}
const loadGrades = async () => { 
  const res = await request.get('/grades')
  grades.value = res.data || res || [] 
}
const loadClasses = async () => { 
  const res = await request.get('/classes')
  classes.value = res.data || res || [] 
}
const loadAllGroups = async () => {
  const res = await request.get('/events/groups/all')
  searchGroupOptions.value = res.data || res || []
}

// 根据选中的年级过滤班级
const filteredClasses = computed(() => {
  if (!searchForm.grade_id) return classes.value
  return classes.value.filter(c => c.grade_id === searchForm.grade_id)
})

// 年级变化时清空班级选择
const onGradeChange = () => {
  searchForm.class_id = null
}

// 搜索表单：项目变化时清空组别选择（组别已在页面加载时获取）
const onSearchEventChange = () => {
  // 如果需要按项目过滤组别，可以在这里实现
  // 目前组别是独立筛选，不需要清空
}

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

// 编辑表单：项目变化时加载组别
const onFormEventChange = async () => {
  form.group_id = null
  if (form.event_id) {
    const res = await request.get(`/events/${form.event_id}/groups`)
    groupOptions.value = res.data || res || []
  } else {
    groupOptions.value = []
  }
}

const handleSearch = () => { currentPage.value = 1; loadData() }
const handleReset = () => { 
  Object.assign(searchForm, { event_id: null, group_name: null, grade_id: null, class_id: null, student_name: '' })
}
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
  // 使用扁平化字段构建学生选项
  studentOptions.value = row.student_id ? [{ id: row.student_id, name: row.student_name, student_no: row.student_no }] : []
  await onFormEventChange()
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

const handleImport = async (files, { resolve, reject }) => {
  try {
    const formData = new FormData()
    // 支持多文件上传
    if (Array.isArray(files)) {
      files.forEach(file => formData.append('files', file))
    } else {
      formData.append('files', files)
    }
    const result = await request.post('/registrations/import', formData)
    
    // 转换后端返回格式为前端期望格式
    const successCount = result.success || 0
    const failCount = result.failed || 0
    const errors = (result.errors || []).map(errStr => {
      // 解析错误字符串，提取行号和消息
      // 格式: "[文件名] [Sheet名] 第X行: 错误消息" 或 "第X行: 错误消息"
      const match = errStr.match(/第(\d+)行[：:]\s*(.+)/)
      if (match) {
        return { row: parseInt(match[1]), message: match[2] }
      }
      return { row: 0, message: errStr }
    })
    
    resolve({
      success: failCount === 0 && successCount > 0,
      successCount,
      failCount,
      errors
    })
  } catch (e) { reject(e) }
}

const handleImportSuccess = () => loadData()

const handleClearAll = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有报名记录吗？此操作将同时删除所有学生、班级、年级数据，且不可恢复！',
      '危险操作',
      { type: 'error', confirmButtonText: '确定清空', cancelButtonText: '取消' }
    )
    await request.delete('/registrations')
    ElMessage.success('已清空所有数据')
    await loadData()
    await loadClasses()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.message || '操作失败')
  }
}

onMounted(() => { loadEvents(); loadGrades(); loadClasses(); loadAllGroups(); loadData() })
</script>

<style scoped>
.registration-manage { padding: 20px; background: #fff; border-radius: 4px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h3 { margin: 0; }
.header-actions { display: flex; gap: 10px; }
</style>
