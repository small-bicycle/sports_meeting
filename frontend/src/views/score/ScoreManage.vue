<template>
  <div class="score-manage">
    <div class="page-header">
      <h3>成绩管理</h3>
      <div class="header-actions">
        <el-button @click="showImportDialog = true"><el-icon><Upload /></el-icon>批量导入</el-button>
        <el-button type="primary" @click="handleAdd"><el-icon><Plus /></el-icon>录入成绩</el-button>
      </div>
    </div>

    <SearchForm v-model="searchForm" :loading="loading" @search="handleSearch" @reset="handleReset">
      <el-form-item label="项目">
        <el-select v-model="searchForm.event_id" placeholder="全部项目" clearable filterable style="width: 150px">
          <el-option v-for="e in events" :key="e.id" :label="e.name" :value="e.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="轮次">
        <el-select v-model="searchForm.round" placeholder="全部轮次" clearable style="width: 100px">
          <el-option label="预赛" value="preliminary" />
          <el-option label="决赛" value="final" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="searchForm.is_valid" placeholder="全部" clearable style="width: 100px">
          <el-option label="有效" :value="true" />
          <el-option label="作废" :value="false" />
        </el-select>
      </el-form-item>
    </SearchForm>

    <DataTable :data="scores" :loading="loading" :total="total" v-model:current-page="currentPage" v-model:page-size="pageSize" @page-change="handlePageChange">
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column label="学生" width="150">
        <template #default="{ row }">{{ row.registration?.student?.name }}</template>
      </el-table-column>
      <el-table-column label="项目" width="120">
        <template #default="{ row }">{{ row.registration?.event?.name }}</template>
      </el-table-column>
      <el-table-column prop="round" label="轮次" width="80">
        <template #default="{ row }">
          <el-tag size="small">{{ row.round === 'preliminary' ? '预赛' : '决赛' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="value" label="成绩" width="100" />
      <el-table-column prop="rank" label="名次" width="70" />
      <el-table-column prop="points" label="积分" width="70" />
      <el-table-column prop="is_valid" label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_valid ? 'success' : 'danger'" size="small">
            {{ row.is_valid ? '有效' : '作废' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
          <el-button v-if="row.is_valid" type="warning" link @click="handleInvalidate(row)">作废</el-button>
          <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </DataTable>

    <!-- 录入/编辑成绩弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑成绩' : '录入成绩'" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item v-if="!isEdit" label="报名" prop="registration_id">
          <el-select v-model="form.registration_id" placeholder="请选择报名记录" filterable remote :remote-method="searchRegistrations" style="width: 100%">
            <el-option v-for="r in registrationOptions" :key="r.id" :label="`${r.student?.name} - ${r.event?.name}`" :value="r.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="轮次" prop="round">
          <el-select v-model="form.round" style="width: 100%">
            <el-option label="预赛" value="preliminary" />
            <el-option label="决赛" value="final" />
          </el-select>
        </el-form-item>
        <el-form-item label="成绩" prop="value">
          <el-input v-model="form.value" placeholder="请输入成绩" />
        </el-form-item>
        <el-form-item label="名次">
          <el-input-number v-model="form.rank" :min="0" :max="100" />
        </el-form-item>
        <el-form-item label="积分">
          <el-input-number v-model="form.points" :min="0" :max="100" />
        </el-form-item>
        <el-form-item v-if="isEdit" label="修改原因">
          <el-input v-model="form.modify_reason" type="textarea" placeholder="请输入修改原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 作废弹窗 -->
    <el-dialog v-model="showInvalidateDialog" title="作废成绩" width="400px">
      <el-form :model="invalidateForm" label-width="80px">
        <el-form-item label="作废原因" required>
          <el-input v-model="invalidateForm.reason" type="textarea" placeholder="请输入作废原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showInvalidateDialog = false">取消</el-button>
        <el-button type="primary" :loading="invalidateLoading" @click="confirmInvalidate">确定</el-button>
      </template>
    </el-dialog>

    <ImportDialog v-model="showImportDialog" title="批量导入成绩" @import="handleImport" @success="handleImportSuccess" />
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
const scores = ref([])
const registrationOptions = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const dialogVisible = ref(false)
const showImportDialog = ref(false)
const showInvalidateDialog = ref(false)
const isEdit = ref(false)
const submitLoading = ref(false)
const invalidateLoading = ref(false)
const formRef = ref(null)
const currentId = ref(null)
const currentScore = ref(null)

const searchForm = reactive({ event_id: null, round: '', is_valid: null })
const form = reactive({ registration_id: null, round: 'final', value: '', rank: 0, points: 0, modify_reason: '' })
const invalidateForm = reactive({ reason: '' })

const rules = {
  registration_id: [{ required: true, message: '请选择报名记录', trigger: 'change' }],
  round: [{ required: true, message: '请选择轮次', trigger: 'change' }],
  value: [{ required: true, message: '请输入成绩', trigger: 'blur' }]
}

const loadEvents = async () => { events.value = (await request.get('/events')).data || [] }

const loadData = async () => {
  loading.value = true
  try {
    const params = { page: currentPage.value, page_size: pageSize.value, ...searchForm }
    Object.keys(params).forEach(k => { if (params[k] === '' || params[k] === null) delete params[k] })
    const res = await request.get('/scores', { params })
    scores.value = res.data || res.items || []
    total.value = res.total || scores.value.length
  } finally { loading.value = false }
}

const searchRegistrations = async (query) => {
  if (!query) return
  const res = await request.get('/registrations', { params: { student_name: query, page_size: 20 } })
  registrationOptions.value = res.data || res.items || []
}

const handleSearch = () => { currentPage.value = 1; loadData() }
const handleReset = () => { Object.assign(searchForm, { event_id: null, round: '', is_valid: null }) }
const handlePageChange = () => loadData()

const resetForm = () => { Object.assign(form, { registration_id: null, round: 'final', value: '', rank: 0, points: 0, modify_reason: '' }); currentId.value = null }
const handleAdd = () => { isEdit.value = false; resetForm(); dialogVisible.value = true }

const handleEdit = (row) => {
  isEdit.value = true
  currentId.value = row.id
  form.registration_id = row.registration_id
  form.round = row.round
  form.value = row.value
  form.rank = row.rank || 0
  form.points = row.points || 0
  form.modify_reason = ''
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该成绩记录吗？', '提示', { type: 'warning' })
    await request.delete(`/scores/${row.id}`)
    ElMessage.success('删除成功')
    await loadData()
  } catch (e) { if (e !== 'cancel') ElMessage.error(e.message || '删除失败') }
}

const handleInvalidate = (row) => {
  currentScore.value = row
  invalidateForm.reason = ''
  showInvalidateDialog.value = true
}

const confirmInvalidate = async () => {
  if (!invalidateForm.reason) { ElMessage.warning('请输入作废原因'); return }
  invalidateLoading.value = true
  try {
    await request.put(`/scores/${currentScore.value.id}/invalidate`, { reason: invalidateForm.reason })
    ElMessage.success('作废成功')
    showInvalidateDialog.value = false
    await loadData()
  } catch (e) { ElMessage.error(e.message || '操作失败') }
  finally { invalidateLoading.value = false }
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitLoading.value = true
  try {
    if (isEdit.value) {
      await request.put(`/scores/${currentId.value}`, form)
      ElMessage.success('更新成功')
    } else {
      await request.post('/scores', form)
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
    const result = await request.post('/scores/import', formData)
    resolve(result)
  } catch (e) { reject(e) }
}

const handleImportSuccess = () => loadData()

onMounted(() => { loadEvents(); loadData() })
</script>

<style scoped>
.score-manage { padding: 20px; background: #fff; border-radius: 4px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h3 { margin: 0; }
.header-actions { display: flex; gap: 10px; }
</style>
