<template>
  <div class="equipment-list">
    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="设备名称">
          <el-input v-model="searchForm.name" placeholder="请输入" clearable @keyup.enter="loadData" />
        </el-form-item>
        <el-form-item label="设备编号">
          <el-input v-model="searchForm.code" placeholder="请输入" clearable @keyup.enter="loadData" />
        </el-form-item>
        <el-form-item label="所属部门">
          <el-tree-select v-model="searchForm.dept_id" :data="deptTree" :props="{ label: 'name', value: 'id', children: 'children' }" placeholder="选择部门" clearable filterable style="width: 200px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 设备表格 -->
    <el-card class="table-card">
      <div class="table-header">
        <el-button type="primary" @click="openDialog()"><el-icon><Plus /></el-icon>新增设备</el-button>
        <el-button @click="importVisible = true"><el-icon><Upload /></el-icon>Excel导入</el-button>
        <el-button link type="primary" @click="downloadTemplate">下载模板</el-button>
      </div>
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="code" label="编号" width="120" />
        <el-table-column prop="name" label="名称" min-width="150" />
        <el-table-column prop="model_no" label="型号" width="140" />
        <el-table-column prop="dept_name" label="所属部门" width="140" />
        <el-table-column prop="location" label="位置" min-width="160" show-overflow-tooltip />
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
            <el-button link type="primary" @click="manageCheckItems(row)">检查项</el-button>
            <el-button link type="primary" @click="showQRCode(row)">二维码</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrap">
        <el-pagination v-model:current-page="page" v-model:page-size="pageSize" :total="total" :page-sizes="[10,20,50]" layout="total, sizes, prev, pager, next" @change="loadData" />
      </div>
    </el-card>

    <!-- 设备编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="设备编号" prop="code"><el-input v-model="form.code" placeholder="如 EQ-001" :disabled="!!editingId" /></el-form-item>
        <el-form-item label="设备名称" prop="name"><el-input v-model="form.name" placeholder="如 离心泵" /></el-form-item>
        <el-form-item label="型号"><el-input v-model="form.model_no" placeholder="如 IS80-65-160" /></el-form-item>
        <el-form-item label="生产厂家"><el-input v-model="form.manufacturer" placeholder="如 大庆油田装备" /></el-form-item>
        <el-form-item label="所属部门" prop="dept_id">
          <el-tree-select v-model="form.dept_id" :data="deptTree" :props="{ label: 'name', value: 'id', children: 'children' }" placeholder="选择部门" filterable style="width: 100%" />
        </el-form-item>
        <el-form-item label="安装位置"><el-input v-model="form.location" placeholder="如 1号联合站" /></el-form-item>
        <el-form-item label="设备类别"><el-input v-model="form.category" placeholder="如 泵类" /></el-form-item>
        <el-form-item label="状态" v-if="editingId">
          <el-radio-group v-model="form.status">
            <el-radio :value="1">正常</el-radio>
            <el-radio :value="2">维修中</el-radio>
            <el-radio :value="3">报废</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 检查项管理弹窗 -->
    <el-dialog v-model="checkItemVisible" :title="`检查项管理 - ${checkEquipName}`" width="750px" destroy-on-close>
      <el-table :data="checkItems" v-loading="checkLoading" max-height="400" stripe>
        <el-table-column prop="item_name" label="检查项名称" min-width="160" />
        <el-table-column label="类型" width="80">
          <template #default="{ row }">{{ typeLabel(row.item_type) }}</template>
        </el-table-column>
        <el-table-column label="必填" width="60">
          <template #default="{ row }">{{ row.required ? '是' : '否' }}</template>
        </el-table-column>
        <el-table-column label="正常范围/选项" min-width="180">
          <template #default="{ row }">
            <template v-if="row.item_type === 'number'">
              {{ row.normalMin ?? '-' }} ~ {{ row.normalMax ?? '-' }} {{ row.unit ?? '' }}
            </template>
            <template v-else-if="row.item_type === 'select'">
              {{ formatOptions(row.options) }}
            </template>
            <template v-else>-</template>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="editCheckItem(row)">编辑</el-button>
            <el-button link type="danger" @click="deleteCheckItem(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div style="margin-top: 16px; padding-top: 16px; border-top: 1px solid #eee;">
        <el-form :model="checkForm" inline label-width="80px">
          <el-form-item label="检查项名">
            <el-input v-model="checkForm.item_name" placeholder="如 运行温度" style="width: 160px" />
          </el-form-item>
          <el-form-item label="类型">
            <el-select v-model="checkForm.item_type" style="width: 100px" @change="onCheckTypeChange">
              <el-option label="单选" value="select" />
              <el-option label="数值" value="number" />
              <el-option label="文本" value="text" />
              <el-option label="拍照" value="photo" />
            </el-select>
          </el-form-item>
          <el-form-item label="必填">
            <el-switch v-model="checkForm.requiredBool" />
          </el-form-item>
          <el-form-item label="排序">
            <el-input-number v-model="checkForm.sort_order" :min="0" :max="99" style="width: 80px" />
          </el-form-item>
        </el-form>

        <!-- 数值类型额外配置 -->
        <el-form v-if="checkForm.item_type === 'number'" :model="checkForm" inline label-width="80px" style="margin-top: 8px;">
          <el-form-item label="正常下限">
            <el-input-number v-model="checkForm.normalMin" :precision="1" style="width: 120px" />
          </el-form-item>
          <el-form-item label="正常上限">
            <el-input-number v-model="checkForm.normalMax" :precision="1" style="width: 120px" />
          </el-form-item>
          <el-form-item label="单位">
            <el-input v-model="checkForm.unit" placeholder="如 ℃" style="width: 80px" />
          </el-form-item>
        </el-form>

        <!-- 单选类型额外配置 -->
        <div v-if="checkForm.item_type === 'select'" style="margin-top: 8px;">
          <el-form label-width="80px">
            <el-form-item label="选项配置">
              <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: center;">
                <template v-for="(opt, idx) in selectOptions" :key="idx">
                  <el-input v-model="opt.label" placeholder="显示名" style="width: 80px" size="small" />
                  <el-input v-model="opt.value" placeholder="值" style="width: 80px" size="small" />
                  <el-button link type="danger" size="small" @click="selectOptions.splice(idx, 1)"><el-icon><Delete /></el-icon></el-button>
                </template>
                <el-button size="small" @click="selectOptions.push({ label: '', value: '' })"><el-icon><Plus /></el-icon>添加选项</el-button>
              </div>
            </el-form-item>
          </el-form>
        </div>

        <div style="margin-top: 12px;">
          <el-button type="primary" @click="submitCheckItem" :loading="checkSubmitting">
            {{ checkEditingId ? '保存修改' : '添加检查项' }}
          </el-button>
          <el-button v-if="checkEditingId" @click="cancelEditCheckItem">取消编辑</el-button>
        </div>
      </div>
    </el-dialog>

    <!-- Excel导入弹窗 -->
    <el-dialog v-model="importVisible" title="Excel批量导入设备" width="500px" destroy-on-close>
      <el-alert type="info" :closable="false" show-icon style="margin-bottom: 16px;">
        <template #title>表头：编号、名称、型号、生产厂家、所属部门、安装位置、设备类别</template>
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

    <!-- 二维码弹窗 -->
    <el-dialog v-model="qrVisible" :title="`设备二维码 - ${qrEquipName}`" width="480px" destroy-on-close>
      <div style="text-align: center;" v-loading="qrLoading">
        <canvas ref="qrCanvas" style="width: 280px; height: 280px;" />
        <p style="margin-top: 8px; color: #999; font-size: 13px;">编号: {{ qrEquipCode }}</p>
      </div>
      <template #footer>
        <el-button @click="qrVisible = false">关闭</el-button>
        <el-button type="primary" @click="printQRCode">打印</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick, computed } from 'vue'
import { Plus, Upload, UploadFilled, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/api/http'

// ===== 状态 =====
const loading = ref(false); const submitting = ref(false)
const list = ref<any[]>([]); const total = ref(0); const page = ref(1); const pageSize = ref(20)
const deptTree = ref<any[]>([])

const searchForm = reactive({ name: '', code: '', dept_id: null as number | null })

// 编辑弹窗
const dialogVisible = ref(false); const editingId = ref<number | null>(null)
const dialogTitle = computed(() => editingId.value ? '编辑设备' : '新增设备')
const formRef = ref()
const form = reactive({
  code: '', name: '', dept_id: null as number | null,
  model_no: '', manufacturer: '', location: '', category: '', status: 1,
})
const rules = {
  code: [{ required: true, message: '请输入设备编号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入设备名称', trigger: 'blur' }],
  dept_id: [{ required: true, message: '请选择所属部门', trigger: 'change' }],
}

// 检查项管理
const checkItemVisible = ref(false); const checkLoading = ref(false); const checkSubmitting = ref(false)
const checkEquipId = ref<number | null>(null); const checkEquipName = ref('')
const checkItems = ref<any[]>([])
const checkEditingId = ref<number | null>(null)
const checkForm = reactive({
  item_name: '', item_type: 'number', requiredBool: true, sort_order: 0,
  normalMin: null as number | null, normalMax: null as number | null, unit: '',
})
const selectOptions = ref<{ label: string; value: string }[]>([])

// 导入
const importVisible = ref(false); const importing = ref(false)
const uploadRef = ref(); const fileList = ref<any[]>([]); const importFile = ref<File | null>(null)

// 二维码
const qrVisible = ref(false); const qrLoading = ref(false)
const qrEquipName = ref(''); const qrEquipCode = ref('')
const qrCanvas = ref<HTMLCanvasElement>()

// ===== 工具函数 =====
function statusTag(s: number) { return { 1: 'success', 2: 'warning', 3: 'danger' }[s] || 'info' }
function statusLabel(s: number) { return { 1: '正常', 2: '维修中', 3: '报废' }[s] || '未知' }
function typeLabel(t: string) { return { select: '单选', number: '数值', text: '文本', photo: '拍照' }[t] || t }
function formatOptions(opt: string | null) {
  if (!opt) return '-'
  try { return JSON.parse(opt).map((o: any) => o.label).join(', ') } catch { return opt }
}

// ===== 数据加载 =====
async function loadDeptTree() {
  const data = await request.get('/departments')
  deptTree.value = Array.isArray(data) ? data : []
}
async function loadData() {
  loading.value = true
  try {
    const params: any = { page: page.value, pageSize: pageSize.value }
    if (searchForm.name) params.name = searchForm.name
    if (searchForm.code) params.code = searchForm.code
    if (searchForm.dept_id) params.dept_id = searchForm.dept_id
    const data = await request.get('/equipments', { params })
    list.value = data.list || []
    total.value = data.total || 0
  } finally { loading.value = false }
}
function resetSearch() { searchForm.name = ''; searchForm.code = ''; searchForm.dept_id = null; page.value = 1; loadData() }

// ===== 设备CRUD =====
function resetForm() {
  form.code = ''; form.name = ''; form.dept_id = null
  form.model_no = ''; form.manufacturer = ''; form.location = ''; form.category = ''; form.status = 1
}
function openDialog(row?: any) {
  resetForm(); editingId.value = row?.id || null
  if (row) {
    form.code = row.code; form.name = row.name; form.dept_id = row.dept_id
    form.model_no = row.model_no || ''; form.manufacturer = row.manufacturer || ''
    form.location = row.location || ''; form.category = row.category || ''
    form.status = row.status ?? 1
  }
  dialogVisible.value = true
}
async function submitForm() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return; submitting.value = true
  try {
    const payload = { ...form }
    if (editingId.value) {
      await request.put(`/equipments/${editingId.value}`, payload)
      ElMessage.success('更新成功')
    } else {
      await request.post('/equipments', payload)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false; loadData()
  } finally { submitting.value = false }
}
async function handleDelete(row: any) {
  await ElMessageBox.confirm(`确定删除"${row.name}"吗？`, '确认', { type: 'warning' })
  await request.delete(`/equipments/${row.id}`); ElMessage.success('删除成功'); loadData()
}

// ===== 检查项管理 =====
async function manageCheckItems(row: any) {
  checkEquipId.value = row.id; checkEquipName.value = row.name
  checkItemVisible.value = true
  await loadCheckItems()
}
async function loadCheckItems() {
  if (!checkEquipId.value) return
  checkLoading.value = true
  try {
    checkItems.value = await request.get(`/equipments/${checkEquipId.value}/check-items`) || []
  } finally { checkLoading.value = false }
}
function resetCheckForm() {
  checkForm.item_name = ''; checkForm.item_type = 'number'; checkForm.requiredBool = true
  checkForm.sort_order = 0; checkForm.normalMin = null; checkForm.normalMax = null; checkForm.unit = ''
  selectOptions.value = []
  checkEditingId.value = null
}
function onCheckTypeChange() {
  selectOptions.value = checkForm.item_type === 'select' ? [{ label: '正常', value: 'normal' }, { label: '异常', value: 'abnormal' }] : []
  checkForm.normalMin = null; checkForm.normalMax = null; checkForm.unit = ''
}
function editCheckItem(row: any) {
  checkEditingId.value = row.id
  checkForm.item_name = row.item_name
  checkForm.item_type = row.item_type
  checkForm.requiredBool = row.required === 1
  checkForm.sort_order = row.sort_order || 0
  checkForm.normalMin = row.normalMin ?? null
  checkForm.normalMax = row.normalMax ?? null
  checkForm.unit = row.unit || ''
  if (row.item_type === 'select' && row.options) {
    try { selectOptions.value = JSON.parse(row.options) } catch { selectOptions.value = [] }
  } else {
    selectOptions.value = []
  }
}
function cancelEditCheckItem() { resetCheckForm() }
async function submitCheckItem() {
  if (!checkForm.item_name) { ElMessage.warning('请输入检查项名称'); return }
  const payload: any = {
    item_name: checkForm.item_name,
    item_type: checkForm.item_type,
    required: checkForm.requiredBool ? 1 : 0,
    sort_order: checkForm.sort_order,
  }
  if (checkForm.item_type === 'number') {
    payload.normalMin = checkForm.normalMin
    payload.normalMax = checkForm.normalMax
    payload.unit = checkForm.unit
  }
  if (checkForm.item_type === 'select') {
    const valid = selectOptions.value.filter(o => o.label && o.value)
    if (valid.length === 0) { ElMessage.warning('请至少配置一个有效选项'); return }
    payload.options = JSON.stringify(valid)
  }
  checkSubmitting.value = true
  try {
    if (checkEditingId.value) {
      await request.put(`/equipments/${checkEquipId.value}/check-items/${checkEditingId.value}`, payload)
      ElMessage.success('修改成功')
    } else {
      await request.post(`/equipments/${checkEquipId.value}/check-items`, payload)
      ElMessage.success('添加成功')
    }
    resetCheckForm()
    await loadCheckItems()
  } finally { checkSubmitting.value = false }
}
async function deleteCheckItem(row: any) {
  await ElMessageBox.confirm('确定删除该检查项？', '确认', { type: 'warning' })
  await request.delete(`/equipments/${checkEquipId.value}/check-items/${row.id}`)
  ElMessage.success('删除成功'); loadCheckItems()
}

// ===== Excel导入 =====
function handleFileChange(file: any) { importFile.value = file.raw }
async function doImport() {
  if (!importFile.value) { ElMessage.warning('请选择文件'); return }
  importing.value = true
  try {
    const fd = new FormData(); fd.append('file', importFile.value)
    const res = await request.post('/equipments/import', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    ElMessage.success(res.message || '导入完成')
    importVisible.value = false; fileList.value = []; importFile.value = null
    loadData()
  } finally { importing.value = false }
}
async function downloadTemplate() {
  const res = await request.get('/equipments/template', { responseType: 'blob' })
  const url = URL.createObjectURL(new Blob([res]))
  const a = document.createElement('a'); a.href = url; a.download = 'equipment_template.xlsx'
  a.click(); URL.revokeObjectURL(url)
}

// ===== 二维码 =====
async function showQRCode(row: any) {
  qrVisible.value = true; qrLoading.value = true
  qrEquipName.value = row.name; qrEquipCode.value = row.code
  try {
    const data = await request.get(`/equipments/${row.id}/qrcode`)
    const qrUrl = data.qrcode || `equip://${row.id}?code=${row.code}`
    await nextTick()
    if (qrCanvas.value) {
      const { default: QRCode } = await import('qrcode')
      await QRCode.toCanvas(qrCanvas.value, qrUrl, { width: 280, margin: 2, color: { dark: '#000', light: '#FFF' } })
    }
  } finally { qrLoading.value = false }
}
function printQRCode() {
  if (!qrCanvas.value) return
  const win = window.open('', '_blank', 'width=400,height=500')
  if (!win) return
  const img = qrCanvas.value.toDataURL('image/png')
  win.document.write(`<html><head><title>设备二维码 - ${qrEquipName.value}</title></head><body style="text-align:center;font-family:sans-serif;padding:20px;"><h3>${qrEquipName.value}</h3><p>编号: ${qrEquipCode.value}</p><img src="${img}" style="width:280px;height:280px;" /><script>window.onload=function(){window.print();}<\/script></body></html>`)
  win.document.close()
}

onMounted(() => { loadDeptTree(); loadData() })
</script>

<style scoped>
.equipment-list { padding: 16px; }
.search-card { margin-bottom: 16px; }
.table-header { margin-bottom: 16px; display: flex; gap: 12px; }
.pagination-wrap { margin-top: 16px; display: flex; justify-content: flex-end; }
</style>
