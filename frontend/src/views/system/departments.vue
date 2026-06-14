<template>
  <div class="dept-page">
    <el-card>
      <div class="table-header">
        <el-button type="primary" @click="openDialog()"><el-icon><Plus /></el-icon>新增机构</el-button>
      </div>
      <el-table :data="deptList" v-loading="loading" row-key="id" default-expand-all :tree-props="{ children: 'children' }" stripe>
        <el-table-column prop="name" label="单位名称" min-width="200" />
        <el-table-column label="级别" width="100">
          <template #default="{ row }"><el-tag size="small">{{ levelLabel(row.level) }}</el-tag></template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }"><el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">{{ row.status === 1 ? '正常' : '停用' }}</el-tag></template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="单位名称" prop="name"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="上级部门">
          <el-tree-select v-model="form.parent_id" :data="deptList" :props="{ label: 'name', value: 'id', children: 'children' }" placeholder="顶级机构(储运销售分公司)" clearable filterable style="width: 100%" />
        </el-form-item>
        <el-form-item label="级别" prop="level">
          <el-select v-model="form.level" placeholder="选择级别" style="width: 100%">
            <el-option label="储运销售分公司" :value="1" />
            <el-option label="大队" :value="2" />
            <el-option label="班组" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="排序"><el-input-number v-model="form.sort_order" :min="0" style="width: 100%" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/api/http'

const loading = ref(false); const submitting = ref(false)
const deptList = ref<any[]>([])
const dialogVisible = ref(false); const dialogTitle = ref(''); const editingId = ref<number | null>(null)
const formRef = ref()
const form = reactive({ name: '', parent_id: null as number | null, level: 1, sort_order: 0 })
const rules = { name: [{ required: true, message: '请输入单位名称', trigger: 'blur' }], level: [{ required: true, message: '请选择级别', trigger: 'change' }] }

function levelLabel(l: number) { return { 1: '储运销售分公司', 2: '大队', 3: '班组' }[l] || '' }

async function loadData() {
  loading.value = true
  try {
    const data = await request.get('/departments')
    deptList.value = Array.isArray(data) ? data : []
  } finally { loading.value = false }
}
function resetForm() { form.name = ''; form.parent_id = null; form.level = 99; form.sort_order = 0 }
function openDialog(row?: any) {
  resetForm(); editingId.value = row?.id || null
  if (row) { dialogTitle.value = '编辑机构'; form.name = row.name; form.parent_id = row.parent_id; form.level = row.level; form.sort_order = row.sort_order }
  else { dialogTitle.value = '新增机构'; form.level = 2 }
  dialogVisible.value = true
}
async function submitForm() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return; submitting.value = true
  try {
    if (editingId.value) { await request.put(`/departments/${editingId.value}`, form); ElMessage.success('更新成功') }
    else { await request.post('/departments', form); ElMessage.success('创建成功') }
    dialogVisible.value = false; loadData()
  } finally { submitting.value = false }
}
async function handleDelete(row: any) {
  await ElMessageBox.confirm(`确定删除"${row.name}"吗？`, '确认', { type: 'warning' })
  await request.delete(`/departments/${row.id}`); ElMessage.success('删除成功'); loadData()
}

onMounted(() => { loadData() })
</script>
<style scoped>
.dept-page { padding: 16px; }
.table-header { margin-bottom: 16px; }
</style>
