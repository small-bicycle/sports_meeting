<template>
  <div class="announcement-page">
    <div class="announcement-header">
      <h1>{{ announcement.title || '成绩公示' }}</h1>
    </div>
    <div v-if="loading" class="loading">
      <el-icon class="is-loading"><Loading /></el-icon>
      加载中...
    </div>
    <div v-else-if="error" class="error">
      <el-icon><CircleClose /></el-icon>
      {{ error }}
    </div>
    <div v-else class="announcement-content">
      <p>公示内容将在此处展示</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const loading = ref(true)
const error = ref('')
const announcement = reactive({
  title: '',
  content: null
})

onMounted(async () => {
  const code = route.params.code
  try {
    // TODO: 调用公示API获取数据
    loading.value = false
  } catch (e) {
    error.value = '公示已结束或不存在'
    loading.value = false
  }
})
</script>

<style scoped>
.announcement-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 20px;
}

.announcement-header {
  text-align: center;
  padding: 40px 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-radius: 8px;
  margin-bottom: 20px;
}

.loading, .error {
  text-align: center;
  padding: 60px;
  font-size: 18px;
  color: #909399;
}

.error {
  color: #f56c6c;
}

.announcement-content {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
}
</style>
