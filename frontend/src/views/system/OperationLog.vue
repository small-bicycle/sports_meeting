<template>
  <div class="operation-log">
    <div class="page-header">
      <h3>操作日志</h3>
    </div>

    <SearchForm v-model="searchForm" :loading="loading" @search="handleSearch" @reset="handleReset">
      <el-form-item label="操作人">
        <el-input v-model="searchForm.user_name" placeholder="操作人姓名" clearable style="width: 120px" />
      </el-form-item>
      <el-form-item label="操作类型">
        <el-select v-model="searchForm.action" placeholder="全部" clearable style="width: 120px">
          <el-option label="创建" value="create" />
          <el-option label="更新" value="update" />
          <el-option label="删除" value="delete" />
          <el-option label="登录" value="login" />
          <el-option label="登出" value="logout" />
        </el-select>
      </el-form-item>
      <el-form-item label="目标类型">
        <el-select v-model="searchForm.target_type" placeholder="全部" clearable style="width: 120px">
          <el-option label="用户" value="user" />
          <el-option label="学生" value="student" />
          <el-option label="项目" value="event" />
          <el-option label="报名" value="registration" />
          <el-option label="成绩" value="score" />
        </el-select>
      </el-form-item>
      <el-form-item label="时间范围">
        <el-date-picker v-model="searchForm.date_range" type="daterange" range-separator="至" 
          start-placeholder="开始日期" end-placeholder="结束日期" style="width: 240px" />
      </el-form-item>
    </SearchForm>

    <DataTable :data="logs" :loading="loading" :total="total" v-model:current-page="currentPage" 
      v-model:page-size="pageSize" @page-change="handlePageChange">
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="user_name" label="操作人" width="100">
        <template #default="{ row }">{{ row.user?.name || '-' }}</template>
      </el-table-column>
      <el-table-column prop="action" label="操作类型" width="80">
        <template #default="{ row }">
          <el-tag :type="getActionType(row.action)" size="small">{{ getActionName(row.action) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="target_type" label="目标类型" width="80" />
      <el-table-column prop="target_id" label="目标ID" width="80" />
      <el-table-column prop="detail" label="详情" show-overflow-tooltip />
      <el-table-column prop="ip_address" label="IP地址" width="130" />
      <el-table-column prop="created_at" label="操作时间" width="160">
        <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
      </el-table-column>
    </DataTable>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import request from '@/api/request'
import DataTable from '@/components/common/DataTable.vue'
import SearchForm from '@/components/common/SearchForm.vue'

const loading = ref(false)
const logs = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

const searchForm = reactive({ user_name: '', action: '', target_type: '', date_range: null })

const getActionName = (action) => ({ create: '创建', update: '更新', delete: '删除', login: '登录', logout: '登出' }[action] || action)
const getActionType = (action) => ({ create: 'success', update: 'warning', delete: 'danger', login: 'primary', logout: 'info' }[action] || 'info')
const formatDate = (date) => date ? new Date(date).toLocaleString('zh-CN') : '-'

const loadData = async () => {
  loading.value = true
  try {
    const params = { page: currentPage.value, page_size: pageSize.value, ...searchForm }
    if (params.date_range) {
      params.start_date = params.date_range[0]
      params.end_date = params.date_range[1]
      delete params.date_range
    }
    Object.keys(params).forEach(k => { if (!params[k]) delete params[k] })
    const res = await request.get('/logs', { params })
    logs.value = res.data || res.items || []
    total.value = res.total || logs.value.length
  } finally { loading.value = false }
}

const handleSearch = () => { currentPage.value = 1; loadData() }
const handleReset = () => { Object.assign(searchForm, { user_name: '', action: '', target_type: '', date_range: null }) }
const handlePageChange = () => loadData()

onMounted(() => { loadData() })
</script>

<style scoped>
.operation-log { padding: 20px; background: #fff; border-radius: 4px; }
.page-header { margin-bottom: 20px; }
.page-header h3 { margin: 0; }
</style>
