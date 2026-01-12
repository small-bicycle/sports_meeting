<template>
  <el-form 
    ref="formRef"
    :model="modelValue" 
    :inline="inline"
    class="search-form"
    @submit.prevent="handleSearch"
  >
    <slot></slot>
    
    <el-form-item class="search-buttons">
      <el-button type="primary" :loading="loading" @click="handleSearch">
        <el-icon><Search /></el-icon>
        {{ searchText }}
      </el-button>
      <el-button @click="handleReset">
        <el-icon><Refresh /></el-icon>
        {{ resetText }}
      </el-button>
      <slot name="extra-buttons"></slot>
    </el-form-item>
  </el-form>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  modelValue: { type: Object, default: () => ({}) },
  inline: { type: Boolean, default: true },
  loading: { type: Boolean, default: false },
  searchText: { type: String, default: '搜索' },
  resetText: { type: String, default: '重置' },
  defaultValues: { type: Object, default: () => ({}) }
})

const emit = defineEmits(['update:modelValue', 'search', 'reset'])

const formRef = ref(null)

const handleSearch = () => {
  emit('search', props.modelValue)
}

const handleReset = () => {
  // 重置为默认值
  const resetData = { ...props.defaultValues }
  emit('update:modelValue', resetData)
  emit('reset')
  // 延迟触发搜索，确保数据已更新
  setTimeout(() => {
    emit('search', resetData)
  }, 0)
}

defineExpose({
  formRef
})
</script>

<style scoped>
.search-form {
  background: #fff;
  padding: 20px 20px 0;
  border-radius: 4px;
  margin-bottom: 16px;
}

.search-buttons {
  margin-left: auto;
}

:deep(.el-form-item) {
  margin-bottom: 20px;
}
</style>
