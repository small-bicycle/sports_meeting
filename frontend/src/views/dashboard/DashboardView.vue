<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>学生总数</template>
          <div class="stat-value">{{ stats.studentCount }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>报名人次</template>
          <div class="stat-value">{{ stats.registrationCount }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>比赛项目</template>
          <div class="stat-value">{{ stats.eventCount }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>已录成绩</template>
          <div class="stat-value">{{ stats.scoreCount }}</div>
        </el-card>
      </el-col>
    </el-row>
    <el-card class="welcome-card" shadow="never">
      <h2>欢迎使用校园运动会教师端管理系统</h2>
      <p>本系统为学校教师专属的校运会综合管理平台，提供运动会全流程管理功能。</p>
    </el-card>
  </div>
</template>

<script setup>
import { reactive } from 'vue'

const stats = reactive({
  studentCount: 0,
  registrationCount: 0,
  eventCount: 0,
  scoreCount: 0
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409EFF;
  text-align: center;
}

.welcome-card {
  margin-top: 20px;
}

.welcome-card h2 {
  margin-bottom: 10px;
}
</style>
