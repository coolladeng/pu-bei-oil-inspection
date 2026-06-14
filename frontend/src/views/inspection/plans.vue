<template>
  <div class="plans-page">
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="月份">
          <el-date-picker v-model="searchForm.month" type="month" placeholder="选择月份" value-format="YYYYMM" style="width: 160px" />
        </el-form-item>
        <el-form-item label="班组">
          <el-tree-select v-model="searchForm.dept_id" :data="deptTree" :props="{ label: 'name', value: 'id', children: 'children' }" placeholder="选择班组" clearable filterable style="width: 200px" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部" clearable style="width: 120px">
            <el-option label="待执行" :value="0" />
            <el-option label="已执行" :value="1" />
            <el-option label="超时" :value="2" />
            <el-option label="漏检" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadPlans">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card">
      <div class="table-header">
        <el-button type="primary" @click="generateMonthly">
          <el-icon><Calendar /></el-icon>生成月度计划
        </el-button>
      </div>
      <el-table :data="plans" v-loading="loading" stripe>
        <el-table-column prop="plan_date" label="计划日期" width="120" />
        <el-table-column prop="point_name" label="巡检点" min-width="140" />
        <el-table-column prop="dept_name" label="班组" width="140" />
        <el-table-column label="班次" width="80">
          <template #default="{ row }">
            <el-tag size="small">{{ shiftLabel(row.shift_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="planStatusTag(row.status)" size="small">{{ planStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewDetail(row)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrap">
        <el-pagination v-model:current-page="page" v-model:page-size="pageSize" :total="total" :page-sizes="[10,20,50]" layout="total, sizes, prev, pager, next" @change="loadPlans" />
      </div>
    </el-card>

    <!-- 计划详情弹窗 -->
    <el-dialog v-model="detailVisible" title="巡检计划详情" width="650px">
      <el-descriptions v-if="detail" :column="2" border>
        <el-descriptions-item label="计划日期">{{ detail.plan_date }}</el-descriptions-item>
        <el-descriptions-item label="班次">
          <el-tag size="small">{{ shiftLabel(detail.shift_type) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="巡检点">{{ detail.point_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="巡检点编号">{{ detail.pointCode || '-' }}</el-descriptions-item>
        <el-descriptions-item label="所属班组">{{ detail.dept_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="planStatusTag(detail.status)" size="small">{{ planStatusLabel(detail.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="检查时间窗">{{ detail.timeWindowStart || '-' }} ~ {{ detail.timeWindowEnd || '-' }}</el-descriptions-item>
        <el-descriptions-item label="NFC UID">{{ detail.nfc_uid || '未绑定' }}</el-descriptions-item>
      </el-descriptions>
      <el-divider content-position="left">相关巡检记录</el-divider>
      <el-table :data="detailRecords" v-loading="recordsLoading" size="small" max-height="240">
        <el-table-column prop="check_time" label="检查时间" width="160" />
        <el-table-column prop="user_name" label="执行人" width="100" />
        <el-table-column prop="status" label="结果" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'normal' ? 'success' : 'danger'" size="small">{{ row.status === 'normal' ? '正常' : '异常' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="140" show-overflow-tooltip />
      </el-table>
      <div v-if="!recordsLoading && detailRecords.length === 0" style="text-align: center; color: #8892A0; padding: 16px;">暂无巡检记录</div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { Calendar } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import request from '@/api/http'

const loading = ref(false); const plans = ref<any[]>([])
const page = ref(1); const pageSize = ref(20); const total = ref(0)
const deptTree = ref<any[]>([])
const searchForm = reactive({ month: '', dept_id: null as number | null, status: null as number | null })

const detailVisible = ref(false); const detail = ref<any>(null)
const detailRecords = ref<any[]>([]); const recordsLoading = ref(false)

function shiftLabel(s: string) { return { day: '白班', mid: '中班', night: '夜班', full: '24h' }[s] || s }
function planStatusTag(s: number) { return ['info', 'success', 'danger', 'warning'][s] || 'info' }
function planStatusLabel(s: number) { return ['待执行', '已执行', '超时', '漏检'][s] || '未知' }

async function loadDeptTree() {
  const data = await request.get('/departments')
  deptTree.value = Array.isArray(data) ? data : []
}
async function loadPlans() {
  loading.value = true
  try {
    const params: any = { page: page.value, pageSize: pageSize.value }
    if (searchForm.month) params.month = searchForm.month
    if (searchForm.dept_id) params.dept_id = searchForm.dept_id
    if (searchForm.status !== null) params.status = searchForm.status
    const data = await request.get('/run-plans', { params })
    plans.value = data.list || data || []
    total.value = data.total || 0
  } finally { loading.value = false }
}
function resetSearch() { searchForm.month = ''; searchForm.dept_id = null; searchForm.status = null; page.value = 1; loadPlans() }
async function generateMonthly() {
  try {
    await request.post('/run-plans/generate-monthly', { yearMonth: searchForm.month || undefined })
    ElMessage.success('月度计划生成成功')
    loadPlans()
  } catch { }
}
async function viewDetail(row: any) {
  detailVisible.value = true
  detailRecords.value = []
  recordsLoading.value = true
  try {
    const [planData, records] = await Promise.all([
      request.get(`/run-plans/${row.id}`),
      request.get('/run-records', { params: { plan_id: row.id } })
    ])
    detail.value = {
      ...planData,
      plan_date: row.plan_date,
      shift_type: row.shift_type,
      status: row.status,
      point_name: row.point_name,
      dept_name: row.dept_name,
    }
    detailRecords.value = records.list || records || []
  } catch {
    detail.value = row
  } finally {
    recordsLoading.value = false
  }
}

onMounted(() => { loadDeptTree(); loadPlans() })
</script>
<style scoped>
.plans-page { padding: 16px; }
.search-card { margin-bottom: 16px; }
.table-header { margin-bottom: 16px; }
.pagination-wrap { margin-top: 16px; display: flex; justify-content: flex-end; }
</style>