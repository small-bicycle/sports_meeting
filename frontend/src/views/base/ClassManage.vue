<template>
  <div class="class-manage">
    <div class="page-header">
      <h3>班级管理</h3>
      <div>
        <el-button type="danger" @click="handleClearAll">
          <el-icon><Delete /></el-icon>一键清空
        </el-button>
        <el-button type="success" @click="handleBatchAdd">
          <el-icon><DocumentAdd /></el-icon>一键新增
        </el-button>
      </div>
    </div>

    <SearchForm v-model="searchForm" @search="handleSearch" @reset="handleReset">
      <el-form-item label="年级">
        <el-select v-model="searchForm.grade_id" placeholder="全部年级" clearable style="width: 150px">
          <el-option v-for="g in grades" :key="g.id" :label="g.name" :value="g.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="班级名称">
        <el-input v-model="searchForm.name" placeholder="请输入班级名称" clearable style="width: 150px" />
      </el-form-item>
    </SearchForm>

    <DataTable :data="classes" :loading="loading" :show-pagination="false">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="grade_name" label="所属年级" width="120">
        <template #default="{ row }">{{ row.grade?.name || row.grade_name || '-' }}</template>
      </el-table-column>
      <el-table-column prop="name" label="班级名称" />
      <el-table-column prop="student_count" label="学生人数" width="100" />
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </DataTable>

    <!-- 批量新增弹窗 -->
    <el-dialog v-model="batchDialogVisible" title="一键新增班级" width="600px">
      <el-alert type="info" :closable="false" style="margin-bottom: 15px">
        勾选年级并设置班级数量，系统将为每个选中的年级自动创建对应班级
      </el-alert>
      
      <el-table :data="batchGradeList" border size="small" max-height="400">
        <el-table-column width="50">
          <template #header>
            <el-checkbox v-model="selectAll" @change="handleSelectAll" />
          </template>
          <template #default="{ row }">
            <el-checkbox v-model="row.selected" />
          </template>
        </el-table-column>
        <el-table-column prop="name" label="年级" width="120" />
        <el-table-column label="班级数量" width="150">
          <template #default="{ row }">
            <el-input-number v-model="row.class_count" :min="1" :max="30" size="small" :disabled="!row.selected" />
          </template>
        </el-table-column>
        <el-table-column label="名称前缀">
          <template #default="{ row }">
            <el-input v-model="row.prefix" placeholder="可选，如：高一" size="small" :disabled="!row.selected" />
          </template>
        </el-table-column>
        <el-table-column label="预览" width="180">
          <template #default="{ row }">
            <span v-if="row.selected" style="color: #999; font-size: 12px">
              {{ row.prefix || '' }}1班 ~ {{ row.prefix || '' }}{{ row.class_count }}班
            </span>
          </template>
        </el-table-column>
      </el-table>

      <div style="margin-top: 15px; color: #666">
        已选择 <span style="color: #409EFF; font-weight: bold">{{ selectedCount }}</span> 个年级，
        共创建 <span style="color: #67C23A; font-weight: bold">{{ totalClassCount }}</span> 个班级
      </div>

      <template #footer>
        <el-button @click="batchDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="batchLoading" :disabled="selectedCount === 0" @click="handleBatchSubmit">
          确定创建
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useBaseStore } from '@/stores/base'
import request from '@/api/request'
import DataTable from '@/components/common/DataTable.vue'
import SearchForm from '@/components/common/SearchForm.vue'

const baseStore = useBaseStore()

const loading = ref(false)
const grades = ref([])
const classes = ref([])
const batchDialogVisible = ref(false)
const batchLoading = ref(false)
const selectAll = ref(false)

const searchForm = reactive({ grade_id: null, name: '' })
const batchGradeList = ref([])

const selectedCount = computed(() => batchGradeList.value.filter(g => g.selected).length)
const totalClassCount = computed(() => batchGradeList.value.filter(g => g.selected).reduce((sum, g) => sum + g.class_count, 0))

const formatDate = (date) => date ? new Date(date).toLocaleString('zh-CN') : '-'

const loadGrades = async () => { grades.value = await baseStore.fetchGrades() }

const loadData = async () => {
  loading.value = true
  try {
    classes.value = await baseStore.fetchClasses(searchForm.grade_id)
    if (searchForm.name) {
      classes.value = classes.value.filter(c => c.name.includes(searchForm.name))
    }
  } finally { loading.value = false }
}

const handleSearch = () => loadData()
const handleReset = () => { searchForm.grade_id = null; searchForm.name = '' }

const handleBatchAdd = () => {
  batchGradeList.value = grades.value.map(g => ({
    id: g.id,
    name: g.name,
    selected: false,
    class_count: 10,
    prefix: ''
  }))
  selectAll.value = false
  batchDialogVisible.value = true
}

const handleSelectAll = (val) => {
  batchGradeList.value.forEach(g => { g.selected = val })
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除班级"${row.name}"吗？`, '提示', { type: 'warning' })
    await baseStore.deleteClass(row.id)
    ElMessage.success('删除成功')
    await loadData()
  } catch (e) { if (e !== 'cancel') ElMessage.error(e.message || '删除失败') }
}

const handleClearAll = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有班级吗？这将同时删除所有学生数据！', '危险操作', { 
      type: 'error',
      confirmButtonText: '确定清空',
      confirmButtonClass: 'el-button--danger'
    })
    const res = await request.delete('/classes/clear-all')
    ElMessage.success(res.message || '清空成功')
    await loadData()
  } catch (e) { if (e !== 'cancel') ElMessage.error(e.message || '清空失败') }
}

const handleBatchSubmit = async () => {
  const selectedGrades = batchGradeList.value.filter(g => g.selected)
  if (selectedGrades.length === 0) {
    ElMessage.warning('请至少选择一个年级')
    return
  }
  
  batchLoading.value = true
  let totalCreated = 0
  let errors = []
  
  try {
    for (const grade of selectedGrades) {
      try {
        const res = await request.post('/classes/batch', null, {
          params: { grade_id: grade.id, class_count: grade.class_count, prefix: grade.prefix }
        })
        const match = res.message?.match(/成功创建(\d+)个/)
        if (match) totalCreated += parseInt(match[1])
      } catch (e) {
        errors.push(`${grade.name}: ${e.message || '创建失败'}`)
      }
    }
    
    if (errors.length > 0) {
      ElMessage.warning(`成功创建${totalCreated}个班级，部分失败: ${errors.join('; ')}`)
    } else {
      ElMessage.success(`成功创建${totalCreated}个班级`)
    }
    batchDialogVisible.value = false
    await loadData()
  } catch (e) { ElMessage.error(e.message || '批量创建失败') }
  finally { batchLoading.value = false }
}

onMounted(() => { loadGrades(); loadData() })
</script>

<style scoped>
.class-manage { padding: 20px; background: #fff; border-radius: 4px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h3 { margin: 0; }
</style>
