<template>
  <div class="role-page">
    <el-card>
      <div class="table-header"><el-button type="primary" @click="openDialog()"><el-icon><Plus /></el-icon>新增角色</el-button></div>
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="role_name" label="角色名称" min-width="150" />
        <el-table-column prop="role_code" label="角色编码" width="150" />
        <el-table-column prop="description" label="描述" min-width="250" show-overflow-tooltip />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }"><el-button link type="primary" @click="openDialog(row)">编辑</el-button><el-button link type="danger" @click="handleDelete(row)">删除</el-button></template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="角色名称" prop="role_name"><el-input v-model="form.role_name" /></el-form-item>
        <el-form-item label="角色编码" prop="role_code"><el-input v-model="form.role_code" :disabled="!!editingId" placeholder="如 admin/inspector" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" :rows="3" /></el-form-item>
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

const loading = ref(false); const submitting = ref(false); const list = ref<any[]>([])
const dialogVisible = ref(false); const dialogTitle = ref(''); const editingId = ref<number | null>(null)
const formRef = ref()
const form = reactive({ role_name: '', role_code: '', description: '' })
const rules = { role_name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }], role_code: [{ required: true, message: '请输入角色编码', trigger: 'blur' }] }

async function loadData() { loading.value = true; try { list.value = await request.get('/roles') || [] } finally { loading.value = false } }
function resetForm() { form.role_name = ''; form.role_code = ''; form.description = '' }
function openDialog(row?: any) {
  resetForm(); editingId.value = row?.id || null
  if (row) { dialogTitle.value = '编辑角色'; form.role_name = row.role_name; form.role_code = row.role_code; form.description = row.description || '' }
  else { dialogTitle.value = '新增角色' }
  dialogVisible.value = true
}
async function submitForm() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return; submitting.value = true
  try {
    if (editingId.value) { await request.put(`/roles/${editingId.value}`, form); ElMessage.success('更新成功') }
    else { await request.post('/roles', form); ElMessage.success('创建成功') }
    dialogVisible.value = false; loadData()
  } finally { submitting.value = false }
}
async function handleDelete(row: any) {
  await ElMessageBox.confirm(`确定删除角色"${row.role_name}"吗？`, '确认', { type: 'warning' })
  await request.delete(`/roles/${row.id}`); ElMessage.success('删除成功'); loadData()
}

onMounted(() => { loadData() })
</script>
<style scoped>
.role-page { padding: 16px; }
.table-header { margin-bottom: 16px; }
</style>
