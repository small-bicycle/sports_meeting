<template>
  <div class="grade-manage">
    <div class="page-header">
      <h3>年级管理</h3>
      <div>
        <el-button type="danger" @click="handleClearAll">
          <el-icon><Delete /></el-icon>一键清空
        </el-button>
        <el-button type="success" @click="handleBatchAdd">
          <el-icon><DocumentAdd /></el-icon>一键新增
        </el-button>
      </div>
    </div>

    <DataTable :data="grades" :loading="loading" :show-pagination="false">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="年级名称" />
      <el-table-column prop="sort_order" label="排序" width="100" />
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="{ row }">
          <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </DataTable>

    <!-- 批量新增弹窗 -->
    <el-dialog v-model="batchDialogVisible" title="一键新增年级" width="500px">
      <el-alert type="info" :closable="false" style="margin-bottom: 15px">
        选择要创建的年级，系统将自动创建对应年级
      </el-alert>
      <el-checkbox-group v-model="selectedGrades">
        <el-checkbox v-for="g in gradeTemplates" :key="g" :label="g">{{ g }}</el-checkbox>
      </el-checkbox-group>
      <div style="margin-top: 15px">
        <el-button link type="primary" @click="selectAllGrades">全选</el-button>
        <el-button link @click="selectedGrades = []">清空</el-button>
      </div>
      <template #footer>
        <el-button @click="batchDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="batchLoading" @click="handleBatchSubmit">确定创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useBaseStore } from '@/stores/base'
import request from '@/api/request'
import DataTable from '@/components/common/DataTable.vue'

const baseStore = useBaseStore()

const loading = ref(false)
const grades = ref([])
const batchDialogVisible = ref(false)
const batchLoading = ref(false)

const gradeTemplates = ['一年级', '二年级', '三年级', '四年级', '五年级', '六年级', '初一', '初二', '初三', '高一', '高二', '高三']
const selectedGrades = ref([])

const formatDate = (date) => date ? new Date(date).toLocaleString('zh-CN') : '-'

const loadData = async () => {
  loading.value = true
  try { grades.value = await baseStore.fetchGrades() }
  finally { loading.value = false }
}

const handleBatchAdd = () => { selectedGrades.value = []; batchDialogVisible.value = true }
const selectAllGrades = () => { selectedGrades.value = [...gradeTemplates] }

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除年级"${row.name}"吗？`, '提示', { type: 'warning' })
    await baseStore.deleteGrade(row.id)
    ElMessage.success('删除成功')
    await loadData()
  } catch (e) { if (e !== 'cancel') ElMessage.error(e.message || '删除失败') }
}

const handleClearAll = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有年级吗？这将同时删除所有班级和学生数据！', '危险操作', { 
      type: 'error',
      confirmButtonText: '确定清空',
      confirmButtonClass: 'el-button--danger'
    })
    const res = await request.delete('/grades/clear-all')
    ElMessage.success(res.message || '清空成功')
    await loadData()
  } catch (e) { if (e !== 'cancel') ElMessage.error(e.message || '清空失败') }
}

const handleBatchSubmit = async () => {
  if (selectedGrades.value.length === 0) {
    ElMessage.warning('请至少选择一个年级')
    return
  }
  batchLoading.value = true
  try {
    const res = await request.post('/grades/batch', selectedGrades.value)
    ElMessage.success(res.message || '批量创建成功')
    batchDialogVisible.value = false
    await loadData()
  } catch (e) { ElMessage.error(e.message || '批量创建失败') }
  finally { batchLoading.value = false }
}

onMounted(() => { loadData() })
</script>

<style scoped>
.grade-manage { padding: 20px; background: #fff; border-radius: 4px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h3 { margin: 0; }
.el-checkbox { margin: 8px 15px 8px 0; }
</style>
