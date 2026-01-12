<template>
  <div class="student-manage">
    <div class="page-header">
      <h3>学生管理</h3>
      <div class="header-actions">
        <el-button @click="showClassImportDialog = true" type="success">
          <el-icon><Upload /></el-icon>按班级批量导入
        </el-button>
        <el-button type="danger" @click="handleClearAll">
          <el-icon><Delete /></el-icon>一键清空
        </el-button>
      </div>
    </div>

    <SearchForm v-model="searchForm" :loading="loading" @search="handleSearch" @reset="handleReset">
      <el-form-item label="年级">
        <el-select v-model="searchForm.grade_id" placeholder="全部年级" clearable style="width: 120px" @change="onGradeChange">
          <el-option v-for="g in grades" :key="g.id" :label="g.name" :value="g.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="班级">
        <el-select v-model="searchForm.class_id" placeholder="全部班级" clearable style="width: 120px">
          <el-option v-for="c in filteredClasses" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="学号">
        <el-input v-model="searchForm.student_no" placeholder="学号" clearable style="width: 120px" />
      </el-form-item>
      <el-form-item label="姓名">
        <el-input v-model="searchForm.name" placeholder="姓名" clearable style="width: 120px" />
      </el-form-item>
      <el-form-item label="性别">
        <el-select v-model="searchForm.gender" placeholder="全部" clearable style="width: 80px">
          <el-option label="男" value="男" />
          <el-option label="女" value="女" />
        </el-select>
      </el-form-item>
    </SearchForm>

    <DataTable
      :data="students"
      :loading="loading"
      :total="total"
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      @page-change="handlePageChange"
    >
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="student_no" label="学号" width="120" />
      <el-table-column prop="name" label="姓名" width="100" />
      <el-table-column label="性别" width="70">
        <template #default="{ row }">
          {{ row.gender === 'M' ? '男' : row.gender === 'F' ? '女' : row.gender }}
        </template>
      </el-table-column>
      <el-table-column label="班级" width="180">
        <template #default="{ row }">
          {{ row.grade_name }} {{ row.class_name }}
        </template>
      </el-table-column>
      <el-table-column label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </DataTable>

    <!-- 按班级导入弹窗 -->
    <el-dialog v-model="showClassImportDialog" title="按班级批量导入学生" width="500px">
      <el-form label-width="100px">
        <el-form-item label="选择年级" required>
          <el-select v-model="classImportForm.grade_id" placeholder="请选择年级" style="width: 100%" @change="onClassImportGradeChange">
            <el-option v-for="g in grades" :key="g.id" :label="g.name" :value="g.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="选择班级" required>
          <el-select v-model="classImportForm.class_id" placeholder="请选择班级" style="width: 100%">
            <el-option v-for="c in classImportClasses" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="下载模板">
          <el-button type="primary" @click="downloadClassTemplate" :disabled="!classImportForm.class_id">
            <el-icon><Download /></el-icon>下载该班级导入模板
          </el-button>
        </el-form-item>
        <el-form-item label="上传文件" required>
          <el-upload
            ref="classUploadRef"
            :auto-upload="false"
            :limit="1"
            accept=".xlsx,.xls"
            :on-change="onClassFileChange"
            :on-remove="onClassFileRemove"
          >
            <el-button type="primary">选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">只支持 .xlsx, .xls 格式</div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showClassImportDialog = false">取消</el-button>
        <el-button type="primary" :loading="classImportLoading" @click="handleClassImport" :disabled="!classImportForm.class_id || !classImportFile">
          开始导入
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useBaseStore } from '@/stores/base'
import DataTable from '@/components/common/DataTable.vue'
import SearchForm from '@/components/common/SearchForm.vue'
import { Download, Delete } from '@element-plus/icons-vue'
import request from '@/api/request'

const baseStore = useBaseStore()

const loading = ref(false)
const grades = ref([])
const classes = ref([])
const students = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const showClassImportDialog = ref(false)
const classUploadRef = ref(null)
const classImportFile = ref(null)
const classImportLoading = ref(false)

const searchForm = reactive({
  grade_id: null,
  class_id: null,
  student_no: '',
  name: '',
  gender: ''
})

const classImportForm = reactive({
  grade_id: null,
  class_id: null
})

const filteredClasses = computed(() => {
  if (!searchForm.grade_id) return classes.value
  return classes.value.filter(c => c.grade_id === searchForm.grade_id)
})

const classImportClasses = computed(() => {
  if (!classImportForm.grade_id) return []
  return classes.value.filter(c => c.grade_id === classImportForm.grade_id)
})

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

const loadGrades = async () => {
  grades.value = await baseStore.fetchGrades()
}

const loadClasses = async () => {
  classes.value = await baseStore.fetchClasses()
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      ...searchForm
    }
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null) {
        delete params[key]
      }
    })
    const result = await baseStore.fetchStudents(params)
    students.value = result.items
    total.value = result.total
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadData()
}

const handleReset = () => {
  Object.assign(searchForm, {
    grade_id: null,
    class_id: null,
    student_no: '',
    name: '',
    gender: ''
  })
}

const handlePageChange = ({ page, size }) => {
  currentPage.value = page
  pageSize.value = size
  loadData()
}

const onGradeChange = () => {
  searchForm.class_id = null
}

const onClassImportGradeChange = () => {
  classImportForm.class_id = null
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除学生"${row.name}"吗？`, '提示', { type: 'warning' })
    await baseStore.deleteStudent(row.id)
    ElMessage.success('删除成功')
    await loadData()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(e.message || '删除失败')
    }
  }
}

// 一键清空所有学生
const handleClearAll = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有学生吗？此操作不可恢复！', '警告', { 
      type: 'warning',
      confirmButtonText: '确定清空',
      cancelButtonText: '取消'
    })
    const res = await request.delete('/students/clear-all')
    ElMessage.success(res.message || '清空成功')
    await loadData()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(e.message || '清空失败')
    }
  }
}

// 按班级导入相关方法
const downloadClassTemplate = async () => {
  if (!classImportForm.class_id) {
    ElMessage.warning('请先选择班级')
    return
  }
  
  try {
    const token = localStorage.getItem('token')
    const response = await fetch(`/api/students/template?class_id=${classImportForm.class_id}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || '下载失败')
    }
    
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    
    const contentDisposition = response.headers.get('Content-Disposition')
    let filename = 'student_import_template.xlsx'
    if (contentDisposition) {
      const utf8Match = contentDisposition.match(/filename\*=UTF-8''(.+)/)
      if (utf8Match) {
        filename = decodeURIComponent(utf8Match[1])
      }
    }
    
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
    ElMessage.success('模板下载成功')
  } catch (e) {
    ElMessage.error(e.message || '下载模板失败')
  }
}

const onClassFileChange = (file) => {
  classImportFile.value = file.raw
}

const onClassFileRemove = () => {
  classImportFile.value = null
}

const handleClassImport = async () => {
  if (!classImportForm.class_id) {
    ElMessage.warning('请选择班级')
    return
  }
  if (!classImportFile.value) {
    ElMessage.warning('请选择文件')
    return
  }
  
  classImportLoading.value = true
  try {
    const result = await baseStore.importStudentsByClass(classImportFile.value, classImportForm.class_id)
    
    if (result.success > 0) {
      ElMessage.success(`成功导入 ${result.success} 名学生`)
    }
    if (result.failed > 0) {
      ElMessage.warning(`${result.failed} 条记录导入失败`)
    }
    
    showClassImportDialog.value = false
    classImportForm.grade_id = null
    classImportForm.class_id = null
    classImportFile.value = null
    if (classUploadRef.value) {
      classUploadRef.value.clearFiles()
    }
    await loadData()
  } catch (e) {
    ElMessage.error(e.message || '导入失败')
  } finally {
    classImportLoading.value = false
  }
}

onMounted(() => {
  loadGrades()
  loadClasses()
  loadData()
})
</script>

<style scoped>
.student-manage {
  padding: 20px;
  background: #fff;
  border-radius: 4px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h3 {
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 10px;
}
</style>
