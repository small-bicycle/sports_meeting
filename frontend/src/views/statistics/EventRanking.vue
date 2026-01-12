<template>
  <div class="event-ranking">
    <div class="page-header">
      <h3>项目排名</h3>
      <el-button @click="loadData"><el-icon><Refresh /></el-icon>刷新</el-button>
    </div>

    <div class="filter-bar">
      <el-select v-model="selectedEvent" placeholder="请选择项目" filterable style="width: 200px" @change="loadRanking">
        <el-option v-for="e in events" :key="e.id" :label="e.name" :value="e.id" />
      </el-select>
      <el-select v-model="selectedRound" placeholder="轮次" style="width: 120px; margin-left: 10px" @change="loadRanking">
        <el-option label="决赛" value="final" />
        <el-option label="预赛" value="preliminary" />
      </el-select>
    </div>

    <el-table :data="rankings" v-loading="loading" border stripe>
      <el-table-column prop="rank" label="名次" width="80">
        <template #default="{ row }">
          <el-tag v-if="row.rank <= 3" :type="['', 'warning', 'success', 'info'][row.rank]" effect="dark">
            {{ row.rank }}
          </el-tag>
          <span v-else>{{ row.rank }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="student_name" label="学生姓名" width="120" />
      <el-table-column prop="student_no" label="学号" width="120" />
      <el-table-column prop="class_name" label="班级" width="150" />
      <el-table-column prop="value" label="成绩" width="120" />
      <el-table-column prop="points" label="积分" width="80" />
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/api/request'

const loading = ref(false)
const events = ref([])
const rankings = ref([])
const selectedEvent = ref(null)
const selectedRound = ref('final')

const loadEvents = async () => {
  const res = await request.get('/events')
  events.value = res.data || res || []
  if (events.value.length > 0) {
    selectedEvent.value = events.value[0].id
    await loadRanking()
  }
}

const loadRanking = async () => {
  if (!selectedEvent.value) return
  loading.value = true
  try {
    const res = await request.get(`/statistics/events/${selectedEvent.value}/ranking`, {
      params: { round: selectedRound.value }
    })
    rankings.value = res.data || res || []
  } finally { loading.value = false }
}

const loadData = () => { loadEvents() }

onMounted(() => { loadData() })
</script>

<style scoped>
.event-ranking { padding: 20px; background: #fff; border-radius: 4px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h3 { margin: 0; }
.filter-bar { margin-bottom: 20px; }
</style>
