<template>
  <el-container class="main-layout">
    <el-aside :width="isCollapse ? '64px' : '220px'" class="aside">
      <div class="logo">
        <span v-if="!isCollapse">运动会管理</span>
        <span v-else>运</span>
      </div>
      <el-scrollbar>
        <el-menu 
          :default-active="activeMenu" 
          :collapse="isCollapse" 
          router
          background-color="#304156" 
          text-color="#bfcbd9" 
          active-text-color="#409EFF"
        >
          <!-- 首页 -->
          <el-menu-item index="/dashboard">
            <el-icon><HomeFilled /></el-icon>
            <template #title>首页</template>
          </el-menu-item>
          
          <!-- 基础信息 -->
          <el-sub-menu v-if="hasAnyPermission(['base:grade', 'base:class', 'base:student'])" index="base">
            <template #title>
              <el-icon><Setting /></el-icon>
              <span>基础信息</span>
            </template>
            <el-menu-item v-if="hasPermission('base:grade')" index="/base/grades">年级管理</el-menu-item>
            <el-menu-item v-if="hasPermission('base:class')" index="/base/classes">班级管理</el-menu-item>
            <el-menu-item v-if="hasPermission('base:student')" index="/base/students">学生管理</el-menu-item>
          </el-sub-menu>
          
          <!-- 项目管理 -->
          <el-menu-item v-if="hasPermission('event:manage')" index="/events">
            <el-icon><Trophy /></el-icon>
            <template #title>项目管理</template>
          </el-menu-item>
          
          <!-- 报名管理 -->
          <el-menu-item v-if="hasPermission('registration:manage')" index="/registrations">
            <el-icon><Document /></el-icon>
            <template #title>报名管理</template>
          </el-menu-item>
          
          <!-- 成绩管理 -->
          <el-menu-item v-if="hasPermission('score:manage')" index="/scores">
            <el-icon><DataLine /></el-icon>
            <template #title>成绩管理</template>
          </el-menu-item>
          
          <!-- 统计排名 -->
          <el-sub-menu v-if="hasPermission('statistics:view')" index="statistics">
            <template #title>
              <el-icon><TrendCharts /></el-icon>
              <span>统计排名</span>
            </template>
            <el-menu-item index="/statistics/event">项目排名</el-menu-item>
            <el-menu-item index="/statistics/class">班级总分</el-menu-item>
            <el-menu-item index="/statistics/grade">年级奖牌</el-menu-item>
          </el-sub-menu>
          
          <!-- 数据导出 -->
          <el-menu-item v-if="hasPermission('export:manage')" index="/exports">
            <el-icon><Download /></el-icon>
            <template #title>数据导出</template>
          </el-menu-item>
          
          <!-- 奖状生成 -->
          <el-menu-item v-if="hasPermission('certificate:manage')" index="/certificates">
            <el-icon><Medal /></el-icon>
            <template #title>奖状生成</template>
          </el-menu-item>
          
          <!-- 成绩公示 -->
          <el-menu-item v-if="hasPermission('announcement:manage')" index="/announcements">
            <el-icon><Bell /></el-icon>
            <template #title>成绩公示</template>
          </el-menu-item>
          
          <!-- 系统管理 -->
          <el-sub-menu v-if="userStore.isAdmin" index="system">
            <template #title>
              <el-icon><Tools /></el-icon>
              <span>系统管理</span>
            </template>
            <el-menu-item index="/system/users">用户管理</el-menu-item>
            <el-menu-item index="/system/logs">操作日志</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-scrollbar>
    </el-aside>
    
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="toggleCollapse">
            <Fold v-if="!isCollapse" />
            <Expand v-else />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentRoute.meta?.title && currentRoute.path !== '/dashboard'">
              {{ currentRoute.meta.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-dropdown>
            <span class="user-info">
              <el-avatar :size="32" class="avatar">
                {{ userStore.userInfo?.name?.charAt(0) || 'U' }}
              </el-avatar>
              <span class="username">{{ userStore.userInfo?.name || '用户' }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="showPasswordDialog = true">
                  <el-icon><Key /></el-icon>修改密码
                </el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">
                  <el-icon><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <el-main class="main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
    
    <!-- 修改密码对话框 -->
    <el-dialog v-model="showPasswordDialog" title="修改密码" width="400px">
      <el-form ref="passwordFormRef" :model="passwordForm" :rules="passwordRules" label-width="80px">
        <el-form-item label="原密码" prop="oldPassword">
          <el-input v-model="passwordForm.oldPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input v-model="passwordForm.newPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="passwordForm.confirmPassword" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPasswordDialog = false">取消</el-button>
        <el-button type="primary" :loading="passwordLoading" @click="handleChangePassword">
          确定
        </el-button>
      </template>
    </el-dialog>
  </el-container>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { logout, changePassword } from '@/api/auth'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 响应式折叠
const isCollapse = ref(false)
const windowWidth = ref(window.innerWidth)

// 当前路由
const currentRoute = computed(() => route)
const activeMenu = computed(() => route.path)

// 修改密码
const showPasswordDialog = ref(false)
const passwordLoading = ref(false)
const passwordFormRef = ref(null)
const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== passwordForm.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordRules = {
  oldPassword: [
    { required: true, message: '请输入原密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 50, message: '密码长度在 6 到 50 个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

// 权限检查
const hasPermission = (permission) => {
  return userStore.hasPermission(permission)
}

const hasAnyPermission = (permissions) => {
  return permissions.some(p => hasPermission(p))
}

// 折叠菜单
const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

// 响应式处理
const handleResize = () => {
  windowWidth.value = window.innerWidth
  if (windowWidth.value < 768) {
    isCollapse.value = true
  }
}

// 修改密码
const handleChangePassword = async () => {
  const valid = await passwordFormRef.value.validate().catch(() => false)
  if (!valid) return

  passwordLoading.value = true
  try {
    await changePassword({
      old_password: passwordForm.oldPassword,
      new_password: passwordForm.newPassword
    })
    ElMessage.success('密码修改成功，请重新登录')
    showPasswordDialog.value = false
    handleLogout()
  } catch (error) {
    console.error('修改密码失败:', error)
  } finally {
    passwordLoading.value = false
  }
}

// 退出登录
const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    try {
      await logout()
    } catch (e) {
      // 忽略登出API错误
    }
    
    userStore.logout()
    router.push('/login')
    ElMessage.success('已退出登录')
  } catch {
    // 用户取消
  }
}

onMounted(() => {
  handleResize()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.main-layout {
  height: 100vh;
}

.aside {
  background-color: #304156;
  transition: width 0.3s;
  overflow: hidden;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  background-color: #263445;
  white-space: nowrap;
  overflow: hidden;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.collapse-btn {
  font-size: 20px;
  cursor: pointer;
  color: #666;
}

.collapse-btn:hover {
  color: #409EFF;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  gap: 8px;
}

.avatar {
  background-color: #409EFF;
  color: #fff;
}

.username {
  color: #333;
}

.main {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}

/* 路由过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 响应式 */
@media (max-width: 768px) {
  .username {
    display: none;
  }
  
  .header {
    padding: 0 10px;
  }
  
  .main {
    padding: 10px;
  }
}
</style>
