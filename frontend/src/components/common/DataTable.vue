<template>
  <div class="data-table">
    <el-table 
      ref="tableRef"
      :data="data" 
      v-loading="loading" 
      border 
      stripe
      :row-key="rowKey"
      :default-sort="defaultSort"
      @sort-change="handleSortChange"
      @selection-change="handleSelectionChange"
    >
      <!-- 选择列 -->
      <el-table-column v-if="showSelection" type="selection" width="55" />
      <!-- 序号列 -->
      <el-table-column v-if="showIndex" type="index" label="序号" width="60" />
      <!-- 自定义列 -->
      <slot></slot>
    </el-table>
    
    <div v-if="showPagination" class="pagination-wrapper">
      <div class="pagination-info">
        <span v-if="selectedCount > 0">已选择 {{ selectedCount }} 项</span>
      </div>
      <el-pagination
        class="pagination"
        :current-page="currentPage"
        :page-size="pageSize"
        :page-sizes="pageSizes"
        :total="total"
        :layout="paginationLayout"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  data: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  total: { type: Number, default: 0 },
  currentPage: { type: Number, default: 1 },
  pageSize: { type: Number, default: 20 },
  pageSizes: { type: Array, default: () => [10, 20, 50, 100] },
  showPagination: { type: Boolean, default: true },
  showSelection: { type: Boolean, default: false },
  showIndex: { type: Boolean, default: false },
  rowKey: { type: String, default: 'id' },
  defaultSort: { type: Object, default: null },
  paginationLayout: { type: String, default: 'total, sizes, prev, pager, next, jumper' }
})

const emit = defineEmits([
  'update:currentPage', 
  'update:pageSize', 
  'page-change',
  'sort-change',
  'selection-change'
])

const tableRef = ref(null)
const selectedRows = ref([])

const selectedCount = computed(() => selectedRows.value.length)

const handleSizeChange = (size) => {
  emit('update:pageSize', size)
  emit('page-change', { page: 1, size })
}

const handleCurrentChange = (page) => {
  emit('update:currentPage', page)
  emit('page-change', { page, size: props.pageSize })
}

const handleSortChange = ({ prop, order }) => {
  emit('sort-change', { prop, order })
}

const handleSelectionChange = (selection) => {
  selectedRows.value = selection
  emit('selection-change', selection)
}

// 暴露方法
const clearSelection = () => {
  tableRef.value?.clearSelection()
}

const toggleRowSelection = (row, selected) => {
  tableRef.value?.toggleRowSelection(row, selected)
}

defineExpose({
  clearSelection,
  toggleRowSelection,
  tableRef
})
</script>

<style scoped>
.data-table {
  background: #fff;
  border-radius: 4px;
}

.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-info {
  color: #666;
  font-size: 14px;
}

.pagination {
  display: flex;
  justify-content: flex-end;
}
</style>
