<template>
  <div class="screen-page">
    <!-- 顶部标题栏 -->
    <div class="header">
      <div class="header-left">
        <div class="title">{{ selectedDeptName }}实时监控大屏</div>
        <div class="subtitle">{{ currentTime }}</div>
        <el-tag v-if="wsConnected" type="success" size="small" effect="dark">实时连接</el-tag>
        <el-tag v-else type="danger" size="small" effect="dark">轮询模式</el-tag>
      </div>
      <div class="header-right">
        <el-tree-select v-model="selectedDept" :data="deptTree" :props="{ label: 'name', value: 'id', children: 'children' }" placeholder="选择大队/班组" @change="onDeptChange" size="large" style="width: 240px" />
      </div>
    </div>

    <!-- 第一行：关键指标 -->
    <el-row :gutter="16" class="row-cards">
      <el-col :span="4" v-for="item in kpiList" :key="item.label">
        <div class="kpi-card">
          <div class="kpi-label">{{ item.label }}</div>
          <div class="kpi-value" :style="{ color: item.color }">{{ item.value }}</div>
          <div class="kpi-unit">{{ item.unit }}</div>
        </div>
      </el-col>
    </el-row>

    <!-- 第二行：巡检进度 + 告警 -->
    <el-row :gutter="16" class="row-cards">
      <el-col :span="14">
        <div class="panel">
          <div class="panel-title">巡检进度</div>
          <div ref="progressChart" class="chart"></div>
        </div>
      </el-col>
      <el-col :span="10">
        <div class="panel">
          <div class="panel-title">实时告警</div>
          <div class="alert-list">
            <div v-for="alert in alerts" :key="alert.id" class="alert-item" :class="alert.urgency">
              <span class="alert-time">{{ alert.time }}</span>
              <span class="alert-dot">●</span>
              <span class="alert-text">{{ alert.title }}</span>
            </div>
            <div v-if="alerts.length === 0" class="no-alert">暂无告警信息</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 第三行：班组排名 + 设备状态 -->
    <el-row :gutter="16" class="row-cards">
      <el-col :span="12">
        <div class="panel">
          <div class="panel-title">班组完成率排名</div>
          <div ref="rankChart" class="chart"></div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="panel">
          <div class="panel-title">设备状态总览</div>
          <div ref="equipChart" class="chart"></div>
        </div>
      </el-col>
    </el-row>

    <!-- 第四行：巡检点分布地图 + 今日明细 -->
    <el-row :gutter="16" class="row-cards">
      <el-col :span="12">
        <div class="panel">
          <div class="panel-title">巡检点分布</div>
          <div ref="mapChart" class="chart"></div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="panel">
          <div class="panel-title">今日巡检明细</div>
          <div class="detail-table">
            <el-table :data="detailList" size="small" style="width: 100%" :header-cell-style="{ background: '#0D1F3C', color: '#00D4FF' }" :cell-style="{ background: '#0A1628', color: '#E0E6ED' }">
              <el-table-column prop="dept_name" label="班组" min-width="120" />
              <el-table-column prop="user_name" label="巡检员" width="100" />
              <el-table-column prop="point_name" label="巡检点" min-width="140" />
              <el-table-column prop="status" label="状态" width="80">
                <template #default="{ row }">
                  <el-tag :type="detailStatusTag(row.status)" size="small">{{ detailStatusLabel(row.status) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="check_time" label="检查时间" width="160" />
            </el-table>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, reactive } from 'vue'
import * as echarts from 'echarts'
import request from '@/api/http'

const deptTree = ref<any[]>([])
const selectedDept = ref<number | null>(null)
const selectedDeptName = ref('')
const currentTime = ref('')
const alerts = ref<any[]>([])
const detailList = ref<any[]>([])
const wsConnected = ref(false)
let timer: any = null
let ws: WebSocket | null = null

const kpiList = reactive([
  { label: '应巡检点数', value: '--', unit: '个', color: '#00D4FF' },
  { label: '已完成', value: '--', unit: '个', color: '#00E676' },
  { label: '完成率', value: '--', unit: '%', color: '#00E676' },
  { label: '超时', value: '--', unit: '个', color: '#FFB300' },
  { label: '漏检', value: '--', unit: '个', color: '#FF1744' },
  { label: '隐患总数', value: '--', unit: '个', color: '#FFB300' },
])

const progressChart = ref<HTMLElement>()
const rankChart = ref<HTMLElement>()
const equipChart = ref<HTMLElement>()
const mapChart = ref<HTMLElement>()
let progressInstance: any = null
let rankInstance: any = null
let equipInstance: any = null
let mapInstance: any = null

function updateTime() {
  const now = new Date()
  currentTime.value = now.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

function detailStatusTag(s: string) { return { normal: 'success', abnormal: 'danger', overtime: 'warning', missed: 'danger' }[s] || 'info' }
function detailStatusLabel(s: string) { return { normal: '正常', abnormal: '异常', overtime: '超时', missed: '漏检' }[s] || s }

async function loadDeptTree() {
  try {
    const data = await request.get('/departments')
    deptTree.value = Array.isArray(data) ? data : []
  } catch { deptTree.value = [] }
}

async function loadData() {
  try {
    const params = selectedDept.value ? `?dept_id=${selectedDept.value}` : ''
    const [stats, alerts_data, records, points_data] = await Promise.all([
      request.get(`/stats/dashboard${params}`),
      request.get(`/hazards?status=reported,reviewing&pageSize=10`),
      request.get(`/run-records?pageSize=20`),
      request.get('/run-points?pageSize=500'),
    ])

    const data = stats || {}
    kpiList[0].value = String(data.totalPoints || 0)
    kpiList[1].value = String(data.completed || 0)
    kpiList[2].value = String(data.rate || 0)
    kpiList[3].value = String(data.overdue || 0)
    kpiList[4].value = String(data.missed || 0)
    kpiList[5].value = String(data.hazardCount || 0)

    alerts.value = (alerts_data?.list || []).slice(0, 10).map((a: any) => ({
      id: a.id, title: a.title, urgency: a.urgency, time: a.createdAt?.substring(0, 16),
    }))

    detailList.value = (records?.list || []).map((r: any) => ({
      dept_name: r.dept_name || '-', user_name: r.user_name || '-', point_name: r.point_name || '-',
      status: r.status, check_time: r.check_time,
    }))

    renderCharts(data)
    renderMapChart(points_data?.list || [])

  } catch { /* silent */ }
}

function renderCharts(data: any) {
  if (progressChart.value) {
    if (!progressInstance) progressInstance = echarts.init(progressChart.value)
    progressInstance.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'category', data: ['已检', '未检', '超时', '漏检'], axisLabel: { color: '#8892A0' }, axisLine: { lineStyle: { color: '#1A3A5C' } } },
      yAxis: { type: 'value', axisLabel: { color: '#8892A0' }, splitLine: { lineStyle: { color: '#1A3A5C' } } },
      series: [{
        type: 'bar',
        data: [
          { value: data.completed || 0, itemStyle: { color: '#00E676' } },
          { value: (data.totalPoints || 0) - (data.completed || 0) - (data.overdue || 0) - (data.missed || 0), itemStyle: { color: '#8892A0' } },
          { value: data.overdue || 0, itemStyle: { color: '#FFB300' } },
          { value: data.missed || 0, itemStyle: { color: '#FF1744' } },
        ],
      }],
    })
  }

  if (rankChart.value) {
    if (!rankInstance) rankInstance = echarts.init(rankChart.value)
    const sorted = [...(data.progress || [])].sort((a: any, b: any) => (b.rate || 0) - (a.rate || 0))
    rankInstance.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'value', max: 100, axisLabel: { color: '#8892A0', formatter: '{value}%' }, splitLine: { lineStyle: { color: '#1A3A5C' } } },
      yAxis: { type: 'category', data: sorted.map((d: any) => d.dept_name || d.name).reverse(), axisLabel: { color: '#E0E6ED' }, axisLine: { lineStyle: { color: '#1A3A5C' } } },
      series: [{
        type: 'bar',
        data: sorted.map((d: any) => ({ value: d.rate || 0, itemStyle: { color: (d.rate || 0) >= 80 ? '#00E676' : (d.rate || 0) >= 50 ? '#FFB300' : '#FF1744' } })).reverse(),
      }],
    })
  }

  if (equipChart.value) {
    if (!equipInstance) equipInstance = echarts.init(equipChart.value)
    equipInstance.setOption({
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie', radius: ['40%', '70%'],
        label: { color: '#E0E6ED' },
        data: [
          { value: data.equipNormal || 0, name: '正常', itemStyle: { color: '#00E676' } },
          { value: data.equipMaintaining || 0, name: '维修中', itemStyle: { color: '#FFB300' } },
          { value: data.equipFault || 0, name: '故障', itemStyle: { color: '#FF1744' } },
        ],
      }],
    })
  }
}

function renderMapChart(points: any[]) {
  if (!mapChart.value) return
  if (!mapInstance) mapInstance = echarts.init(mapChart.value)

  const pointData = points.filter((p: any) => p.latitude && p.longitude).map((p: any) => ({
    name: p.name,
    value: [p.longitude, p.latitude, p.status],
  }))

  mapInstance.setOption({
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => `${params.name}<br/>状态: ${params.value[2] === 1 ? '已检' : '未检'}`,
    },
    grid: { left: '10%', right: '10%', top: '10%', bottom: '10%' },
    xAxis: { type: 'value', show: true, axisLabel: { color: '#8892A0', fontSize: 10 }, axisLine: { lineStyle: { color: '#1A3A5C' } }, splitLine: { show: true, lineStyle: { color: '#1A3A5C', type: 'dashed' } }, name: '经度', nameTextStyle: { color: '#8892A0', fontSize: 10 } },
    yAxis: { type: 'value', show: true, axisLabel: { color: '#8892A0', fontSize: 10 }, axisLine: { lineStyle: { color: '#1A3A5C' } }, splitLine: { show: true, lineStyle: { color: '#1A3A5C', type: 'dashed' } }, name: '纬度', nameTextStyle: { color: '#8892A0', fontSize: 10 } },
    series: [{
      type: 'scatter',
      data: pointData,
      symbolSize: 12,
      itemStyle: { color: '#00D4FF' },
      label: { show: true, formatter: '{b}', position: 'right', color: '#E0E6ED', fontSize: 11 },
    }],
  })
}

function connectWebSocket() {
  const token = localStorage.getItem('token')
  const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsUrl = `${protocol}//${location.host}/ws/screen${token ? `?token=${token}` : ''}`

  try {
    ws = new WebSocket(wsUrl)
    ws.onopen = () => { wsConnected.value = true; console.log('[WS] 大屏连接成功') }
    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data)
        if (msg.type === 'alert') {
          alerts.value.unshift({
            id: Date.now(),
            title: msg.data.title,
            urgency: msg.data.urgency,
            time: new Date().toLocaleTimeString('zh-CN'),
          })
          if (alerts.value.length > 20) alerts.value = alerts.value.slice(0, 20)
        }
        if (msg.type === 'progress' || msg.type === 'stats') {
          loadData()
        }
      } catch { /* */ }
    }
    ws.onclose = () => { wsConnected.value = false; setTimeout(connectWebSocket, 5000) }
    ws.onerror = () => { wsConnected.value = false }
  } catch { wsConnected.value = false }
}

function onDeptChange(val: number | null) {
  const findName = (list: any[], id: number | null): string => {
    if (!id) return '全站'
    for (const item of list) {
      if (item.id === id) return item.name
      if (item.children) { const n = findName(item.children, id); if (n) return n }
    }
    return ''
  }
  selectedDeptName.value = findName(deptTree.value, val) + ' '
  loadData()
}

function cleanupCharts() {
  progressInstance?.dispose(); progressInstance = null
  rankInstance?.dispose(); rankInstance = null
  equipInstance?.dispose(); equipInstance = null
  mapInstance?.dispose(); mapInstance = null
}

onMounted(async () => {
  updateTime()
  timer = setInterval(updateTime, 1000)
  await loadDeptTree()
  selectedDeptName.value = '全站 '
  await nextTick()
  connectWebSocket()
  loadData()
  setInterval(() => loadData(), 30000)
})

onUnmounted(() => {
  clearInterval(timer)
  if (ws) { ws.close(); ws = null }
  cleanupCharts()
})
</script>

<style scoped>
.screen-page {
  background: #0A1628;
  min-height: 100vh;
  padding: 16px;
  color: #E0E6ED;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.header-left {
  display: flex;
  align-items: baseline;
  gap: 24px;
}
.title { font-size: 24px; font-weight: bold; color: #00D4FF; text-shadow: 0 0 10px rgba(0,212,255,0.3); }
.subtitle { font-size: 16px; color: #8892A0; font-family: monospace; }
.row-cards { margin-bottom: 16px; }
.kpi-card {
  background: linear-gradient(135deg, #0D1F3C 0%, #142B4A 100%);
  border: 1px solid #1A3A5C;
  border-radius: 8px;
  padding: 16px;
  text-align: center;
}
.kpi-label { font-size: 13px; color: #8892A0; margin-bottom: 8px; }
.kpi-value { font-size: 28px; font-weight: bold; font-family: 'Courier New', monospace; }
.kpi-unit { font-size: 12px; color: #8892A0; margin-top: 4px; }
.panel {
  background: linear-gradient(135deg, #0D1F3C 0%, #142B4A 100%);
  border: 1px solid #1A3A5C;
  border-radius: 8px;
  padding: 16px;
  height: 100%;
}
.panel-title { font-size: 14px; color: #00D4FF; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #1A3A5C; }
.chart { height: 260px; }
.alert-list { height: 260px; overflow-y: auto; }
.alert-item { padding: 8px 12px; margin-bottom: 4px; border-radius: 4px; display: flex; align-items: center; gap: 8px; font-size: 13px; }
.alert-item.urgent { background: rgba(255,23,68,0.15); }
.alert-item.warning { background: rgba(255,179,0,0.1); }
.alert-time { color: #8892A0; font-size: 12px; font-family: monospace; width: 80px; }
.alert-dot { color: #FF1744; font-size: 10px; }
.alert-item.warning .alert-dot { color: #FFB300; }
.alert-text { flex: 1; }
.no-alert { text-align: center; color: #8892A0; padding: 60px 0; }
.detail-table { max-height: 300px; overflow-y: auto; }
</style>