<template>
  <div class="event-manage">
    <div class="page-header">
      <h3>项目管理</h3>
      <div class="header-actions">
        <el-button type="danger" plain @click="handleClearAll">
          <el-icon><Delete /></el-icon>清除所有
        </el-button>
        <el-button @click="showTemplateDialog = true">
          <el-icon><DocumentCopy /></el-icon>从模板创建
        </el-button>
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>新增项目
        </el-button>
      </div>
    </div>

    <SearchForm v-model="searchForm" :loading="loading" @search="handleSearch" @reset="handleReset">
      <el-form-item label="项目类型">
        <el-select v-model="searchForm.type" placeholder="全部类型" clearable style="width: 120px">
          <el-option label="径赛" value="track" />
          <el-option label="田赛" value="field" />
        </el-select>
      </el-form-item>
      <el-form-item label="子分类">
        <el-select v-model="searchForm.category" placeholder="全部分类" clearable style="width: 120px">
          <el-option-group label="径赛">
            <el-option label="短距离跑" value="短距离跑" />
            <el-option label="中距离跑" value="中距离跑" />
            <el-option label="接力跑" value="接力跑" />
            <el-option label="跨栏跑" value="跨栏跑" />
            <el-option label="游泳" value="游泳" />
            <el-option label="跳绳" value="跳绳" />
          </el-option-group>
          <el-option-group label="田赛">
            <el-option label="投掷" value="投掷" />
            <el-option label="跳跃" value="跳跃" />
          </el-option-group>
          <el-option-group label="其他">
            <el-option label="趣味" value="趣味" />
          </el-option-group>
        </el-select>
      </el-form-item>
      <el-form-item label="项目名称">
        <el-input v-model="searchForm.name" placeholder="项目名称" clearable style="width: 150px" />
      </el-form-item>
    </SearchForm>

    <DataTable :data="filteredEvents" :loading="loading" :show-pagination="false">
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="name" label="项目名称" width="150" />
      <el-table-column prop="type" label="类型" width="80">
        <template #default="{ row }">
          <el-tag :type="getTypeTag(row.type)">{{ getTypeName(row.type) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="category" label="分类" width="100">
        <template #default="{ row }">
          <el-tag type="info" v-if="row.category">{{ row.category }}</el-tag>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column prop="unit" label="单位" width="80" />
      <el-table-column prop="max_per_class" label="每班限报" width="90" />
      <el-table-column prop="max_per_student" label="每人限报" width="90" />
      <el-table-column prop="has_preliminary" label="预赛" width="70">
        <template #default="{ row }">
          <el-tag :type="row.has_preliminary ? 'success' : 'info'" size="small">
            {{ row.has_preliminary ? '是' : '否' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="组别" width="120">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="handleManageGroups(row)">
            管理组别 ({{ row.groups?.length || 0 }})
          </el-button>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
          <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </DataTable>

    <!-- 新增/编辑项目弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑项目' : '新增项目'" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="项目类型" prop="type">
          <el-select v-model="form.type" placeholder="请选择类型" style="width: 100%" @change="onTypeChange">
            <el-option label="径赛" value="track" />
            <el-option label="田赛" value="field" />
          </el-select>
        </el-form-item>
        <el-form-item label="子分类" prop="category">
          <el-select v-model="form.category" placeholder="请选择分类" style="width: 100%">
            <template v-if="form.type === 'track'">
              <el-option label="短距离跑" value="短距离跑" />
              <el-option label="中距离跑" value="中距离跑" />
              <el-option label="接力跑" value="接力跑" />
              <el-option label="跨栏跑" value="跨栏跑" />
              <el-option label="游泳" value="游泳" />
              <el-option label="跳绳" value="跳绳" />
              <el-option label="趣味" value="趣味" />
            </template>
            <template v-else>
              <el-option label="投掷" value="投掷" />
              <el-option label="跳跃" value="跳跃" />
              <el-option label="趣味" value="趣味" />
            </template>
          </el-select>
        </el-form-item>
        <el-form-item label="成绩单位" prop="unit">
          <el-input v-model="form.unit" placeholder="如：秒、米、次、分秒" />
        </el-form-item>
        <el-form-item label="每班限报人数" prop="max_per_class">
          <el-input-number v-model="form.max_per_class" :min="1" :max="50" />
        </el-form-item>
        <el-form-item label="每人限报项数" prop="max_per_student">
          <el-input-number v-model="form.max_per_student" :min="1" :max="10" />
        </el-form-item>
        <el-form-item label="是否有预赛">
          <el-switch v-model="form.has_preliminary" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 模板选择弹窗 -->
    <el-dialog v-model="showTemplateDialog" title="从模板创建项目" width="850px">
      <el-tabs v-model="activeTemplateTab">
        <el-tab-pane label="径赛" name="track">
          <div v-for="(items, cat) in trackCategories" :key="cat" class="template-category">
            <div class="category-header">
              <span class="category-title">{{ cat }}</span>
              <el-checkbox 
                :indeterminate="isCategoryIndeterminate('track', cat)"
                :model-value="isCategoryAllSelected('track', cat)"
                @change="toggleCategorySelection('track', cat)"
              >全选</el-checkbox>
            </div>
            <div class="template-tags">
              <el-checkbox-group v-model="selectedTemplates">
                <el-checkbox 
                  v-for="tpl in items" 
                  :key="tpl.name"
                  :value="tpl.name"
                  :disabled="isTemplateCreated(tpl.name)"
                  class="template-checkbox"
                >
                  <el-tag 
                    :type="isTemplateCreated(tpl.name) ? 'info' : (tpl.is_team ? 'warning' : 'primary')"
                    :effect="isTemplateCreated(tpl.name) ? 'plain' : 'light'"
                  >
                    {{ tpl.name }}
                    <span v-if="tpl.is_team" class="team-badge">团</span>
                  </el-tag>
                </el-checkbox>
              </el-checkbox-group>
            </div>
          </div>
        </el-tab-pane>
        <el-tab-pane label="田赛" name="field">
          <div v-for="(items, cat) in fieldCategories" :key="cat" class="template-category">
            <div class="category-header">
              <span class="category-title">{{ cat }}</span>
              <el-checkbox 
                :indeterminate="isCategoryIndeterminate('field', cat)"
                :model-value="isCategoryAllSelected('field', cat)"
                @change="toggleCategorySelection('field', cat)"
              >全选</el-checkbox>
            </div>
            <div class="template-tags">
              <el-checkbox-group v-model="selectedTemplates">
                <el-checkbox 
                  v-for="tpl in items" 
                  :key="tpl.name"
                  :value="tpl.name"
                  :disabled="isTemplateCreated(tpl.name)"
                  class="template-checkbox"
                >
                  <el-tag 
                    :type="isTemplateCreated(tpl.name) ? 'info' : (tpl.is_team ? 'warning' : 'success')"
                    :effect="isTemplateCreated(tpl.name) ? 'plain' : 'light'"
                  >
                    {{ tpl.name }}
                    <span v-if="tpl.is_team" class="team-badge">团</span>
                  </el-tag>
                </el-checkbox>
              </el-checkbox-group>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
      <div class="template-footer">
        <div class="template-tip">
          <el-icon><InfoFilled /></el-icon>
          <span>已选择 {{ selectedTemplates.length }} 个项目</span>
          <el-tag type="warning" size="small" style="margin-left: 10px">团</el-tag>
          <span style="margin-left: 4px; color: #909399;">= 团体项目</span>
        </div>
        <div class="template-actions">
          <el-button @click="selectedTemplates = []">清空选择</el-button>
          <el-button @click="selectAllAvailable">全部选择</el-button>
          <el-button type="primary" :loading="batchLoading" :disabled="selectedTemplates.length === 0" @click="handleBatchCreate">
            批量创建 ({{ selectedTemplates.length }})
          </el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 组别管理弹窗 -->
    <el-dialog v-model="showGroupDialog" :title="`${currentEvent?.name} - 组别管理`" width="500px">
      <div class="group-header">
        <el-select v-model="selectedGroupNames" multiple placeholder="选择要添加的组别" style="width: 280px">
          <el-option 
            v-for="opt in availableGroups" 
            :key="opt.name" 
            :label="opt.name" 
            :value="opt.name"
          />
        </el-select>
        <el-button type="primary" :disabled="selectedGroupNames.length === 0" :loading="groupLoading" @click="handleAddGroups">
          添加 ({{ selectedGroupNames.length }})
        </el-button>
      </div>
      <el-table :data="eventGroups" border style="margin-top: 15px">
        <el-table-column prop="name" label="组别名称" />
        <el-table-column prop="gender" label="性别限制" width="100">
          <template #default="{ row }">
            {{ { M: '仅男生', F: '仅女生', A: '不限' }[row.gender] || row.gender }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-button type="danger" link @click="handleDeleteGroup(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div v-if="eventGroups.length === 0" class="empty-tip">暂无组别，请添加</div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Check, InfoFilled, Delete } from '@element-plus/icons-vue'
import { useEventStore } from '@/stores/event'
import DataTable from '@/components/common/DataTable.vue'
import SearchForm from '@/components/common/SearchForm.vue'
import request from '@/api/request'

const eventStore = useEventStore()

const loading = ref(false)
const events = ref([])
const templates = ref([])
const eventGroups = ref([])
const dialogVisible = ref(false)
const showTemplateDialog = ref(false)
const showGroupDialog = ref(false)
const isEdit = ref(false)
const submitLoading = ref(false)
const batchLoading = ref(false)
const formRef = ref(null)
const currentId = ref(null)
const currentEvent = ref(null)
const activeTemplateTab = ref('track')
const selectedTemplates = ref([])
const groupLoading = ref(false)
const selectedGroupNames = ref([])

const searchForm = reactive({ type: '', category: '', name: '' })

const form = reactive({
  name: '',
  type: 'track',
  category: '',
  unit: '秒',
  max_per_class: 3,
  max_per_student: 3,
  has_preliminary: false
})

// 固定的三个组别选项
const groupOptions = [
  { name: '男子组', gender: 'M' },
  { name: '女子组', gender: 'F' },
  { name: '团体组', gender: 'A' }
]

// 可添加的组别（排除已有的）
const availableGroups = computed(() => {
  return groupOptions.filter(opt => !eventGroups.value.some(g => g.name === opt.name))
})

const rules = {
  name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择项目类型', trigger: 'change' }],
  unit: [{ required: true, message: '请输入成绩单位', trigger: 'blur' }]
}

// 按分类组织模板
const trackCategories = computed(() => {
  const cats = {}
  templates.value.filter(t => t.type === 'track').forEach(t => {
    const cat = t.category || '其他'
    if (!cats[cat]) cats[cat] = []
    cats[cat].push(t)
  })
  return cats
})

const fieldCategories = computed(() => {
  const cats = {}
  templates.value.filter(t => t.type === 'field').forEach(t => {
    const cat = t.category || '其他'
    if (!cats[cat]) cats[cat] = []
    cats[cat].push(t)
  })
  return cats
})

// 检查模板是否已创建
const isTemplateCreated = (name) => {
  return events.value.some(e => e.name === name)
}

// 获取分类下可选的模板
const getAvailableInCategory = (type, cat) => {
  const cats = type === 'track' ? trackCategories.value : fieldCategories.value
  return (cats[cat] || []).filter(t => !isTemplateCreated(t.name)).map(t => t.name)
}

// 检查分类是否全选
const isCategoryAllSelected = (type, cat) => {
  const available = getAvailableInCategory(type, cat)
  if (available.length === 0) return false
  return available.every(name => selectedTemplates.value.includes(name))
}

// 检查分类是否部分选中
const isCategoryIndeterminate = (type, cat) => {
  const available = getAvailableInCategory(type, cat)
  if (available.length === 0) return false
  const selectedCount = available.filter(name => selectedTemplates.value.includes(name)).length
  return selectedCount > 0 && selectedCount < available.length
}

// 切换分类全选
const toggleCategorySelection = (type, cat) => {
  const available = getAvailableInCategory(type, cat)
  const allSelected = isCategoryAllSelected(type, cat)
  
  if (allSelected) {
    // 取消选择该分类
    selectedTemplates.value = selectedTemplates.value.filter(name => !available.includes(name))
  } else {
    // 全选该分类
    const newSelection = [...selectedTemplates.value]
    available.forEach(name => {
      if (!newSelection.includes(name)) newSelection.push(name)
    })
    selectedTemplates.value = newSelection
  }
}

// 选择所有可用模板
const selectAllAvailable = () => {
  const all = templates.value.filter(t => !isTemplateCreated(t.name)).map(t => t.name)
  selectedTemplates.value = all
}

const filteredEvents = computed(() => {
  let result = events.value
  if (searchForm.type) result = result.filter(e => e.type === searchForm.type)
  if (searchForm.category) result = result.filter(e => e.category === searchForm.category)
  if (searchForm.name) result = result.filter(e => e.name.includes(searchForm.name))
  return result
})

const getTypeName = (type) => ({ track: '径赛', field: '田赛' }[type] || type)
const getTypeTag = (type) => ({ track: 'primary', field: 'success' }[type] || 'info')

const loadData = async () => {
  loading.value = true
  try {
    events.value = await eventStore.fetchEvents()
  } finally {
    loading.value = false
  }
}

const loadTemplates = async () => {
  templates.value = await eventStore.fetchTemplates()
}

const handleSearch = () => loadData()
const handleReset = () => { searchForm.type = ''; searchForm.category = ''; searchForm.name = '' }

const onTypeChange = () => {
  form.category = ''
  form.unit = form.type === 'track' ? '秒' : '米'
}

const resetForm = () => {
  Object.assign(form, { name: '', type: 'track', category: '', unit: '秒', max_per_class: 3, max_per_student: 3, has_preliminary: false })
  currentId.value = null
}

const handleAdd = () => { isEdit.value = false; resetForm(); dialogVisible.value = true }

const handleEdit = (row) => {
  isEdit.value = true
  currentId.value = row.id
  Object.assign(form, { 
    name: row.name, 
    type: row.type, 
    category: row.category || '',
    unit: row.unit, 
    max_per_class: row.max_per_class, 
    max_per_student: row.max_per_student, 
    has_preliminary: row.has_preliminary 
  })
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除项目"${row.name}"吗？`, '提示', { type: 'warning' })
    await eventStore.deleteEvent(row.id)
    ElMessage.success('删除成功')
    await loadData()
  } catch (e) { if (e !== 'cancel') ElMessage.error(e.message || '删除失败') }
}

const handleClearAll = async () => {
  if (events.value.length === 0) {
    ElMessage.warning('暂无项目可清除')
    return
  }
  try {
    await ElMessageBox.confirm(
      `确定要清除所有 ${events.value.length} 个项目吗？此操作不可恢复！`, 
      '危险操作', 
      { type: 'error', confirmButtonText: '确定清除', cancelButtonText: '取消' }
    )
    const res = await request.delete('/events/all')
    ElMessage.success(res.message || '清除成功')
    await loadData()
  } catch (e) { 
    if (e !== 'cancel') ElMessage.error(e.response?.data?.detail || e.message || '清除失败') 
  }
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitLoading.value = true
  try {
    if (isEdit.value) {
      await eventStore.updateEvent(currentId.value, form)
      ElMessage.success('更新成功')
    } else {
      await eventStore.createEvent(form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    await loadData()
  } catch (e) { ElMessage.error(e.message || '操作失败') }
  finally { submitLoading.value = false }
}

const handleBatchCreate = async () => {
  if (selectedTemplates.value.length === 0) {
    ElMessage.warning('请先选择要创建的项目')
    return
  }
  batchLoading.value = true
  try {
    const res = await request.post('/events/batch-from-templates', selectedTemplates.value)
    ElMessage.success(res.message || `成功创建 ${res.success} 个项目`)
    if (res.errors?.length > 0) {
      console.warn('部分项目创建失败:', res.errors)
    }
    selectedTemplates.value = []
    showTemplateDialog.value = false
    await loadData()
  } catch (e) { 
    ElMessage.error(e.response?.data?.detail || e.message || '创建失败') 
  } finally { 
    batchLoading.value = false 
  }
}

const handleManageGroups = async (row) => {
  currentEvent.value = row
  try {
    const res = await eventStore.fetchEventGroups(row.id)
    eventGroups.value = Array.isArray(res) ? res : []
  } catch (e) {
    console.error('获取组别失败:', e)
    eventGroups.value = []
  }
  selectedGroupNames.value = []
  showGroupDialog.value = true
}

// 批量添加组别
const handleAddGroups = async () => {
  if (selectedGroupNames.value.length === 0 || groupLoading.value) return
  
  groupLoading.value = true
  try {
    for (const name of selectedGroupNames.value) {
      const opt = groupOptions.find(o => o.name === name)
      if (opt) {
        await request.post(`/events/${currentEvent.value.id}/groups`, {
          name: opt.name,
          gender: opt.gender,
          grade_ids: []
        })
      }
    }
    ElMessage.success(`已添加 ${selectedGroupNames.value.length} 个组别`)
    const res = await eventStore.fetchEventGroups(currentEvent.value.id)
    eventGroups.value = Array.isArray(res) ? res : []
    selectedGroupNames.value = []
    await loadData()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || e.message || '添加失败')
  } finally {
    groupLoading.value = false
  }
}

// 删除组别
const handleDeleteGroup = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除"${row.name}"吗？`, '提示', { type: 'warning' })
    groupLoading.value = true
    await request.delete(`/events/groups/${row.id}`)
    ElMessage.success('删除成功')
    const res = await eventStore.fetchEventGroups(currentEvent.value.id)
    eventGroups.value = Array.isArray(res) ? res : []
    await loadData()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(e.response?.data?.detail || e.message || '删除失败')
    }
  } finally {
    groupLoading.value = false
  }
}

onMounted(() => { loadData(); loadTemplates() })
</script>

<style scoped>
.event-manage { padding: 20px; background: #fff; border-radius: 4px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h3 { margin: 0; }
.header-actions { display: flex; gap: 10px; }
.group-header { margin-bottom: 15px; }

.template-category { margin-bottom: 20px; }
.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding: 0 8px;
}
.category-title { 
  font-size: 14px; 
  color: #606266; 
  padding-left: 8px;
  border-left: 3px solid #409eff;
}
.template-tags { display: flex; flex-wrap: wrap; gap: 8px; padding-left: 8px; }
.template-checkbox { margin-right: 0 !important; }
.template-checkbox :deep(.el-checkbox__label) { padding-left: 4px; }
.team-badge {
  display: inline-block;
  font-size: 10px;
  background: rgba(230, 162, 60, 0.3);
  color: #e6a23c;
  padding: 0 4px;
  border-radius: 2px;
  margin-left: 4px;
}

.template-footer {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #ebeef5;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.template-tip {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #909399;
  font-size: 13px;
}
.template-actions { display: flex; gap: 10px; }

/* 组别管理样式 */
.group-header { display: flex; gap: 10px; align-items: center; }
.empty-tip { text-align: center; color: #909399; padding: 20px 0; }
</style>
