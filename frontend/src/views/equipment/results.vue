<template>
  <div class="check-results-page">
    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="检查任务">
          <el-select v-model="searchForm.taskId" filterable clearable placeholder="选择任务" style="width: 200px" @change="loadData">
            <el-option v-for="t in taskList" :key="t.id" :label="t.task_name" :value="t.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="设备">
          <el-select v-model="searchForm.equipId" filterable clearable placeholder="选择设备" style="width: 200px" @change="loadData">
            <el-option v-for="e in equipList" :key="e.id" :label="`${e.code} - ${e.name}`" :value="e.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="结果">
          <el-select v-model="searchForm.is_normal" clearable placeholder="全部" style="width: 120px" @change="loadData">
            <el-option label="正常" :value="1" />
            <el-option label="异常" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 结果表格 -->
    <el-card>
      <div class="table-header">
        <span class="table-title">检查结果记录</span>
      </div>
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="task_name" label="任务" min-width="140" show-overflow-tooltip />
        <el-table-column prop="equipName" label="设备" min-width="120" show-overflow-tooltip />
        <el-table-column prop="item_name" label="检查项" width="120" />
        <el-table-column label="类型" width="70">
          <template #default="{ row }">{{ typeLabel(row.item_type) }}</template>
        </el-table-column>
        <el-table-column prop="resultValue" label="检查值" min-width="120" show-overflow-tooltip />
        <el-table-column label="结论" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_normal ? 'success' : 'danger'" size="small">{{ row.is_normal ? '正常' : '异常' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="user_name" label="检查人" width="100" />
        <el-table-column label="时间" width="170">
          <template #default="{ row }">{{ formatTime(row.check_time) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="showDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrap">
        <el-pagination v-model:current-page="page" v-model:page-size="pageSize" :total="total" :page-sizes="[10,20,50]" layout="total, sizes, prev, pager, next" @change="loadData" />
      </div>
    </el-card>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="检查结果详情" width="550px">
      <el-descriptions :column="2" border v-if="detailRow">
        <el-descriptions-item label="任务">{{ detailRow.task_name }}</el-descriptions-item>
        <el-descriptions-item label="设备">{{ detailRow.equipName }} ({{ detailRow.equipCode }})</el-descriptions-item>
        <el-descriptions-item label="检查项">{{ detailRow.item_name }}</el-descriptions-item>
        <el-descriptions-item label="类型">{{ typeLabel(detailRow.item_type) }}</el-descriptions-item>
        <el-descriptions-item label="检查值">{{ detailRow.resultValue || '-' }}</el-descriptions-item>
        <el-descriptions-item label="结论">
          <el-tag :type="detailRow.is_normal ? 'success' : 'danger'" size="small">{{ detailRow.is_normal ? '正常' : '异常' }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="检查人">{{ detailRow.user_name }}</el-descriptions-item>
        <el-descriptions-item label="时间">{{ formatTime(detailRow.check_time) }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ detailRow.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
      <div v-if="detailRow?.photoPath" style="margin-top: 12px; text-align: center;">
        <el-image :src="detailRow.photoPath" style="max-width: 100%; max-height: 300px;" fit="contain" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import request from '@/api/http'

const loading = ref(false)
const list = ref<any[]>([]); const total = ref(0); const page = ref(1); const pageSize = ref(20)
const taskList = ref<any[]>([]); const equipList = ref<any[]>([])

const searchForm = reactive({
  taskId: null as number | null,
  equipId: null as number | null,
  is_normal: null as number | null,
})

const detailVisible = ref(false); const detailRow = ref<any>(null)

// ===== 工具函数 =====
function typeLabel(t: string) { return { select: '单选', number: '数值', text: '文本', photo: '拍照' }[t] || t }
function formatTime(t: string | null) {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

// ===== 数据加载 =====
async function loadTasks() {
  try { taskList.value = await request.get('/check-tasks', { params: { pageSize: 9999 } }).then((d: any) => d.list || []) } catch { taskList.value = [] }
}
async function loadEquipments() {
  try { equipList.value = await request.get('/equipments', { params: { pageSize: 9999 } }).then((d: any) => d.list || []) } catch { equipList.value = [] }
}

async function loadData() {
  loading.value = true
  try {
    const params: any = { page: page.value, pageSize: pageSize.value }
    if (searchForm.taskId) params.taskId = searchForm.taskId
    if (searchForm.equipId) params.equipId = searchForm.equipId
    if (searchForm.is_normal !== null) params.is_normal = searchForm.is_normal
    const data = await request.get('/check-results', { params })
    list.value = data.list || []
    total.value = data.total || 0
  } finally { loading.value = false }
}

function resetSearch() {
  searchForm.taskId = null; searchForm.equipId = null; searchForm.is_normal = null
  page.value = 1; loadData()
}

function showDetail(row: any) {
  detailRow.value = row; detailVisible.value = true
}

onMounted(() => {
  loadTasks()
  loadEquipments()
  loadData()
})
</script>

<style scoped>
.check-results-page { padding: 16px; }
.search-card { margin-bottom: 16px; }
.table-header { margin-bottom: 16px; }
.table-title { font-size: 15px; font-weight: 600; color: #cfd8dc; }
.pagination-wrap { margin-top: 16px; display: flex; justify-content: flex-end; }
</style>
