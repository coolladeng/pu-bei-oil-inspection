<template>
  <div class="stats-page">
    <!-- 概要卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover"><div class="stat-item"><div class="stat-label">设备总数</div><div class="stat-value">{{ overview.total || 0 }}</div></div></el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover"><div class="stat-item"><div class="stat-label">正常运行</div><div class="stat-value" style="color:#00E676">{{ overview.normal || 0 }}</div></div></el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover"><div class="stat-item"><div class="stat-label">维修/报废</div><div class="stat-value" style="color:#FF1744">{{ (overview.maintaining || 0) + (overview.scrapped || 0) }}</div></div></el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover"><div class="stat-item"><div class="stat-label">完好率</div><div class="stat-value" style="color:#00D4FF">{{ 100 - (overview.faultRate || 0) }}%</div></div></el-card>
      </el-col>
    </el-row>

    <!-- 图表区 -->
    <el-row :gutter="16" style="margin-top: 16px;">
      <el-col :span="12">
        <el-card>
          <template #header><span>设备状态分布</span></template>
          <div ref="pieChart" style="height: 350px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header><span>各设备类别统计</span></template>
          <div ref="barChart" style="height: 350px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 设备明细 -->
    <el-card style="margin-top: 16px;">
      <template #header>
        <div class="card-header">
          <span>设备明细清单</span>
          <el-button size="small" @click="exportData">导出Excel</el-button>
        </div>
      </template>
      <el-table :data="equipList" v-loading="loading" stripe max-height="400">
        <el-table-column prop="code" label="编号" width="120" />
        <el-table-column prop="name" label="名称" min-width="160" />
        <el-table-column prop="model_no" label="型号" width="140" />
        <el-table-column prop="dept_name" label="所属部门" width="140" />
        <el-table-column prop="category" label="类别" width="100" />
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status)" size="small">{{ row.statusLabel }}</el-tag>
          </template>
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
const overview = ref({ total: 0, normal: 0, maintaining: 0, scrapped: 0, faultRate: 0 })
const equipList = ref<any[]>([]); const categories = ref<any[]>([])

const pieChart = ref<HTMLElement>(); const barChart = ref<HTMLElement>()
let pieInst: any = null; let barInst: any = null

function statusTag(s: number) { return { 1: 'success', 2: 'warning', 3: 'danger' }[s] || 'info' }

async function loadData() {
  loading.value = true
  try {
    const data = await request.get('/stats/equipment')
    overview.value = data.overview || overview.value
    equipList.value = data.list || []
    categories.value = data.categories || []

    await nextTick()
    const echarts = await import('echarts')
    const darkTheme = { textStyle: { color: '#E0E6ED' } }

    // 饼图：状态分布
    if (pieChart.value) {
      if (!pieInst) pieInst = echarts.default.init(pieChart.value)
      pieInst.setOption({
        ...darkTheme,
        tooltip: { trigger: 'item' },
        legend: { bottom: 0, textStyle: { color: '#8892A0' } },
        series: [{
          type: 'pie', radius: ['40%', '70%'], center: ['50%', '45%'],
          label: { color: '#8892A0' },
          data: [
            { value: overview.value.normal, name: '正常', itemStyle: { color: '#00E676' } },
            { value: overview.value.maintaining, name: '维修中', itemStyle: { color: '#FFB300' } },
            { value: overview.value.scrapped, name: '报废', itemStyle: { color: '#FF1744' } },
          ].filter(d => d.value > 0),
        }],
      }, true)
    }

    // 柱状图：类别统计
    if (barChart.value && categories.value.length > 0) {
      if (!barInst) barInst = echarts.default.init(barChart.value)
      barInst.setOption({
        ...darkTheme,
        tooltip: { trigger: 'axis' },
        legend: { data: ['正常', '异常'], textStyle: { color: '#8892A0' }, bottom: 0 },
        grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
        xAxis: { type: 'category', data: categories.value.map(c => c.category), axisLabel: { color: '#8892A0' } },
        yAxis: { type: 'value', axisLabel: { color: '#8892A0' } },
        series: [
          { name: '正常', type: 'bar', stack: 'total', data: categories.value.map(c => c.normal), itemStyle: { color: '#00E676' } },
          { name: '异常', type: 'bar', stack: 'total', data: categories.value.map(c => c.abnormal), itemStyle: { color: '#FF1744' } },
        ],
      }, true)
    }
  } catch { /* */ }
  finally { loading.value = false }
}

function exportData() {
  if (equipList.value.length === 0) { ElMessage.warning('暂无数据'); return }
  exportCSV(
    ['编号', '名称', '型号', '部门', '类别', '状态', '位置'],
    equipList.value.map(d => [d.code, d.name, d.model_no || '', d.dept_name || '', d.category || '', d.statusLabel, d.location || '']),
    '设备统计报表'
  )
  ElMessage.success('导出成功')
}

onMounted(async () => { await nextTick(); loadData() })
onUnmounted(() => { pieInst?.dispose(); barInst?.dispose() })
</script>
<style scoped>
.stats-page { padding: 16px; }
.stats-row { margin-bottom: 4px; }
.stat-item { text-align: center; padding: 12px 0; }
.stat-label { font-size: 14px; color: #8892A0; margin-bottom: 8px; }
.stat-value { font-size: 36px; font-weight: bold; color: #00D4FF; font-family: 'Courier New', monospace; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
