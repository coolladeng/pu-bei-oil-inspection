<template>
  <div class="stats-page">
    <!-- 概要卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="6"><el-card shadow="hover"><div class="stat-item"><div class="stat-label">今日应检</div><div class="stat-value" style="color:#00D4FF">{{ overview.total || 0 }}</div></div></el-card></el-col>
      <el-col :span="6"><el-card shadow="hover"><div class="stat-item"><div class="stat-label">已完成</div><div class="stat-value" style="color:#00E676">{{ overview.completed || 0 }}</div></div></el-card></el-col>
      <el-col :span="6"><el-card shadow="hover"><div class="stat-item"><div class="stat-label">完成率</div><div class="stat-value" style="color:#00D4FF">{{ overview.rate || 0 }}%</div></div></el-card></el-col>
      <el-col :span="6"><el-card shadow="hover"><div class="stat-item"><div class="stat-label">超时/漏检</div><div class="stat-value" style="color:#FF1744">{{ (overview.overdue || 0) + (overview.missed || 0) }}</div></div></el-card></el-col>
    </el-row>

    <!-- 图表区 -->
    <el-row :gutter="16" style="margin-top: 16px;">
      <el-col :span="14">
        <el-card>
          <template #header><span>各班组今日完成率</span></template>
          <div ref="barChart" style="height: 350px;"></div>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card>
          <template #header><span>巡检员排名 (今日)</span></template>
          <div class="ranking-list">
            <div v-for="(u, idx) in userRanking" :key="u.user_id" class="rank-item">
              <span class="rank-num" :class="'top' + (idx + 1)" v-if="idx < 3">{{ idx + 1 }}</span>
              <span class="rank-num" v-else>{{ idx + 1 }}</span>
              <span class="rank-name">{{ u.user_name }}</span>
              <span class="rank-count">{{ u.count }} 条</span>
            </div>
            <el-empty v-if="userRanking.length === 0" description="暂无数据" :image-size="60" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 趋势图 -->
    <el-card style="margin-top: 16px;">
      <template #header>
        <div class="card-header">
          <span>近7天完成率趋势</span>
          <el-button size="small" @click="exportData">导出Excel</el-button>
        </div>
      </template>
      <div ref="lineChart" style="height: 300px;"></div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/api/http'
import { exportCSV } from '@/utils/export'

const overview = ref({ total: 0, completed: 0, overdue: 0, missed: 0, rate: 0 })
const deptProgress = ref<any[]>([]); const trend = ref<any[]>([]); const userRanking = ref<any[]>([])

const barChart = ref<HTMLElement>(); const lineChart = ref<HTMLElement>()
let barInst: any = null; let lineInst: any = null

async function loadData() {
  try {
    const data = await request.get('/stats/inspection', { params: { days: 7 } })
    overview.value = data.overview || overview.value
    deptProgress.value = data.deptProgress || []
    trend.value = data.trend || []
    userRanking.value = data.userRanking || []

    await nextTick()
    const echarts = await import('echarts')

    // 柱状图：班组完成率
    if (barChart.value && deptProgress.value.length > 0) {
      if (!barInst) barInst = echarts.default.init(barChart.value)
      barInst.setOption({
        tooltip: {
          trigger: 'axis',
          formatter: (p: any) => {
            const d = deptProgress.value[p[0].dataIndex]
            return `${d.dept_name}<br/>完成率: ${d.rate}%<br/>已完成: ${d.completed}/${d.total}<br/>超时: ${d.overdue} | 漏检: ${d.missed}`
          },
        },
        grid: { left: '3%', right: '4%', bottom: '10%', containLabel: true },
        xAxis: { type: 'category', data: deptProgress.value.map(d => d.dept_name), axisLabel: { color: '#8892A0', rotate: 20 } },
        yAxis: { type: 'value', max: 100, axisLabel: { formatter: '{value}%', color: '#8892A0' } },
        series: [{
          type: 'bar',
          data: deptProgress.value.map(d => ({
            value: d.rate,
            itemStyle: { color: d.rate >= 80 ? '#00E676' : d.rate >= 50 ? '#FFB300' : '#FF1744' },
          })),
          label: { show: true, position: 'top', formatter: '{c}%', color: '#8892A0' },
        }],
      }, true)
    }

    // 折线图：近N天趋势
    if (lineChart.value && trend.value.length > 0) {
      if (!lineInst) lineInst = echarts.default.init(lineChart.value)
      lineInst.setOption({
        tooltip: { trigger: 'axis' },
        legend: { data: ['完成率', '应检数'], bottom: 0, textStyle: { color: '#8892A0' } },
        grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
        xAxis: { type: 'category', data: trend.value.map(t => t.date.slice(5)), axisLabel: { color: '#8892A0' } },
        yAxis: [
          { type: 'value', max: 100, axisLabel: { formatter: '{value}%', color: '#8892A0' } },
          { type: 'value', axisLabel: { color: '#8892A0' } },
        ],
        series: [
          {
            name: '完成率', type: 'line', yAxisIndex: 0,
            data: trend.value.map(t => t.rate), smooth: true,
            itemStyle: { color: '#00D4FF' }, lineStyle: { width: 2 },
            areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(0,212,255,0.3)' }, { offset: 1, color: 'rgba(0,212,255,0.02)' }] } },
          },
          {
            name: '应检数', type: 'bar', yAxisIndex: 1,
            data: trend.value.map(t => t.total),
            itemStyle: { color: 'rgba(136,146,160,0.3)' }, barWidth: '40%',
          },
        ],
      }, true)
    }
  } catch { /* */ }
}

function exportData() {
  if (deptProgress.value.length === 0) { ElMessage.warning('暂无数据'); return }
  exportCSV(
    ['班组', '应检数', '已检数', '超时', '漏检', '完成率(%)'],
    deptProgress.value.map(d => [d.dept_name, String(d.total), String(d.completed), String(d.overdue), String(d.missed), String(d.rate)]),
    '巡检统计报表'
  )
  ElMessage.success('导出成功')
}

onMounted(async () => { await nextTick(); loadData() })
onUnmounted(() => { barInst?.dispose(); lineInst?.dispose() })
</script>
<style scoped>
.stats-page { padding: 16px; }
.stats-row { margin-bottom: 4px; }
.stat-item { text-align: center; padding: 12px 0; }
.stat-label { font-size: 14px; color: #8892A0; margin-bottom: 8px; }
.stat-value { font-size: 36px; font-weight: bold; font-family: 'Courier New', monospace; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.ranking-list { max-height: 330px; overflow-y: auto; }
.rank-item { display: flex; align-items: center; padding: 8px 12px; margin-bottom: 4px; border-radius: 6px; background: #f8f9fa; }
.rank-num { width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; border-radius: 50%; font-size: 13px; font-weight: bold; background: #e0e0e0; color: #666; }
.rank-num.top1 { background: #FFD700; color: #fff; }
.rank-num.top2 { background: #C0C0C0; color: #fff; }
.rank-num.top3 { background: #CD7F32; color: #fff; }
.rank-name { flex: 1; margin-left: 12px; font-size: 14px; color: #303133; }
.rank-count { font-size: 13px; color: #8892A0; }
</style>
