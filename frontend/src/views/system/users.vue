<template>
  <div class="user-page">
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="用户名"><el-input v-model="searchForm.username" placeholder="搜索" clearable /></el-form-item>
        <el-form-item label="部门"><el-tree-select v-model="searchForm.dept_id" :data="deptTree" :props="{ label: 'name', value: 'id', children: 'children' }" placeholder="选择部门" clearable filterable style="width: 200px" /></el-form-item>
        <el-form-item><el-button type="primary" @click="loadData">查询</el-button><el-button @click="resetSearch">重置</el-button></el-form-item>
      </el-form>
    </el-card>
    <el-card>
      <div class="table-header"><el-button type="primary" @click="openDialog()"><el-icon><Plus /></el-icon>新增用户</el-button></div>
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="real_name" label="真实姓名" width="120" />
        <el-table-column prop="employee_no" label="工号" width="100" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="dept_name" label="部门" width="140" />
        <el-table-column label="角色" min-width="150">
          <template #default="{ row }"><el-tag v-for="r in (row.roles || [])" :key="r" size="small" style="margin-right: 4px">{{ r }}</el-tag></template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }"><el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">{{ row.status === 1 ? '正常' : '停用' }}</el-tag></template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }"><el-button link type="primary" @click="openDialog(row)">编辑</el-button><el-button link type="danger" @click="handleDelete(row)">删除</el-button></template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrap"><el-pagination v-model:current-page="page" v-model:page-size="pageSize" :total="total" :page-sizes="[10,20,50]" layout="total, sizes, prev, pager, next" @change="loadData" /></div>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="550px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="用户名" prop="username"><el-input v-model="form.username" :disabled="!!editingId" /></el-form-item>
        <el-form-item label="真实姓名" prop="real_name"><el-input v-model="form.real_name" /></el-form-item>
        <el-form-item label="密码" :prop="editingId ? '' : 'password'"><el-input v-model="form.password" type="password" show-password :placeholder="editingId ? '留空则不修改' : '请输入密码'" /></el-form-item>
        <el-form-item label="手机号"><el-input v-model="form.phone" /></el-form-item>
        <el-form-item label="所属部门"><el-tree-select v-model="form.dept_id" :data="deptTree" :props="{ label: 'name', value: 'id', children: 'children' }" placeholder="选择部门" filterable style="width: 100%" /></el-form-item>
        <el-form-item label="角色"><el-select v-model="form.role_ids" multiple placeholder="选择角色" style="width: 100%"><el-option v-for="r in roleList" :key="r.id" :label="r.role_name" :value="r.id" /></el-select></el-form-item>
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
const list = ref<any[]>([]); const page = ref(1); const pageSize = ref(20); const total = ref(0)
const deptTree = ref<any[]>([]); const roleList = ref<any[]>([])
const searchForm = reactive({ username: '', dept_id: null as number | null })
const dialogVisible = ref(false); const dialogTitle = ref(''); const editingId = ref<number | null>(null)
const formRef = ref()
const form = reactive({ username: '', real_name: '', password: '', phone: '', dept_id: null as number | null, role_ids: [] as number[] })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  real_name: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }],
}

async function loadDeptTree() { const data = await request.get('/departments'); deptTree.value = Array.isArray(data) ? data : [] }
async function loadRoles() { try { roleList.value = await request.get('/roles') || [] } catch { roleList.value = [] } }
async function loadData() {
  loading.value = true
  try {
    const params: any = { page: page.value, pageSize: pageSize.value }
    if (searchForm.username) params.username = searchForm.username
    if (searchForm.dept_id) params.dept_id = searchForm.dept_id
    const data = await request.get('/users', { params })
    list.value = data.list || data || []; total.value = data.total || 0
  } finally { loading.value = false }
}
function resetSearch() { searchForm.username = ''; searchForm.dept_id = null; page.value = 1; loadData() }
function resetForm() { form.username = ''; form.real_name = ''; form.password = ''; form.phone = ''; form.dept_id = null; form.role_ids = [] }
function openDialog(row?: any) {
  resetForm(); editingId.value = row?.id || null
  if (row) { dialogTitle.value = '编辑用户'; form.username = row.username; form.real_name = row.real_name; form.phone = row.phone || ''; form.dept_id = row.dept_id }
  else { dialogTitle.value = '新增用户' }
  dialogVisible.value = true
}
async function submitForm() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return; submitting.value = true
  try {
    const payload = { ...form }
    if (editingId.value && !payload.password) delete payload.password
    if (editingId.value) { await request.put(`/users/${editingId.value}`, payload); ElMessage.success('更新成功') }
    else { await request.post('/users', payload); ElMessage.success('创建成功') }
    dialogVisible.value = false; loadData()
  } finally { submitting.value = false }
}
async function handleDelete(row: any) {
  await ElMessageBox.confirm(`确定删除用户"${row.real_name}"吗？`, '确认', { type: 'warning' })
  await request.delete(`/users/${row.id}`); ElMessage.success('删除成功'); loadData()
}

onMounted(() => { loadDeptTree(); loadRoles(); loadData() })
</script>
<style scoped>
.user-page { padding: 16px; }
.search-card { margin-bottom: 16px; }
.table-header { margin-bottom: 16px; }
.pagination-wrap { margin-top: 16px; display: flex; justify-content: flex-end; }
</style>
