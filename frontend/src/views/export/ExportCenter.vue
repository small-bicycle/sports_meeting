<template>
  <div class="export-center">
    <div class="page-header">
      <h3>数据导出中心</h3>
    </div>

    <el-row :gutter="20">
      <el-col :span="8" v-for="item in exportItems" :key="item.key">
        <el-card class="export-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon :size="24"><component :is="item.icon" /></el-icon>
              <span>{{ item.title }}</span>
            </div>
          </template>
          <p class="card-desc">{{ item.description }}</p>
          <div class="card-actions">
            <el-button type="primary" :loading="loading[item.key]" @click="handleExport(item)">
              <el-icon><Download /></el-icon>导出Excel
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 自定义导出弹窗 -->
    <el-dialog v-model="showCustomDialog" title="自定义导出" width="500px">
      <el-form :model="customForm" label-width="100px">
        <el-form-item label="导出类型">
          <el-select v-model="customForm.type" style="width: 100%">
            <el-option label="报名表" value="registrations" />
            <el-option label="成绩表" value="scores" />
            <el-option label="排名表" value="rankings" />
          </el-select>
        </el-form-item>
        <el-form-item label="筛选项目">
          <el-select v-model="customForm.event_id" placeholder="全部项目" clearable style="width: 100%">
            <el-option v-for="e in events" :key="e.id" :label="e.name" :value="e.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="筛选年级">
          <el-select v-model="customForm.grade_id" placeholder="全部年级" clearable style="width: 100%">
            <el-option v-for="g in grades" :key="g.id" :label="g.name" :value="g.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCustomDialog = false">取消</el-button>
        <el-button type="primary" :loading="customLoading" @click="handleCustomExport">导出</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/api/request'

const loading = reactive({})
const showCustomDialog = ref(false)
const customLoading = ref(false)
const events = ref([])
const grades = ref([])

const customForm = reactive({
  type: 'registrations',
  event_id: null,
  grade_id: null
})

const exportItems = [
  { key: 'registrations', title: '报名表导出', description: '导出所有报名信息，包含学生、项目、组别等', icon: 'Document', url: '/exports/registrations' },
  { key: 'scores', title: '成绩表导出', description: '导出所有成绩记录，包含名次、积分等', icon: 'DataLine', url: '/exports/scores' },
  { key: 'rankings', title: '排名表导出', description: '导出各项目排名、班级总分、年级奖牌榜', icon: 'TrendCharts', url: '/exports/rankings' },
  { key: 'students', title: '学生名单导出', description: '导出学生基本信息', icon: 'User', url: '/exports/students' },
  { key: 'participation', title: '参赛表格导出', description: '导出参赛表格，可自定义字段', icon: 'List', url: '/exports/participation' },
  { key: 'custom', title: '自定义导出', description: '根据条件筛选导出数据', icon: 'Setting', custom: true }
]

const loadEvents = async () => { events.value = (await request.get('/events')).data || [] }
const loadGrades = async () => { grades.value = (await request.get('/grades')).data || [] }

const downloadFile = (blob, filename) => {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}

const handleExport = async (item) => {
  if (item.custom) {
    showCustomDialog.value = true
    return
  }
  
  loading[item.key] = true
  try {
    const response = await request.get(item.url, { responseType: 'blob' })
    const filename = `${item.title}_${new Date().toLocaleDateString()}.xlsx`
    downloadFile(response, filename)
    ElMessage.success('导出成功')
  } catch (e) {
    ElMessage.error('导出失败')
  } finally {
    loading[item.key] = false
  }
}

const handleCustomExport = async () => {
  customLoading.value = true
  try {
    const params = { ...customForm }
    Object.keys(params).forEach(k => { if (!params[k]) delete params[k] })
    const response = await request.get(`/exports/${customForm.type}`, { params, responseType: 'blob' })
    const filename = `自定义导出_${new Date().toLocaleDateString()}.xlsx`
    downloadFile(response, filename)
    ElMessage.success('导出成功')
    showCustomDialog.value = false
  } catch (e) {
    ElMessage.error('导出失败')
  } finally {
    customLoading.value = false
  }
}

onMounted(() => { loadEvents(); loadGrades() })
</script>

<style scoped>
.export-center { padding: 20px; }
.page-header { margin-bottom: 20px; }
.page-header h3 { margin: 0; }
.export-card { margin-bottom: 20px; }
.card-header { display: flex; align-items: center; gap: 10px; font-size: 16px; font-weight: bold; }
.card-desc { color: #666; font-size: 14px; margin-bottom: 15px; }
.card-actions { text-align: center; }
</style>
