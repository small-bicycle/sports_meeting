import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/LoginView.vue'),
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/views/layout/MainLayout.vue'),
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/DashboardView.vue'),
        meta: { title: '首页' }
      },
      // 基础信息管理
      {
        path: 'base/grades',
        name: 'GradeManage',
        component: () => import('@/views/base/GradeManage.vue'),
        meta: { title: '年级管理', permission: 'base:grade' }
      },
      {
        path: 'base/classes',
        name: 'ClassManage',
        component: () => import('@/views/base/ClassManage.vue'),
        meta: { title: '班级管理', permission: 'base:class' }
      },
      {
        path: 'base/students',
        name: 'StudentManage',
        component: () => import('@/views/base/StudentManage.vue'),
        meta: { title: '学生管理', permission: 'base:student' }
      },
      // 运动项目管理
      {
        path: 'events',
        name: 'EventManage',
        component: () => import('@/views/event/EventManage.vue'),
        meta: { title: '项目管理', permission: 'event:manage' }
      },
      // 报名管理
      {
        path: 'registrations',
        name: 'RegistrationManage',
        component: () => import('@/views/registration/RegistrationManage.vue'),
        meta: { title: '报名管理', permission: 'registration:manage' }
      },
      // 成绩管理
      {
        path: 'scores',
        name: 'ScoreManage',
        component: () => import('@/views/score/ScoreManage.vue'),
        meta: { title: '成绩管理', permission: 'score:manage' }
      },
      // 统计排名
      {
        path: 'statistics/event',
        name: 'EventRanking',
        component: () => import('@/views/statistics/EventRanking.vue'),
        meta: { title: '项目排名', permission: 'statistics:view' }
      },
      {
        path: 'statistics/class',
        name: 'ClassTotal',
        component: () => import('@/views/statistics/ClassTotal.vue'),
        meta: { title: '班级总分', permission: 'statistics:view' }
      },
      {
        path: 'statistics/grade',
        name: 'GradeMedals',
        component: () => import('@/views/statistics/GradeMedals.vue'),
        meta: { title: '年级奖牌', permission: 'statistics:view' }
      },
      // 数据导出
      {
        path: 'exports',
        name: 'ExportCenter',
        component: () => import('@/views/export/ExportCenter.vue'),
        meta: { title: '数据导出', permission: 'export:manage' }
      },
      // 奖状生成
      {
        path: 'certificates',
        name: 'CertificateGenerate',
        component: () => import('@/views/certificate/CertificateGenerate.vue'),
        meta: { title: '奖状生成', permission: 'certificate:manage' }
      },
      // 成绩公示
      {
        path: 'announcements',
        name: 'AnnouncementManage',
        component: () => import('@/views/announcement/AnnouncementManage.vue'),
        meta: { title: '成绩公示', permission: 'announcement:manage' }
      },
      // 系统管理
      {
        path: 'system/users',
        name: 'UserManage',
        component: () => import('@/views/system/UserManage.vue'),
        meta: { title: '用户管理', permission: 'system:user', requiresAdmin: true }
      },
      {
        path: 'system/logs',
        name: 'OperationLog',
        component: () => import('@/views/system/OperationLog.vue'),
        meta: { title: '操作日志', permission: 'system:log', requiresAdmin: true }
      }
    ]
  },
  // 公示页面（无需登录）
  {
    path: '/public/announcement/:code',
    name: 'PublicAnnouncement',
    component: () => import('@/views/public/AnnouncementView.vue'),
    meta: { title: '成绩公示', requiresAuth: false }
  },
  // 404页面
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/error/NotFound.vue'),
    meta: { title: '页面不存在', requiresAuth: false }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 校园运动会管理系统` : '校园运动会管理系统'
  
  const token = localStorage.getItem('token')
  const userInfo = JSON.parse(localStorage.getItem('userInfo') || 'null')
  
  // 不需要认证的页面直接放行
  if (to.meta.requiresAuth === false) {
    next()
    return
  }
  
  // 需要认证但没有token，跳转登录
  if (!token) {
    next('/login')
    return
  }
  
  // 需要管理员权限
  if (to.meta.requiresAdmin && !userInfo?.is_admin) {
    next('/dashboard')
    return
  }
  
  // 检查权限
  if (to.meta.permission) {
    const permissions = userInfo?.permissions || []
    const hasPermission = userInfo?.is_admin || permissions.includes(to.meta.permission)
    if (!hasPermission) {
      next('/dashboard')
      return
    }
  }
  
  next()
})

export default router
