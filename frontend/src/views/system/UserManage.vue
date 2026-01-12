<template>
  <div class="user-manage">
    <div class="page-header">
      <h3>用户管理</h3>
      <el-button type="primary" @click="handleAdd"><el-icon><Plus /></el-icon>新增用户</el-button>
    </div>

    <DataTable :data="users" :loading="loading" :show-pagination="false">
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="username" label="账号" width="120" />
      <el-table-column prop="name" label="姓名" width="120" />
      <el-table-column prop="is_admin" label="管理员" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_admin ? 'danger' : 'info'" size="small">{{ row.is_admin ? '是' : '否' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="is_active" label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="160">
        <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
          <el-button type="warning" link @click="handleResetPwd(row)">重置密码</el-button>
          <el-button :type="row.is_active ? 'danger' : 'success'" link @click="handleToggle(row)">
            {{ row.is_active ? '禁用' : '启用' }}
          </el-button>
        </template>
      </el-table-column>
    </DataTable>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑用户' : '新增用户'" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="账号" prop="username">
          <el-input v-model="form.username" :disabled="isEdit" placeholder="请输入账号" />
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item v-if="!isEdit" label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item label="管理员">
          <el-switch v-model="form.is_admin" />
        </el-form-item>
        <el-form-item label="权限">
          <el-checkbox-group v-model="form.permissions">
            <el-checkbox v-for="p in permissionOptions" :key="p.value" :label="p.value">{{ p.label }}</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
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
const users = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitLoading = ref(false)
const formRef = ref(null)
const currentId = ref(null)

const form = reactive({ username: '', name: '', password: '', is_admin: false, permissions: [] })
const rules = {
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const permissionOptions = [
  { value: 'base:grade', label: '年级管理' },
  { value: 'base:class', label: '班级管理' },
  { value: 'base:student', label: '学生管理' },
  { value: 'event:manage', label: '项目管理' },
  { value: 'registration:manage', label: '报名管理' },
  { value: 'score:manage', label: '成绩管理' },
  { value: 'statistics:view', label: '统计查看' },
  { value: 'export:manage', label: '数据导出' },
  { value: 'certificate:manage', label: '奖状生成' },
  { value: 'announcement:manage', label: '公示管理' }
]

const formatDate = (date) => date ? new Date(date).toLocaleString('zh-CN') : '-'

const loadData = async () => {
  loading.value = true
  try {
    const res = await request.get('/users')
    users.value = res.data || res || []
  } finally { loading.value = false }
}

const resetForm = () => { Object.assign(form, { username: '', name: '', password: '', is_admin: false, permissions: [] }); currentId.value = null }
const handleAdd = () => { isEdit.value = false; resetForm(); dialogVisible.value = true }

const handleEdit = (row) => {
  isEdit.value = true
  currentId.value = row.id
  Object.assign(form, { username: row.username, name: row.name, password: '', is_admin: row.is_admin, permissions: row.permissions || [] })
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitLoading.value = true
  try {
    if (isEdit.value) {
      await request.put(`/users/${currentId.value}`, form)
      ElMessage.success('更新成功')
    } else {
      await request.post('/users', form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    await loadData()
  } catch (e) { ElMessage.error(e.message || '操作失败') }
  finally { submitLoading.value = false }
}

const handleResetPwd = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要重置用户"${row.name}"的密码吗？`, '提示', { type: 'warning' })
    await request.put(`/users/${row.id}/reset-password`)
    ElMessage.success('密码已重置为初始密码')
  } catch (e) { if (e !== 'cancel') ElMessage.error(e.message || '操作失败') }
}

const handleToggle = async (row) => {
  try {
    await request.put(`/users/${row.id}`, { is_active: !row.is_active })
    ElMessage.success(row.is_active ? '已禁用' : '已启用')
    await loadData()
  } catch (e) { ElMessage.error(e.message || '操作失败') }
}

onMounted(() => { loadData() })
</script>

<style scoped>
.user-manage { padding: 20px; background: #fff; border-radius: 4px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h3 { margin: 0; }
</style>
