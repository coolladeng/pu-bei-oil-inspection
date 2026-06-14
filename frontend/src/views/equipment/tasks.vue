<template>
  <div class="tasks-page">
    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="任务名称"><el-input v-model="searchForm.name" placeholder="搜索" clearable /></el-form-item>
        <el-form-item label="班组"><el-tree-select v-model="searchForm.dept_id" :data="deptTree" :props="{ label: 'name', value: 'id', children: 'children' }" placeholder="选择班组" clearable filterable style="width: 200px" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部" clearable style="width: 120px">
            <el-option label="待执行" :value="0" /><el-option label="执行中" :value="1" /><el-option label="已完成" :value="2" /><el-option label="超时" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item><el-button type="primary" @click="loadData">查询</el-button><el-button @click="resetSearch">重置</el-button></el-form-item>
      </el-form>
    </el-card>

    <!-- 表格 -->
    <el-card>
      <div class="table-header">
        <el-button type="primary" @click="openDialog()"><el-icon><Plus /></el-icon>新建任务</el-button>
        <el-button @click="importVisible = true"><el-icon><Upload /></el-icon>Excel导入</el-button>
        <el-button link type="primary" @click="downloadTemplate">下载模板</el-button>
      </div>
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="task_name" label="任务名称" min-width="180" />
        <el-table-column prop="dept_name" label="班组" width="140" />
        <el-table-column label="类型" width="80"><template #default="{ row }">{{ row.taskType === 'regular' ? '定期' : '一次' }}</template></el-table-column>
        <el-table-column prop="frequency" label="频率" width="80">
          <template #default="{ row }">{{ freqLabel(row.frequency) }}</template>
        </el-table-column>
        <el-table-column label="设备数" width="80">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewEquipments(row)">{{ row.equipCount ?? 0 }}</el-button>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80"><template #default="{ row }"><el-tag :type="statusTag(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag></template></el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }"><el-button link type="primary" @click="openDialog(row)">编辑</el-button><el-button link type="danger" @click="handleDelete(row)">删除</el-button></template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrap">
        <el-pagination v-model:current-page="page" v-model:page-size="pageSize" :total="total" :page-sizes="[10,20,50]" layout="total, sizes, prev, pager, next" @change="loadData" />
      </div>
    </el-card>

    <!-- 编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑检查任务' : '新建检查任务'" width="650px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="任务名称" prop="task_name"><el-input v-model="form.task_name" placeholder="如 1月设备周检" /></el-form-item>
        <el-form-item label="负责班组" prop="dept_id">
          <el-tree-select v-model="form.dept_id" :data="deptTree" :props="{ label: 'name', value: 'id', children: 'children' }" placeholder="选择班组" filterable style="width: 100%" />
        </el-form-item>
        <el-form-item label="任务类型" prop="taskType">
          <el-select v-model="form.taskType" style="width: 100%">
            <el-option label="定期任务" value="regular" />
            <el-option label="一次性任务" value="one_time" />
          </el-select>
        </el-form-item>
        <el-form-item label="频率" v-if="form.taskType === 'regular'">
          <el-select v-model="form.frequency" style="width: 100%">
            <el-option label="每日" value="daily" />
            <el-option label="每周" value="weekly" />
            <el-option label="每月" value="monthly" />
          </el-select>
        </el-form-item>
        <el-form-item label="截止日期" v-if="form.taskType === 'one_time'">
          <el-date-picker v-model="form.deadline" type="date" placeholder="选择截止日期" style="width: 100%" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="关联设备">
          <el-select v-model="form.equipIds" multiple filterable placeholder="选择设备（可多选）" style="width: 100%" :loading="equipLoading">
            <el-option v-for="e in allEquipments" :key="e.id" :label="`${e.code} - ${e.name}`" :value="e.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 关联设备查看弹窗 -->
    <el-dialog v-model="equipViewVisible" title="关联设备列表" width="500px">
      <el-table :data="viewEquipList" stripe max-height="400">
        <el-table-column prop="code" label="编号" width="120" />
        <el-table-column prop="name" label="名称" min-width="200" />
      </el-table>
    </el-dialog>

    <!-- Excel导入弹窗 -->
    <el-dialog v-model="importVisible" title="Excel批量导入任务" width="500px" destroy-on-close>
      <el-alert type="info" :closable="false" show-icon style="margin-bottom: 16px;">
        <template #title>表头：任务名称、班组名称、任务类型(定期/一次性)、频率(每日/每周/每月)</template>
      </el-alert>
      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :limit="1"
        accept=".xlsx,.xls"
        :on-change="handleFileChange"
        :file-list="fileList"
        drag
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
      </el-upload>
      <template #footer>
        <el-button @click="importVisible = false">取消</el-button>
        <el-button type="primary" @click="doImport" :loading="importing">开始导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { Plus, Upload, UploadFilled } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/api/http'

const loading = ref(false); const submitting = ref(false)
const list = ref<any[]>([]); const total = ref(0); const page = ref(1); const pageSize = ref(20)
const deptTree = ref<any[]>([])

const searchForm = reactive({ name: '', dept_id: null as number | null, status: null as number | null })

// 编辑弹窗
const dialogVisible = ref(false); const editingId = ref<number | null>(null)
const formRef = ref(); const equipLoading = ref(false); const allEquipments = ref<any[]>([])
const form = reactive({
  task_name: '', dept_id: null as number | null,
  taskType: 'regular', frequency: 'daily',
  deadline: null as string | null, equipIds: [] as number[],
})
const rules = {
  task_name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
  dept_id: [{ required: true, message: '请选择班组', trigger: 'change' }],
  taskType: [{ required: true, message: '请选择任务类型', trigger: 'change' }],
}

// 设备查看
const equipViewVisible = ref(false); const viewEquipList = ref<any[]>([])

// 导入
const importVisible = ref(false); const importing = ref(false)
const uploadRef = ref(); const fileList = ref<any[]>([]); const importFile = ref<File | null>(null)

// ===== 工具函数 =====
function statusTag(s: number) { return ['info', '', 'success', 'danger'][s] || 'info' }
function statusLabel(s: number) { return ['待执行', '执行中', '已完成', '超时'][s] || '未知' }
function freqLabel(f: string) { return { daily: '每日', weekly: '每周', monthly: '每月' }[f] || (f || '-') }

// ===== 数据加载 =====
async function loadDeptTree() { const data = await request.get('/departments'); deptTree.value = Array.isArray(data) ? data : [] }
async function loadData() {
  loading.value = true
  try {
    const params: any = { page: page.value, pageSize: pageSize.value }
    if (searchForm.name) params.name = searchForm.name
    if (searchForm.dept_id) params.dept_id = searchForm.dept_id
    if (searchForm.status !== null && searchForm.status !== undefined) params.status = searchForm.status
    const data = await request.get('/check-tasks', { params })
    list.value = data.list || []
    total.value = data.total || 0
  } finally { loading.value = false }
}
function resetSearch() { searchForm.name = ''; searchForm.dept_id = null; searchForm.status = null; page.value = 1; loadData() }

// ===== 加载设备列表 =====
async function loadAllEquipments() {
  equipLoading.value = true
  try {
    const data = await request.get('/equipments', { params: { pageSize: 9999 } })
    allEquipments.value = data.list || []
  } finally { equipLoading.value = false }
}

// ===== 任务CRUD =====
function resetForm() {
  form.task_name = ''; form.dept_id = null
  form.taskType = 'regular'; form.frequency = 'daily'
  form.deadline = null; form.equipIds = []
}
async function openDialog(row?: any) {
  resetForm(); await loadAllEquipments()
  editingId.value = row?.id || null
  if (row) {
    form.task_name = row.task_name || ''
    form.dept_id = row.dept_id
    form.taskType = row.taskType || 'regular'
    form.frequency = row.frequency || 'daily'
    form.deadline = row.deadline || null
    // 加载已有设备关联
    try {
      const equips = await request.get(`/check-tasks/${row.id}/equipments`)
      form.equipIds = (equips || []).map((e: any) => e.id)
    } catch { form.equipIds = [] }
  }
  dialogVisible.value = true
}
async function submitForm() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return; submitting.value = true
  try {
    const payload: any = {
      task_name: form.task_name,
      dept_id: form.dept_id,
      taskType: form.taskType,
      frequency: form.taskType === 'regular' ? form.frequency : null,
      deadline: form.taskType === 'one_time' ? form.deadline : null,
      equipIds: form.equipIds,
    }
    if (editingId.value) {
      await request.put(`/check-tasks/${editingId.value}`, payload)
      ElMessage.success('更新成功')
    } else {
      await request.post('/check-tasks', payload)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false; loadData()
  } finally { submitting.value = false }
}
async function handleDelete(row: any) {
  await ElMessageBox.confirm(`确定删除任务"${row.task_name}"吗？`, '确认', { type: 'warning' })
  await request.delete(`/check-tasks/${row.id}`); ElMessage.success('删除成功'); loadData()
}

// ===== 查看关联设备 =====
async function viewEquipments(row: any) {
  viewEquipList.value = []
  try {
    viewEquipList.value = await request.get(`/check-tasks/${row.id}/equipments`) || []
  } catch { viewEquipList.value = [] }
  equipViewVisible.value = true
}

// ===== Excel导入 =====
function handleFileChange(file: any) { importFile.value = file.raw }
async function doImport() {
  if (!importFile.value) { ElMessage.warning('请选择文件'); return }
  importing.value = true
  try {
    const fd = new FormData(); fd.append('file', importFile.value)
    await request.post('/check-tasks/import', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    ElMessage.success('导入完成')
    importVisible.value = false; fileList.value = []; importFile.value = null
    loadData()
  } finally { importing.value = false }
}
async function downloadTemplate() {
  // Build CSV as a simple template
  const csv = '\uFEFF任务名称,班组名称,任务类型,频率\n日检任务,班组1,定期,每日\n周检任务,班组1,定期,每周'
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a'); a.href = url; a.download = 'check_task_template.csv'
  a.click(); URL.revokeObjectURL(url)
}

onMounted(() => { loadDeptTree(); loadData() })
</script>
<style scoped>
.tasks-page { padding: 16px; }
.search-card { margin-bottom: 16px; }
.table-header { margin-bottom: 16px; display: flex; gap: 12px; }
.pagination-wrap { margin-top: 16px; display: flex; justify-content: flex-end; }
</style>

