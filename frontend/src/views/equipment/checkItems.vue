<template>
  <div class="check-items">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>检查项管理</span>
          <el-button @click="$router.back()" size="small">返回设备列表</el-button>
        </div>
      </template>
      <el-table :data="items" v-loading="loading" stripe>
        <el-table-column prop="item_name" label="检查项名称" min-width="160" />
        <el-table-column label="类型" width="100"><template #default="{ row }">{{ typeLabel(row.item_type) }}</template></el-table-column>
        <el-table-column label="必填" width="60"><template #default="{ row }">{{ row.required ? '是' : '否' }}</template></el-table-column>
        <el-table-column label="正常范围" width="180">
          <template #default="{ row }">
            <span v-if="row.item_type === 'number'">{{ row.normalMin || '-' }} ~ {{ row.normalMax || '-' }} {{ row.unit || '' }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="add-row" style="margin-top: 16px; display: flex; gap: 8px">
        <el-input v-model="new_itemName" placeholder="检查项名称" style="width: 200px" />
        <el-select v-model="new_itemType" placeholder="类型" style="width: 120px">
          <el-option label="单选" value="select" />
          <el-option label="数值" value="number" />
          <el-option label="文本" value="text" />
          <el-option label="拍照" value="photo" />
        </el-select>
        <el-button type="primary" @click="addItem">添加</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRoute } from 'vue-router'
import request from '@/api/http'

const route = useRoute()
const equipId = ref(Number(route.params.id) || 0)
const loading = ref(false); const items = ref<any[]>([])
const new_itemName = ref(''); const new_itemType = ref('number')

function typeLabel(t: string) { return { select: '单选', number: '数值', text: '文本', photo: '拍照' }[t] || t }

async function loadData() {
  if (!equipId.value) return
  loading.value = true
  try {
    items.value = await request.get(`/equipments/${equipId.value}/check-items`) || []
  } finally { loading.value = false }
}
async function addItem() {
  if (!new_itemName.value) { ElMessage.warning('请输入检查项名称'); return }
  await request.post(`/equipments/${equipId.value}/check-items`, { item_name: new_itemName.value, item_type: new_itemType.value })
  ElMessage.success('添加成功')
  new_itemName.value = ''; loadData()
}
async function handleDelete(row: any) {
  await ElMessageBox.confirm('确定删除该检查项？', '确认', { type: 'warning' })
  await request.delete(`/equipments/${equipId.value}/check-items/${row.id}`)
  ElMessage.success('删除成功'); loadData()
}

onMounted(() => { loadData() })
</script>
<style scoped>
.check-items { padding: 16px; }
</style>