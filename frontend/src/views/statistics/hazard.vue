<template>
  <div class="stats-page">
    <!-- 概要卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="6"><el-card shadow="hover"><div class="stat-item"><div class="stat-label">隐患总数</div><div class="stat-value" style="color:#409EFF">{{ overview.total || 0 }}</div></div></el-card></el-col>
      <el-col :span="6"><el-card shadow="hover"><div class="stat-item"><div class="stat-label">待审核</div><div class="stat-value" style="color:#E6A23C">{{ overview.reported || 0 }}</div></div></el-card></el-col>
      <el-col :span="6"><el-card shadow="hover"><div class="stat-item"><div class="stat-label">处理中</div><div class="stat-value" style="color:#00D4FF">{{ overview.handling || 0 }}</div></div></el-card></el-col>
      <el-col :span="6"><el-card shadow="hover"><div class="stat-item"><div class="stat-label">已关闭</div><div class="stat-value" style="color:#00E676">{{ overview.closed || 0 }}</div></div></el-card></el-col>
    </el-row>

    <!-- 图表区 -->
    <el-row :gutter="16" style="margin-top: 16px;">
      <el-col :span="12">
        <el-card>
          <template #header><span>紧急程度分布</span></template>
          <div ref="pieChart" style="height: 350px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header><span>月度趋势 (近12个月)</span></template>
          <div ref="lineChart" style="height: 350px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近隐患 -->
    <el-card style="margin-top: 16px;">
      <template #header>
        <div class="card-header">
          <span>最近隐患记录</span>
          <el-button size="small" @click="exportData">导出Excel</el-button>
        </div>
      </template>
      <el-table :data="recent" v-loading="loading" stripe>
        <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
        <el-table-column label="紧急程度" width="90">
          <template #default="{ row }">
            <el-tag :type="urgencyTag(row.urgency)" size="small">{{ row.urgencyLabel }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status)" size="small">{{ row.statusLabel }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="reporterName" label="上报人" width="90" />
        <el-table-column prop="point_name" label="巡检点" width="120" />
        <el-table-column label="上报时间" width="160">
          <template #default="{ row }">{{ formatTime(row.createdAt) }}</template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/api/http'
import { exportCSV } from '@/utils/export'

const loading = ref(false)
const overview = ref({ total: 0, reported: 0, handling: 0, completed: 0, closed: 0 })
const urgencyStats = ref<any[]>([]); const trend = ref<any[]>([]); const recent = ref<any[]>([])

const pieChart = ref<HTMLElement>(); const lineChart = ref<HTMLElement>()
let pieInst: any = null; let lineInst: any = null

function urgencyTag(u: string) { return { normal: 'warning', important: 'danger', urgent: 'danger' }[u] || 'info' }
function statusTag(s: string) {
  return { reported: 'info', reviewing: 'warning', handling: '', completed: 'success', closed: 'info' }[s] || 'info'
}
function formatTime(t: string | null) {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

async function loadData() {
  loading.value = true
  try {
    const data = await request.get('/stats/hazard')
    overview.value = data.overview || overview.value
    urgencyStats.value = data.urgencyStats || []
    trend.value = data.trend || []
    recent.value = data.recent || []

    await nextTick()
    const echarts = await import('echarts')

    // 饼图：紧急程度
    if (pieChart.value && urgencyStats.value.length > 0) {
      if (!pieInst) pieInst = echarts.default.init(pieChart.value)
      const colors: Record<string, string> = { normal: '#FFB300', important: '#FF6D00', urgent: '#FF1744' }
      pieInst.setOption({
        tooltip: { trigger: 'item' },
        legend: { bottom: 0, textStyle: { color: '#8892A0' } },
        series: [{
          type: 'pie', radius: '65%', center: ['50%', '45%'],
          label: { color: '#8892A0' },
          data: urgencyStats.value.map(s => ({
            value: s.count,
            name: s.urgencyLabel,
            itemStyle: { color: colors[s.urgency] || '#8892A0' },
          })),
        }],
      }, true)
    }

    // 折线图：月度趋势
    if (lineChart.value && trend.value.length > 0) {
      if (!lineInst) lineInst = echarts.default.init(lineChart.value)
      lineInst.setOption({
        tooltip: { trigger: 'axis' },
        legend: { data: ['上报数', '关闭数'], bottom: 0, textStyle: { color: '#8892A0' } },
        grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
        xAxis: { type: 'category', data: trend.value.map(t => t.month), axisLabel: { color: '#8892A0' } },
        yAxis: { type: 'value', axisLabel: { color: '#8892A0' } },
        series: [
          { name: '上报数', type: 'line', data: trend.value.map(t => t.reported), smooth: true, itemStyle: { color: '#FFB300' }, lineStyle: { width: 2 } },
          { name: '关闭数', type: 'line', data: trend.value.map(t => t.closed), smooth: true, itemStyle: { color: '#00E676' }, lineStyle: { width: 2 } },
        ],
      }, true)
    }
  } catch { /* */ }
  finally { loading.value = false }
}

function exportData() {
  if (recent.value.length === 0) { ElMessage.warning('暂无数据'); return }
  exportCSV(
    ['标题', '紧急程度', '状态', '上报人', '巡检点', '时间'],
    recent.value.map(d => [d.title, d.urgencyLabel, d.statusLabel, d.reporterName || '', d.point_name || '', formatTime(d.createdAt)]),
    '隐患统计报表'
  )
  ElMessage.success('导出成功')
}

onMounted(async () => { await nextTick(); loadData() })
onUnmounted(() => { pieInst?.dispose(); lineInst?.dispose() })
</script>
<style scoped>
.stats-page { padding: 16px; }
.stats-row { margin-bottom: 4px; }
.stat-item { text-align: center; padding: 12px 0; }
.stat-label { font-size: 14px; color: #8892A0; margin-bottom: 8px; }
.stat-value { font-size: 36px; font-weight: bold; font-family: 'Courier New', monospace; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
