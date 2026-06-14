<template>
  <div class="supervise-page">
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="日期">
          <el-date-picker v-model="searchForm.date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" style="width: 160px" />
        </el-form-item>
        <el-form-item label="大队/班组">
          <el-tree-select v-model="searchForm.dept_id" :data="deptTree" :props="{ label: 'name', value: 'id', children: 'children' }" placeholder="选择部门" clearable filterable style="width: 200px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 概览统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item"><div class="stat-label">应巡检</div><div class="stat-value">{{ stats.total }}</div></div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item"><div class="stat-label">已完成</div><div class="stat-value success">{{ stats.completed }}</div></div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item"><div class="stat-label">超时</div><div class="stat-value warning">{{ stats.overdue }}</div></div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item"><div class="stat-label">漏检</div><div class="stat-value danger">{{ stats.missed }}</div></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 班组进度 -->
    <el-card class="table-card">
      <template #header><span>班组巡检进度</span></template>
      <el-table :data="progressList" v-loading="loading" stripe>
        <el-table-column prop="dept_name" label="班组" min-width="150" />
        <el-table-column label="完成率" width="200">
          <template #default="{ row }">
            <el-progress :percentage="row.rate" :color="progressColor(row.rate)" />
          </template>
        </el-table-column>
        <el-table-column prop="completed" label="已检" width="80" />
        <el-table-column prop="pending" label="未检" width="80" />
        <el-table-column prop="overdue" label="超时" width="80" />
        <el-table-column prop="missed" label="漏检" width="80" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import request from '@/api/http'

const loading = ref(false)
const deptTree = ref<any[]>([])
const searchForm = reactive({ date: '', dept_id: null as number | null })
const stats = reactive({ total: 0, completed: 0, overdue: 0, missed: 0 })
const progressList = ref<any[]>([])

function progressColor(rate: number) {
  if (rate >= 80) return '#00E676'
  if (rate >= 50) return '#FFB300'
  return '#FF1744'
}

async function loadDeptTree() {
  const data = await request.get('/departments')
  deptTree.value = Array.isArray(data) ? data : []
}

async function loadData() {
  loading.value = true
  try {
    const params: any = {}
    if (searchForm.date) params.date = searchForm.date
    if (searchForm.dept_id) params.dept_id = searchForm.dept_id
    const data = await request.get('/stats/daily-run', { params })
    stats.total = data.total || 0
    stats.completed = data.completed || 0
    stats.overdue = data.overdue || 0
    stats.missed = data.missed || 0
    progressList.value = data.progress || []
  } finally { loading.value = false }
}

function resetSearch() {
  searchForm.date = ''
  searchForm.dept_id = null
  loadData()
}

onMounted(() => { loadDeptTree(); loadData() })
</script>
<style scoped>
.supervise-page { padding: 16px; }
.search-card { margin-bottom: 16px; }
.stats-row { margin-bottom: 16px; }
.stat-item { text-align: center; padding: 8px 0; }
.stat-label { font-size: 14px; color: #8892A0; margin-bottom: 8px; }
.stat-value { font-size: 32px; font-weight: bold; color: #00D4FF; }
.stat-value.success { color: #00E676; }
.stat-value.warning { color: #FFB300; }
.stat-value.danger { color: #FF1744; }
.table-card { }
</style>
