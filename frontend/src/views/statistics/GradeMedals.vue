<template>
  <div class="grade-medals">
    <div class="page-header">
      <h3>年级奖牌榜</h3>
      <el-button @click="loadData"><el-icon><Refresh /></el-icon>刷新</el-button>
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
      <el-table-column prop="grade_name" label="年级" width="150" />
      <el-table-column prop="gold" label="金牌" width="100">
        <template #default="{ row }">
          <span class="medal gold">🥇 {{ row.gold || 0 }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="silver" label="银牌" width="100">
        <template #default="{ row }">
          <span class="medal silver">🥈 {{ row.silver || 0 }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="bronze" label="铜牌" width="100">
        <template #default="{ row }">
          <span class="medal bronze">🥉 {{ row.bronze || 0 }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="total_medals" label="奖牌总数" width="100" />
      <el-table-column prop="total_points" label="总积分" width="100" />
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/api/request'

const loading = ref(false)
const rankings = ref([])

const loadData = async () => {
  loading.value = true
  try {
    const res = await request.get('/statistics/grades/medals')
    rankings.value = res.data || res || []
  } finally { loading.value = false }
}

onMounted(() => { loadData() })
</script>

<style scoped>
.grade-medals { padding: 20px; background: #fff; border-radius: 4px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h3 { margin: 0; }
.medal { font-size: 16px; }
.medal.gold { color: #f5a623; }
.medal.silver { color: #999; }
.medal.bronze { color: #cd7f32; }
</style>
