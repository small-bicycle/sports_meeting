<template>
  <div class="announcement-manage">
    <div class="page-header">
      <h3>成绩公示管理</h3>
      <el-button type="primary" @click="handleAdd"><el-icon><Plus /></el-icon>创建公示</el-button>
    </div>

    <DataTable :data="announcements" :loading="loading" :show-pagination="false">
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="title" label="公示标题" />
      <el-table-column prop="content_type" label="内容类型" width="120">
        <template #default="{ row }">
          <el-tag size="small">{{ getContentTypeName(row.content_type) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="share_code" label="分享码" width="120" />
      <el-table-column prop="is_active" label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
            {{ row.is_active ? '公示中' : '已关闭' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="160">
        <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="handleCopyLink(row)">复制链接</el-button>
          <el-button v-if="row.is_active" type="warning" link @click="handleClose(row)">关闭</el-button>
          <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </DataTable>

    <!-- 创建公示弹窗 -->
    <el-dialog v-model="dialogVisible" title="创建公示" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="公示标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入公示标题" />
        </el-form-item>
        <el-form-item label="内容类型" prop="content_type">
          <el-select v-model="form.content_type" style="width: 100%">
            <el-option label="项目排名" value="event_ranking" />
            <el-option label="班级总分" value="class_total" />
            <el-option label="年级奖牌" value="grade_medals" />
            <el-option label="综合公示" value="all" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="form.content_type === 'event_ranking'" label="选择项目">
          <el-select v-model="form.event_ids" multiple placeholder="请选择项目" style="width: 100%">
            <el-option v-for="e in events" :key="e.id" :label="e.name" :value="e.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/api/request'
import DataTable from '@/components/common/DataTable.vue'

const loading = ref(false)
const announcements = ref([])
const events = ref([])
const dialogVisible = ref(false)
const submitLoading = ref(false)
const formRef = ref(null)

const form = reactive({
  title: '',
  content_type: 'all',
  event_ids: []
})

const rules = {
  title: [{ required: true, message: '请输入公示标题', trigger: 'blur' }],
  content_type: [{ required: true, message: '请选择内容类型', trigger: 'change' }]
}

const getContentTypeName = (type) => ({
  event_ranking: '项目排名',
  class_total: '班级总分',
  grade_medals: '年级奖牌',
  all: '综合公示'
}[type] || type)

const formatDate = (date) => date ? new Date(date).toLocaleString('zh-CN') : '-'

const loadData = async () => {
  loading.value = true
  try {
    const res = await request.get('/announcements')
    announcements.value = res.data || res || []
  } finally { loading.value = false }
}

const loadEvents = async () => {
  const res = await request.get('/events')
  events.value = res.data || res || []
}

const handleAdd = () => {
  form.title = ''
  form.content_type = 'all'
  form.event_ids = []
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitLoading.value = true
  try {
    await request.post('/announcements', form)
    ElMessage.success('创建成功')
    dialogVisible.value = false
    await loadData()
  } catch (e) {
    ElMessage.error(e.message || '创建失败')
  } finally {
    submitLoading.value = false
  }
}

const handleCopyLink = (row) => {
  const link = `${window.location.origin}/public/announcement/${row.share_code}`
  navigator.clipboard.writeText(link)
  ElMessage.success('链接已复制到剪贴板')
}

const handleClose = async (row) => {
  try {
    await ElMessageBox.confirm('确定要关闭该公示吗？关闭后将无法通过链接访问。', '提示', { type: 'warning' })
    await request.put(`/announcements/${row.id}/close`)
    ElMessage.success('已关闭')
    await loadData()
  } catch (e) { if (e !== 'cancel') ElMessage.error(e.message || '操作失败') }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该公示吗？', '提示', { type: 'warning' })
    await request.delete(`/announcements/${row.id}`)
    ElMessage.success('删除成功')
    await loadData()
  } catch (e) { if (e !== 'cancel') ElMessage.error(e.message || '删除失败') }
}

onMounted(() => { loadData(); loadEvents() })
</script>

<style scoped>
.announcement-manage { padding: 20px; background: #fff; border-radius: 4px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h3 { margin: 0; }
</style>
