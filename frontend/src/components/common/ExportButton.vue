<template>
  <el-dropdown 
    v-if="showDropdown" 
    split-button 
    type="primary" 
    :loading="loading"
    @click="handleExport(defaultFormat)"
    @command="handleExport"
  >
    <el-icon><Download /></el-icon>
    {{ text }}
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item 
          v-for="format in formats" 
          :key="format.value" 
          :command="format.value"
        >
          <el-icon v-if="format.icon"><component :is="format.icon" /></el-icon>
          {{ format.label }}
        </el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
  
  <el-button 
    v-else
    type="primary" 
    :loading="loading"
    @click="handleExport(defaultFormat)"
  >
    <el-icon><Download /></el-icon>
    {{ text }}
  </el-button>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  text: { type: String, default: '导出' },
  formats: { 
    type: Array, 
    default: () => [
      { value: 'xlsx', label: 'Excel (.xlsx)', icon: 'Document' },
      { value: 'csv', label: 'CSV (.csv)', icon: 'Document' },
      { value: 'pdf', label: 'PDF (.pdf)', icon: 'Document' }
    ]
  },
  defaultFormat: { type: String, default: 'xlsx' },
  showDropdown: { type: Boolean, default: true },
  filename: { type: String, default: 'export' }
})

const emit = defineEmits(['export'])

const loading = ref(false)

const handleExport = async (format) => {
  loading.value = true
  try {
    // 触发导出事件，由父组件处理实际导出逻辑
    await new Promise((resolve, reject) => {
      emit('export', { format, filename: props.filename, resolve, reject })
    })
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error(error.message || '导出失败')
  } finally {
    loading.value = false
  }
}

// 下载文件的工具方法
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

defineExpose({
  downloadFile
})
</script>

<style scoped>
</style>
