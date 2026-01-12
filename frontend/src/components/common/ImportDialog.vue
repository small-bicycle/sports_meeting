<template>
  <el-dialog 
    v-model="visible" 
    :title="title" 
    width="500px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div class="import-content">
      <!-- 上传区域 -->
      <el-upload
        ref="uploadRef"
        class="upload-area"
        drag
        :action="uploadAction"
        :headers="uploadHeaders"
        :accept="accept"
        :limit="1"
        :auto-upload="false"
        :on-change="handleFileChange"
        :on-exceed="handleExceed"
        :before-upload="beforeUpload"
      >
        <el-icon class="upload-icon"><UploadFilled /></el-icon>
        <div class="upload-text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="upload-tip">
            {{ tip || `支持 ${accept} 格式，文件大小不超过 ${maxSizeMB}MB` }}
          </div>
        </template>
      </el-upload>
      
      <!-- 模板下载 -->
      <div v-if="templateUrl" class="template-download">
        <el-link type="primary" @click="downloadTemplate">
          <el-icon><Download /></el-icon>
          下载导入模板
        </el-link>
      </div>
      
      <!-- 导入结果 -->
      <div v-if="importResult" class="import-result">
        <el-alert
          :title="importResult.success ? '导入成功' : '导入完成（有错误）'"
          :type="importResult.success ? 'success' : 'warning'"
          :closable="false"
          show-icon
        >
          <template #default>
            <div class="result-detail">
              <p>成功导入：{{ importResult.successCount }} 条</p>
              <p v-if="importResult.failCount > 0">导入失败：{{ importResult.failCount }} 条</p>
            </div>
            <div v-if="importResult.errors?.length" class="error-list">
              <p class="error-title">错误详情：</p>
              <ul>
                <li v-for="(error, index) in importResult.errors.slice(0, 5)" :key="index">
                  第 {{ error.row }} 行：{{ error.message }}
                </li>
                <li v-if="importResult.errors.length > 5">
                  ... 还有 {{ importResult.errors.length - 5 }} 条错误
                </li>
              </ul>
            </div>
          </template>
        </el-alert>
      </div>
    </div>
    
    <template #footer>
      <el-button @click="handleClose">{{ importResult ? '关闭' : '取消' }}</el-button>
      <el-button 
        v-if="!importResult"
        type="primary" 
        :loading="loading" 
        :disabled="!selectedFile"
        @click="handleImport"
      >
        开始导入
      </el-button>
      <el-button 
        v-else
        type="primary" 
        @click="handleReset"
      >
        继续导入
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: '批量导入' },
  accept: { type: String, default: '.xlsx,.xls' },
  maxSizeMB: { type: Number, default: 10 },
  tip: { type: String, default: '' },
  templateUrl: { type: String, default: '' },
  uploadAction: { type: String, default: '' },
  uploadHeaders: { type: Object, default: () => ({}) }
})

const emit = defineEmits(['update:modelValue', 'import', 'success'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const uploadRef = ref(null)
const selectedFile = ref(null)
const loading = ref(false)
const importResult = ref(null)

const handleFileChange = (file) => {
  selectedFile.value = file.raw
}

const handleExceed = () => {
  ElMessage.warning('只能上传一个文件')
}

const beforeUpload = (file) => {
  const isValidType = props.accept.split(',').some(type => {
    return file.name.toLowerCase().endsWith(type.trim())
  })
  if (!isValidType) {
    ElMessage.error(`只能上传 ${props.accept} 格式的文件`)
    return false
  }
  
  const isValidSize = file.size / 1024 / 1024 < props.maxSizeMB
  if (!isValidSize) {
    ElMessage.error(`文件大小不能超过 ${props.maxSizeMB}MB`)
    return false
  }
  
  return true
}

const handleImport = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }
  
  loading.value = true
  try {
    // 触发导入事件，由父组件处理实际导入逻辑
    const result = await new Promise((resolve, reject) => {
      emit('import', selectedFile.value, { resolve, reject })
    })
    
    importResult.value = result
    if (result.success) {
      emit('success', result)
    }
  } catch (error) {
    console.error('导入失败:', error)
    importResult.value = {
      success: false,
      successCount: 0,
      failCount: 0,
      errors: [{ row: 0, message: error.message || '导入失败' }]
    }
  } finally {
    loading.value = false
  }
}

const handleReset = () => {
  selectedFile.value = null
  importResult.value = null
  uploadRef.value?.clearFiles()
}

const downloadTemplate = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await fetch(props.templateUrl, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (!response.ok) throw new Error('下载失败')
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'import_template.xlsx'
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  } catch (e) {
    ElMessage.error('模板下载失败')
  }
}

const handleClose = () => {
  handleReset()
  visible.value = false
}

watch(visible, (val) => {
  if (!val) {
    handleReset()
  }
})
</script>

<style scoped>
.import-content {
  padding: 10px 0;
}

.upload-area {
  width: 100%;
}

.upload-area :deep(.el-upload-dragger) {
  width: 100%;
}

.upload-icon {
  font-size: 48px;
  color: #c0c4cc;
  margin-bottom: 10px;
}

.upload-text {
  color: #606266;
}

.upload-text em {
  color: #409EFF;
  font-style: normal;
}

.upload-tip {
  color: #909399;
  font-size: 12px;
  margin-top: 10px;
}

.template-download {
  margin-top: 16px;
  text-align: center;
}

.import-result {
  margin-top: 20px;
}

.result-detail p {
  margin: 5px 0;
}

.error-list {
  margin-top: 10px;
}

.error-title {
  font-weight: bold;
  margin-bottom: 5px;
}

.error-list ul {
  margin: 0;
  padding-left: 20px;
}

.error-list li {
  color: #f56c6c;
  font-size: 12px;
  line-height: 1.8;
}
</style>
