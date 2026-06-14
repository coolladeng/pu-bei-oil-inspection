<template>
  <div class="inspection-points">
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="巡检点名称">
          <el-input v-model="searchForm.name" placeholder="请输入" clearable />
        </el-form-item>
        <el-form-item label="所属部门">
          <el-tree-select
            v-model="searchForm.dept_id"
            :data="deptTree"
            :props="{ label: 'name', value: 'id', children: 'children' }"
            placeholder="选择部门"
            clearable
            filterable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部" clearable style="width: 120px">
            <el-option label="启用" :value="1" />
            <el-option label="停用" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadPoints">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card">
      <div class="table-header">
        <el-button type="primary" @click="openDialog()">
          <el-icon><Plus /></el-icon>新增巡检点
        </el-button>
        <el-button @click="importVisible = true">
          <el-icon><Upload /></el-icon>批量导入
        </el-button>
        <el-button link type="primary" @click="downloadTemplate">
          下载导入模板
        </el-button>
      </div>

      <el-table :data="points" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="code" label="编号" width="120" />
        <el-table-column prop="name" label="名称" min-width="150" />
        <el-table-column prop="nfcUid" label="NFC UID" width="140">
          <template #default="{ row }">
            <el-tag v-if="row.nfcUid" type="success" size="small">{{ row.nfcUid }}</el-tag>
            <span v-else class="text-muted">未绑定</span>
          </template>
        </el-table-column>
        <el-table-column prop="dept_name" label="所属部门" width="150" />
        <el-table-column prop="address" label="位置" min-width="180" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">
              {{ row.status === 1 ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @change="loadPoints"
        />
      </div>
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="巡检点编号" prop="code">
          <el-input v-model="form.code" placeholder="如 PT-001" />
        </el-form-item>
        <el-form-item label="巡检点名称" prop="name">
          <el-input v-model="form.name" placeholder="如 1号分离器" />
        </el-form-item>
        <el-form-item label="NFC标签UID">
          <el-input v-model="form.nfcUid" placeholder="NTAG213 标签UID">
            <template #append>
              <el-button @click="readNfc">读取NFC</el-button>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="所属部门" prop="dept_id">
          <el-tree-select
            v-model="form.dept_id"
            :data="deptTree"
            :props="{ label: 'name', value: 'id', children: 'children' }"
            placeholder="选择所属部门"
            filterable
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="GPS纬度">
          <el-input-number v-model="form.latitude" :precision="6" :step="0.01" placeholder="如 46.5891" style="width: 100%" />
        </el-form-item>
        <el-form-item label="GPS经度">
          <el-input-number v-model="form.longitude" :precision="6" :step="0.01" placeholder="如 125.1037" style="width: 100%" />
        </el-form-item>
        <el-form-item label="位置描述">
          <el-input v-model="form.address" type="textarea" :rows="2" placeholder="如 大庆油田第一采油厂" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 批量导入弹窗 -->
    <el-dialog v-model="importVisible" title="批量导入巡检点" width="500px">
      <div class="import-hint">
        <el-alert type="info" :closable="false" show-icon>
          <template #title>
            <span>支持 .xlsx / .xls 格式，表头：编号、名称、NFC_UID、部门、纬度、经度、位置描述</span>
          </template>
        </el-alert>
      </div>
      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :limit="1"
        accept=".xlsx,.xls"
        :on-change="handleFileChange"
        :on-exceed="() => ElMessage.warning('每次只能上传一个文件')"
        :file-list="fileList"
        drag
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
      </el-upload>
      <template #footer>
        <el-button @click="importVisible = false; fileList = []">取消</el-button>
        <el-button type="primary" @click="submitImport" :loading="importing" :disabled="!uploadFile">确认导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { Plus, Upload, UploadFilled } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { UploadInstance, UploadFile as ElUploadFile, UploadRawFile } from 'element-plus'
import request from '@/api/http'

interface RunPoint {
  id: number
  code: string
  name: string
  nfcUid: string | null
  dept_id: number
  dept_name: string
  latitude: number | null
  longitude: number | null
  address: string | null
  status: number
}

const loading = ref(false)
const submitting = ref(false)
const points = ref<RunPoint[]>([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const deptTree = ref<any[]>([])

const searchForm = reactive({
  name: '',
  dept_id: null as number | null,
  status: null as number | null,
})

const dialogVisible = ref(false)
const dialogTitle = ref('新增巡检点')
const editingId = ref<number | null>(null)
const formRef = ref()

const form = reactive({
  code: '',
  name: '',
  nfcUid: '',
  dept_id: null as number | null,
  latitude: null as number | null,
  longitude: null as number | null,
  address: '',
})

const rules = {
  code: [{ required: true, message: '请输入编号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  dept_id: [{ required: true, message: '请选择所属部门', trigger: 'change' }],
}

// 批量导入相关
const importVisible = ref(false)
const importing = ref(false)
const fileList = ref<ElUploadFile[]>([])
const uploadFile = ref<File | null>(null)
const uploadRef = ref<UploadInstance>()

function handleFileChange(file: ElUploadFile) {
  uploadFile.value = (file as UploadRawFile).raw || null
}

function downloadTemplate() {
  const csvContent = '编号,名称,NFC_UID,部门,纬度,经度,位置描述\nPT-001,1号分离器,,采油一队,46.5891,125.1037,大庆油田第一采油厂\nPT-002,3号加热炉,,采油二队,46.5900,125.1100,大庆油田第一采油厂'
  const BOM = '\uFEFF'
  const blob = new Blob([BOM + csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = '巡检点导入模板.csv'
  link.click()
  URL.revokeObjectURL(url)
  ElMessage.success('模板已下载')
}

async function submitImport() {
  if (!uploadFile.value) { ElMessage.warning('请选择文件'); return }
  importing.value = true
  try {
    const formData = new FormData()
    formData.append('file', uploadFile.value)
    const res = await request.post('/run-points/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    ElMessage.success(res.message || '导入成功')
    importVisible.value = false
    fileList.value = []
    uploadFile.value = null
    loadPoints()
  } finally {
    importing.value = false
  }
}

async function loadDeptTree() {
  try {
    const data = await request.get('/departments')
    deptTree.value = Array.isArray(data) ? data : []
  } catch {
    deptTree.value = []
  }
}

async function loadPoints() {
  loading.value = true
  try {
    const params: any = { page: page.value, pageSize: pageSize.value }
    if (searchForm.name) params.name = searchForm.name
    if (searchForm.dept_id) params.dept_id = searchForm.dept_id
    if (searchForm.status !== null) params.status = searchForm.status
    const data = await request.get('/run-points', { params })
    points.value = data.list || data || []
    total.value = data.total || 0
  } catch {
    points.value = []
  } finally {
    loading.value = false
  }
}

function resetSearch() {
  searchForm.name = ''
  searchForm.dept_id = null
  searchForm.status = null
  page.value = 1
  loadPoints()
}

function resetForm() {
  form.code = ''
  form.name = ''
  form.nfcUid = ''
  form.dept_id = null
  form.latitude = null
  form.longitude = null
  form.address = ''
}

function openDialog(row?: RunPoint) {
  resetForm()
  editingId.value = row?.id || null
  if (row) {
    dialogTitle.value = '编辑巡检点'
    form.code = row.code
    form.name = row.name
    form.nfcUid = row.nfcUid || ''
    form.dept_id = row.dept_id
    form.latitude = row.latitude
    form.longitude = row.longitude
    form.address = row.address || ''
  } else {
    dialogTitle.value = '新增巡检点'
  }
  dialogVisible.value = true
}

async function submitForm() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    if (editingId.value) {
      await request.put(`/run-points/${editingId.value}`, form)
      ElMessage.success('更新成功')
    } else {
      await request.post('/run-points', form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadPoints()
  } finally {
    submitting.value = false
  }
}

async function handleDelete(row: RunPoint) {
  await ElMessageBox.confirm(`确定删除巡检点"${row.name}"吗？`, '确认', { type: 'warning' })
  await request.delete(`/run-points/${row.id}`)
  ElMessage.success('删除成功')
  loadPoints()
}

function readNfc() {
  ElMessage.info('请在移动端使用 NFC 读取功能绑定标签')
}

onMounted(() => {
  loadDeptTree()
  loadPoints()
})
</script>

<style scoped>
.inspection-points { padding: 16px; }
.search-card { margin-bottom: 16px; }
.table-card { }
.table-header { margin-bottom: 16px; display: flex; gap: 12px; }
.pagination-wrap { margin-top: 16px; display: flex; justify-content: flex-end; }
.text-muted { color: #8892A0; font-size: 12px; }
.import-hint { margin-bottom: 16px; }
</style>