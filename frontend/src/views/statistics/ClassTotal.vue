<template>
  <div class="class-total">
    <div class="page-header">
      <h3>班级总分榜</h3>
      <el-button @click="loadData"><el-icon><Refresh /></el-icon>刷新</el-button>
    </div>

    <div class="filter-bar">
      <el-select v-model="selectedGrade" placeholder="全部年级" clearable style="width: 150px" @change="loadData">
        <el-option v-for="g in grades" :key="g.id" :label="g.name" :value="g.id" />
      </el-select>
    </div>

    <el-table :data="rankings" v-loading="loading" border stripe>
      <el-table-column prop="rank" label="排名" width="80">
        <template #default="{ row }">
          <el-tag v-if="row.rank <= 3" :type="['', 'warning', 'success', 'info'][row.rank]" effect="dark">
            {{ row.rank }}
          </el-tag>
          <span v-else>{{ row.rank }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="grade_name" label="年级" width="120" />
      <el-table-column prop="class_name" label="班级" width="150" />
      <el-table-column prop="total_points" label="总积分" width="100" />
      <el-table-column prop="gold" label="金牌" width="80">
        <template #default="{ row }">
          <span style="color: #f5a623">{{ row.gold || 0 }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="silver" label="银牌" width="80">
        <template #default="{ row }">
          <span style="color: #999">{{ row.silver || 0 }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="bronze" label="铜牌" width="80">
        <template #default="{ row }">
          <span style="color: #cd7f32">{{ row.bronze || 0 }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="participant_count" label="参赛人次" width="100" />
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/api/request'

const loading = ref(false)
const grades = ref([])
const rankings = ref([])
const selectedGrade = ref(null)

const loadGrades = async () => {
  const res = await request.get('/grades')
  grades.value = res.data || res || []
}

const loadData = async () => {
  loading.value = true
  try {
    const params = selectedGrade.value ? { grade_id: selectedGrade.value } : {}
    const res = await request.get('/statistics/classes/total', { params })
    rankings.value = res.data || res || []
  } finally { loading.value = false }
}

onMounted(() => { loadGrades(); loadData() })
</script>

<style scoped>
.class-total { padding: 20px; background: #fff; border-radius: 4px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h3 { margin: 0; }
.filter-bar { margin-bottom: 20px; }
</style>
