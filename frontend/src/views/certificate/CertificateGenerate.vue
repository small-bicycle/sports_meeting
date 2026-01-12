<template>
  <div class="certificate-generate">
    <div class="page-header">
      <h3>奖状生成</h3>
    </div>

    <el-row :gutter="20">
      <el-col :span="16">
        <el-card>
          <template #header>生成条件</template>
          <el-form :model="form" label-width="100px">
            <el-form-item label="选择项目">
              <el-select v-model="form.event_id" placeholder="请选择项目" filterable style="width: 100%">
                <el-option v-for="e in events" :key="e.id" :label="e.name" :value="e.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="名次范围">
              <el-input-number v-model="form.rank_from" :min="1" :max="20" /> 至
              <el-input-number v-model="form.rank_to" :min="1" :max="20" style="margin-left: 10px" />
            </el-form-item>
            <el-form-item label="奖状模板">
              <el-select v-model="form.template" style="width: 100%">
                <el-option label="标准模板" value="standard" />
                <el-option label="简约模板" value="simple" />
                <el-option label="精美模板" value="fancy" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="previewLoading" @click="handlePreview">预览</el-button>
              <el-button type="success" :loading="generateLoading" @click="handleGenerate">批量生成</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <el-card style="margin-top: 20px" v-if="previewList.length > 0">
          <template #header>预览列表 ({{ previewList.length }} 张)</template>
          <el-table :data="previewList" border>
            <el-table-column prop="rank" label="名次" width="80" />
            <el-table-column prop="student_name" label="学生姓名" width="120" />
            <el-table-column prop="class_name" label="班级" width="150" />
            <el-table-column prop="event_name" label="项目" width="120" />
            <el-table-column prop="value" label="成绩" width="100" />
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button type="primary" link @click="handleSingleDownload(row)">下载</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card>
          <template #header>奖状预览</template>
          <div class="preview-area">
            <div v-if="previewImage" class="preview-image">
              <img :src="previewImage" alt="奖状预览" />
            </div>
            <el-empty v-else description="请先选择条件并预览" />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/api/request'

const events = ref([])
const previewList = ref([])
const previewImage = ref('')
const previewLoading = ref(false)
const generateLoading = ref(false)

const form = reactive({
  event_id: null,
  rank_from: 1,
  rank_to: 8,
  template: 'standard'
})

const loadEvents = async () => {
  const res = await request.get('/events')
  events.value = res.data || res || []
}

const handlePreview = async () => {
  if (!form.event_id) {
    ElMessage.warning('请选择项目')
    return
  }
  previewLoading.value = true
  try {
    const res = await request.get('/certificates/preview', { params: form })
    previewList.value = res.data || res || []
    if (previewList.value.length > 0) {
      previewImage.value = previewList.value[0].preview_url || ''
    }
    ElMessage.success(`找到 ${previewList.value.length} 条记录`)
  } catch (e) {
    ElMessage.error('预览失败')
  } finally {
    previewLoading.value = false
  }
}

const handleGenerate = async () => {
  if (previewList.value.length === 0) {
    ElMessage.warning('请先预览')
    return
  }
  generateLoading.value = true
  try {
    const response = await request.post('/certificates/generate', form, { responseType: 'blob' })
    const url = window.URL.createObjectURL(response)
    const link = document.createElement('a')
    link.href = url
    link.download = `奖状_${new Date().toLocaleDateString()}.zip`
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('生成成功')
  } catch (e) {
    ElMessage.error('生成失败')
  } finally {
    generateLoading.value = false
  }
}

const handleSingleDownload = async (row) => {
  try {
    const response = await request.get(`/certificates/${row.id}/download`, { responseType: 'blob' })
    const url = window.URL.createObjectURL(response)
    const link = document.createElement('a')
    link.href = url
    link.download = `奖状_${row.student_name}.pdf`
    link.click()
    window.URL.revokeObjectURL(url)
  } catch (e) {
    ElMessage.error('下载失败')
  }
}

onMounted(() => { loadEvents() })
</script>

<style scoped>
.certificate-generate { padding: 20px; }
.page-header { margin-bottom: 20px; }
.page-header h3 { margin: 0; }
.preview-area { min-height: 300px; display: flex; align-items: center; justify-content: center; }
.preview-image img { max-width: 100%; border: 1px solid #eee; }
</style>
