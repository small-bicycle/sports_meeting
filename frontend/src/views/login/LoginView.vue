<template>
  <div class="login-container">
    <div class="login-box">
      <h2 class="login-title">校园运动会管理系统</h2>
      <p class="login-subtitle">教师端登录</p>
      
      <!-- 账号锁定提示 -->
      <el-alert
        v-if="lockMessage"
        :title="lockMessage"
        type="warning"
        :closable="false"
        show-icon
        class="lock-alert"
      />
      
      <el-form ref="formRef" :model="form" :rules="rules" label-width="0" class="login-form">
        <el-form-item prop="username">
          <el-input 
            v-model="form.username" 
            placeholder="请输入账号" 
            prefix-icon="User"
            :disabled="isLocked"
            size="large"
            clearable
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input 
            v-model="form.password" 
            type="password" 
            placeholder="请输入密码" 
            prefix-icon="Lock" 
            show-password 
            :disabled="isLocked"
            size="large"
            @keyup.enter="handleLogin" 
          />
        </el-form-item>
        <el-form-item style="margin-bottom: 0;">
          <el-button 
            type="primary" 
            :loading="loading" 
            :disabled="isLocked"
            class="login-btn" 
            @click="handleLogin"
          >
            {{ isLocked ? '账号已锁定' : '登 录' }}
          </el-button>
        </el-form-item>
      </el-form>
      
      <!-- 登录失败次数提示 -->
      <div v-if="failCount > 0 && !isLocked" class="fail-tip">
        <el-text type="warning" size="small">
          登录失败 {{ failCount }} 次，连续失败 5 次将锁定账号 30 分钟
        </el-text>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Trophy, Right } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { login } from '@/api/auth'

const router = useRouter()
const userStore = useUserStore()

const formRef = ref(null)
const loading = ref(false)
const failCount = ref(0)
const lockMessage = ref('')
const lockUntil = ref(null)

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: '请输入账号', trigger: 'blur' },
    { min: 2, max: 50, message: '账号长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 50, message: '密码长度在 6 到 50 个字符', trigger: 'blur' }
  ]
}

const isLocked = computed(() => {
  if (!lockUntil.value) return false
  return new Date() < new Date(lockUntil.value)
})

const handleLogin = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const res = await login({
      username: form.username,
      password: form.password
    })
    
    // 保存token和用户信息
    userStore.setToken(res.access_token || res.token)
    userStore.setUserInfo(res.user || res.user_info)
    
    // 重置失败计数
    failCount.value = 0
    lockMessage.value = ''
    
    ElMessage.success('登录成功')
    router.push('/')
  } catch (error) {
    console.error('登录失败:', error)
    
    // 处理错误响应
    if (error.response?.data) {
      const data = error.response.data
      
      // 账号锁定
      if (data.locked_until) {
        lockUntil.value = data.locked_until
        const lockTime = new Date(data.locked_until)
        const minutes = Math.ceil((lockTime - new Date()) / 60000)
        lockMessage.value = `账号已锁定，请 ${minutes} 分钟后重试`
      }
      
      // 更新失败次数
      if (data.fail_count !== undefined) {
        failCount.value = data.fail_count
      } else {
        failCount.value++
      }
      
      // 显示错误消息
      ElMessage.error(data.detail || data.message || '登录失败')
    } else {
      ElMessage.error('登录失败，请检查网络连接')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #87CEEB;
  position: relative;
  overflow: hidden;
}

.login-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: url('@/assets/login-bg.jpg');
  background-size: cover;
  background-position: top center;
  background-repeat: no-repeat;
  opacity: 0.9;
  z-index: 0;
}

.login-box {
  width: 320px;
  padding: 28px 32px;
  background: rgba(255, 255, 255, 0.35);
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(8px);
  position: relative;
  z-index: 1;
  border: 1px solid rgba(255, 255, 255, 0.4);
}

.login-title {
  margin: 0 0 4px;
  text-align: center;
  color: #333;
  font-size: 18px;
  font-weight: 600;
}

.login-subtitle {
  margin: 0 0 20px;
  text-align: center;
  color: #666;
  font-size: 13px;
}

.login-form :deep(.el-input__wrapper) {
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.6);
  box-shadow: none;
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.login-form :deep(.el-input__wrapper:hover) {
  border-color: rgba(64, 158, 255, 0.5);
}

.login-form :deep(.el-input__wrapper.is-focus) {
  border-color: #409EFF;
  background: rgba(255, 255, 255, 0.8);
}

.lock-alert {
  margin-bottom: 16px;
  border-radius: 6px;
}

.login-btn {
  width: 100%;
  height: 40px;
  font-size: 14px;
  font-weight: 500;
  border-radius: 6px;
  background: rgba(64, 158, 255, 0.8);
  border: none;
  letter-spacing: 6px;
  padding-left: 6px;
}

.login-btn:hover:not(:disabled) {
  background: rgba(64, 158, 255, 0.95);
}

.fail-tip {
  text-align: center;
  margin-top: 12px;
}
</style>
