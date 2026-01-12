<template>
  <div class="event-manage">
    <div class="page-header">
      <h3>项目管理</h3>
      <div class="header-actions">
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
          <el-option label="接力" value="relay" />
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
          <el-select v-model="form.type" placeholder="请选择类型" style="width: 100%">
            <el-option label="径赛" value="track" />
            <el-option label="田赛" value="field" />
            <el-option label="接力" value="relay" />
          </el-select>
        </el-form-item>
        <el-form-item label="成绩单位" prop="unit">
          <el-input v-model="form.unit" placeholder="如：秒、米、分秒" />
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
    <el-dialog v-model="showTemplateDialog" title="从模板创建项目" width="600px">
      <el-table :data="templates" border>
        <el-table-column prop="name" label="项目名称" />
        <el-table-column prop="type" label="类型" width="80">
          <template #default="{ row }">{{ getTypeName(row.type) }}</template>
        </el-table-column>
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleCreateFromTemplate(row)">创建</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <!-- 组别管理弹窗 -->
    <el-dialog v-model="showGroupDialog" :title="`${currentEvent?.name} - 组别管理`" width="700px">
      <div class="group-header">
        <el-button type="primary" size="small" @click="handleAddGroup">新增组别</el-button>
      </div>
      <el-table :data="eventGroups" border>
        <el-table-column prop="name" label="组别名称" />
        <el-table-column prop="gender" label="性别" width="80" />
        <el-table-column label="适用年级">
          <template #default="{ row }">
            {{ row.grade_names?.join('、') || '全部年级' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEditGroup(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDeleteGroup(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useEventStore } from '@/stores/event'
import DataTable from '@/components/common/DataTable.vue'
import SearchForm from '@/components/common/SearchForm.vue'

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
const formRef = ref(null)
const currentId = ref(null)
const currentEvent = ref(null)

const searchForm = reactive({ type: '', name: '' })

const form = reactive({
  name: '',
  type: 'track',
  unit: '秒',
  max_per_class: 3,
  max_per_student: 3,
  has_preliminary: false
})

const rules = {
  name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择项目类型', trigger: 'change' }],
  unit: [{ required: true, message: '请输入成绩单位', trigger: 'blur' }]
}

const filteredEvents = computed(() => {
  let result = events.value
  if (searchForm.type) result = result.filter(e => e.type === searchForm.type)
  if (searchForm.name) result = result.filter(e => e.name.includes(searchForm.name))
  return result
})

const getTypeName = (type) => ({ track: '径赛', field: '田赛', relay: '接力' }[type] || type)
const getTypeTag = (type) => ({ track: 'primary', field: 'success', relay: 'warning' }[type] || 'info')

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
const handleReset = () => { searchForm.type = ''; searchForm.name = '' }

const resetForm = () => {
  Object.assign(form, { name: '', type: 'track', unit: '秒', max_per_class: 3, max_per_student: 3, has_preliminary: false })
  currentId.value = null
}

const handleAdd = () => { isEdit.value = false; resetForm(); dialogVisible.value = true }

const handleEdit = (row) => {
  isEdit.value = true
  currentId.value = row.id
  Object.assign(form, { name: row.name, type: row.type, unit: row.unit, max_per_class: row.max_per_class, max_per_student: row.max_per_student, has_preliminary: row.has_preliminary })
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

const handleCreateFromTemplate = async (tpl) => {
  try {
    await eventStore.createFromTemplate(tpl.id)
    ElMessage.success('创建成功')
    showTemplateDialog.value = false
    await loadData()
  } catch (e) { ElMessage.error(e.message || '创建失败') }
}

const handleManageGroups = async (row) => {
  currentEvent.value = row
  eventGroups.value = await eventStore.fetchEventGroups(row.id)
  showGroupDialog.value = true
}

const handleAddGroup = () => { ElMessage.info('组别新增功能待实现') }
const handleEditGroup = () => { ElMessage.info('组别编辑功能待实现') }
const handleDeleteGroup = () => { ElMessage.info('组别删除功能待实现') }

onMounted(() => { loadData(); loadTemplates() })
</script>

<style scoped>
.event-manage { padding: 20px; background: #fff; border-radius: 4px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h3 { margin: 0; }
.header-actions { display: flex; gap: 10px; }
.group-header { margin-bottom: 15px; }
</style>
