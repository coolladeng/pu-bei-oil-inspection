<template>
  <div class="dashboard">
    <!-- 顶部概览卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #00D4FF, #0099CC)">
            <el-icon :size="28" color="#fff"><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">52</div>
            <div class="stat-label">在线用户</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #00E676, #009624)">
            <el-icon :size="28" color="#fff"><Location /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">128</div>
            <div class="stat-label">巡检点</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #7B61FF, #5A3DCC)">
            <el-icon :size="28" color="#fff"><Cpu /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">86</div>
            <div class="stat-label">设备</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #FF1744, #D50000)">
            <el-icon :size="28" color="#fff"><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">5</div>
            <div class="stat-label">今日隐患</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 中间区域 -->
    <el-row :gutter="16" class="content-row">
      <!-- 待办事项 -->
      <el-col :span="8">
        <div class="panel">
          <div class="panel-header">
            <span>今日待办</span>
            <el-tag type="warning" size="small">3 条待处理</el-tag>
          </div>
          <div class="todo-list">
            <div class="todo-item todo-danger">
              <el-icon><WarningFilled /></el-icon>
              <span>3条隐患待审核</span>
            </div>
            <div class="todo-item todo-warn">
              <el-icon><BellFilled /></el-icon>
              <span>2条隐患待处理</span>
            </div>
            <div class="todo-item todo-info">
              <el-icon><CircleCloseFilled /></el-icon>
              <span>1个岗位巡检超时</span>
            </div>
          </div>
        </div>
      </el-col>

      <!-- 今日巡检进度 -->
      <el-col :span="8">
        <div class="panel">
          <div class="panel-header">
            <span>今日巡检进度</span>
            <span class="progress-percent">75%</span>
          </div>
          <el-progress
            :percentage="75"
            :stroke-width="18"
            :show-text="false"
            color="linear-gradient(90deg, #00D4FF 0%, #00E676 100%)"
            class="main-progress"
          />
          <div class="progress-detail">
            <span class="detail-item"><span class="dot dot-success"></span>已检 24</span>
            <span class="detail-item"><span class="dot dot-warning"></span>超时 2</span>
            <span class="detail-item"><span class="dot dot-danger"></span>未检 5</span>
          </div>
        </div>
      </el-col>

      <!-- 快捷入口 -->
      <el-col :span="8">
        <div class="panel">
          <div class="panel-header">
            <span>快捷入口</span>
          </div>
          <div class="quick-links">
            <div class="quick-item" @click="$router.push('/inspection/supervise')">
              <el-icon :size="24" color="#00D4FF"><Monitor /></el-icon>
              <span>巡检监督</span>
            </div>
            <div class="quick-item" @click="$router.push('/equipment/list')">
              <el-icon :size="24" color="#7B61FF"><Cpu /></el-icon>
              <span>设备管理</span>
            </div>
            <div class="quick-item" @click="$router.push('/hazard/list')">
              <el-icon :size="24" color="#FF1744"><Warning /></el-icon>
              <span>隐患管理</span>
            </div>
            <div class="quick-item" @click="$router.push('/screen')">
              <el-icon :size="24" color="#FFB300"><FullScreen /></el-icon>
              <span>实时监控</span>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 底部区域 -->
    <el-row :gutter="16" class="bottom-row">
      <el-col :span="12">
        <div class="panel">
          <div class="panel-header">
            <span>各岗位巡检完成率</span>
          </div>
          <div ref="barChartRef" class="chart-container"></div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="panel">
          <div class="panel-header">
            <span>近7天隐患趋势</span>
          </div>
          <div ref="lineChartRef" class="chart-container"></div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import {
  User, Location, Cpu, Warning, Monitor, FullScreen,
  WarningFilled, BellFilled, CircleCloseFilled,
} from '@element-plus/icons-vue'

const barChartRef = ref<HTMLElement>()
const lineChartRef = ref<HTMLElement>()

onMounted(() => {
  initBarChart()
  initLineChart()
})

function initBarChart() {
  const chart = echarts.init(barChartRef.value)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: ['采油岗', '安全岗', '维保岗', '电工岗', '焊工岗'],
      axisLine: { lineStyle: { color: '#1E3A5F' } },
      axisLabel: { color: '#8892A0' },
    },
    yAxis: {
      type: 'value',
      max: 100,
      axisLine: { lineStyle: { color: '#1E3A5F' } },
      axisLabel: { color: '#8892A0' },
      splitLine: { lineStyle: { color: 'rgba(30,58,95,0.5)' } },
    },
    series: [{
      type: 'bar',
      data: [80, 70, 60, 85, 90],
      itemStyle: {
        color: (params) => {
          const colors = ['#00D4FF', '#00E676', '#FFB300', '#7B61FF', '#00D4FF']
          return colors[params.dataIndex]
        },
        borderRadius: [4, 4, 0, 0],
      },
      barWidth: '50%',
    }],
  })
}

function initLineChart() {
  const chart = echarts.init(lineChartRef.value)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
      axisLine: { lineStyle: { color: '#1E3A5F' } },
      axisLabel: { color: '#8892A0' },
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#1E3A5F' } },
      axisLabel: { color: '#8892A0' },
      splitLine: { lineStyle: { color: 'rgba(30,58,95,0.5)' } },
    },
    series: [{
      name: '隐患上报',
      type: 'line',
      data: [3, 5, 2, 8, 4, 6, 5],
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: { color: '#00D4FF', width: 2 },
      itemStyle: { color: '#00D4FF' },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(0,212,255,0.3)' },
          { offset: 1, color: 'rgba(0,212,255,0)' },
        ]),
      },
    }],
  })
}
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stats-row {
  margin-bottom: 0;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: var(--bg-card);
  backdrop-filter: blur(10px);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  transition: all 0.3s;
}

.stat-card:hover {
  border-color: var(--primary);
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.1);
  transform: translateY(-2px);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  font-family: 'JetBrains Mono', monospace;
}

.stat-label {
  font-size: 13px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.content-row {
  margin-bottom: 0;
}

.bottom-row {
  margin-bottom: 0;
}

.panel {
  padding: 20px;
  background: var(--bg-card);
  backdrop-filter: blur(10px);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  transition: all 0.3s;
}

.panel:hover {
  border-color: rgba(0, 212, 255, 0.2);
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  font-size: 15px;
  font-weight: 600;
  color: #fff;
}

.progress-percent {
  font-size: 18px;
  font-weight: 700;
  color: #00D4FF;
  font-family: 'JetBrains Mono', monospace;
}

.main-progress {
  margin-bottom: 12px;
}

.progress-detail {
  display: flex;
  gap: 20px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-secondary);
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.dot-success { background: #00E676; }
.dot-warning { background: #FFB300; }
.dot-danger { background: #FF1744; }

.todo-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.todo-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 14px;
}

.todo-danger {
  background: rgba(255, 23, 68, 0.1);
  border-left: 3px solid #FF1744;
  color: #FF1744;
}

.todo-warn {
  background: rgba(255, 179, 0, 0.1);
  border-left: 3px solid #FFB300;
  color: #FFB300;
}

.todo-info {
  background: rgba(0, 212, 255, 0.1);
  border-left: 3px solid #00D4FF;
  color: #00D4FF;
}

.quick-links {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.quick-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px;
  background: rgba(10, 22, 40, 0.5);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s;
  color: var(--text-secondary);
}

.quick-item:hover {
  border-color: var(--primary);
  background: rgba(0, 212, 255, 0.05);
  color: #fff;
}

.chart-container {
  width: 100%;
  height: 260px;
}

/* 覆盖 el-col 的负 margin */
:deep(.el-row) {
  margin-left: 0 !important;
  margin-right: 0 !important;
}
:deep(.el-col) {
  padding-left: 0 !important;
  padding-right: 0 !important;
}
</style>
