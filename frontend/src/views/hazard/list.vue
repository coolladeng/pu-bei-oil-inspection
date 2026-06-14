<template>
  <div class="hazard-list">
    <!-- 统计卡片 -->
    <el-row :gutter="16" style="margin-bottom: 16px;">
      <el-col :span="4" v-for="s in statsCards" :key="s.key">
        <el-card shadow="hover" class="stat-card" :class="s.cssClass">
          <div class="stat-value" :style="{ color: s.color }">{{ s.value }}</div>
          <div class="stat-label">{{ s.label }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部" clearable style="width: 140px" @change="loadData">
            <el-option label="已上报" value="reported" />
            <el-option label="审核中" value="reviewing" />
            <el-option label="处理中" value="handling" />
            <el-option label="已完成" value="completed" />
            <el-option label="已关闭" value="closed" />
          </el-select>
        </el-form-item>
        <el-form-item label="紧急程度">
          <el-select v-model="searchForm.urgency" placeholder="全部" clearable style="width: 140px" @change="loadData">
            <el-option label="一般 🟡" value="normal" />
            <el-option label="重要 🟠" value="important" />
            <el-option label="紧急 🔴" value="urgent" />
          </el-select>
        </el-form-item>
        <el-form-item label="搜索">
          <el-input v-model="searchForm.keyword" placeholder="标题/描述" clearable style="width: 200px" @keyup.enter="loadData" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 隐患列表 -->
    <el-card class="table-card">
      <el-table :data="list" v-loading="loading" stripe @row-click="viewDetail" style="cursor: pointer">
        <el-table-column prop="title" label="隐患标题" min-width="200" show-overflow-tooltip />
        <el-table-column label="紧急程度" width="100">
          <template #default="{ row }">
            <el-tag :type="urgencyTag(row.urgency)" size="small">{{ urgencyLabel(row.urgency) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="来源" width="80">
          <template #default="{ row }">
            <el-tag size="small">{{ row.source === 'patrol' ? '巡检' : '设备检查' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="point_name" label="巡检点" width="120" />
        <el-table-column prop="equipName" label="设备" width="120" />
        <el-table-column prop="reporterName" label="上报人" width="100" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="上报时间" width="160">
          <template #default="{ row }">{{ formatTime(row.createdAt) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }" @click.stop>
            <el-button link type="primary" @click.stop="viewDetail(row)">详情</el-button>
            <el-button v-if="canReview(row)" link type="warning" @click.stop="openReviewDialog(row)">审核</el-button>
            <el-button v-if="row.status === 'handling'" link type="primary" @click.stop="openHandleDialog(row)">处理</el-button>
            <el-button v-if="row.status === 'completed'" link type="success" @click.stop="openAcceptDialog(row)">验收</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrap">
        <el-pagination v-model:current-page="page" v-model:page-size="pageSize" :total="total" :page-sizes="[10,20,50]" layout="total, sizes, prev, pager, next" @change="loadData" />
      </div>
    </el-card>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="隐患详情" width="750px" destroy-on-close>
      <template v-if="detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="隐患标题" :span="2">{{ detail.title }}</el-descriptions-item>
          <el-descriptions-item label="紧急程度">
            <el-tag :type="urgencyTag(detail.urgency)" size="small">{{ urgencyLabel(detail.urgency) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="当前状态">
            <el-tag :type="statusTag(detail.status)" size="small">{{ statusLabel(detail.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="来源">{{ detail.source === 'patrol' ? '巡检' : '设备检查' }}</el-descriptions-item>
          <el-descriptions-item label="上报人">{{ detail.reporterName || '-' }}</el-descriptions-item>
          <el-descriptions-item label="巡检点">{{ detail.point_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="关联设备">{{ detail.equipName || '-' }}</el-descriptions-item>
          <el-descriptions-item label="审核人" v-if="detail.reviewerName">{{ detail.reviewerName }}</el-descriptions-item>
          <el-descriptions-item label="处理人" v-if="detail.handlerName">{{ detail.handlerName }}</el-descriptions-item>
          <el-descriptions-item label="上报时间">{{ formatTime(detail.createdAt) }}</el-descriptions-item>
          <el-descriptions-item label="完成时间" v-if="detail.completedAt">{{ formatTime(detail.completedAt) }}</el-descriptions-item>
          <el-descriptions-item label="隐患描述" :span="2">
            <div style="white-space: pre-wrap; max-height: 120px; overflow-y: auto;">{{ detail.description || '无' }}</div>
          </el-descriptions-item>
          <el-descriptions-item label="处理结果" :span="2" v-if="detail.handleResult">
            <div style="white-space: pre-wrap;">{{ detail.handleResult }}</div>
          </el-descriptions-item>
        </el-descriptions>

        <!-- 照片/视频附件 -->
        <div v-if="photos.length > 0" style="margin-top: 16px;">
          <div class="detail-subtitle">现场照片 ({{ photos.length }})</div>
          <div style="display: flex; gap: 8px; flex-wrap: wrap;">
            <el-image v-for="att in photos" :key="att.id" :src="'/uploads/' + att.filePath" fit="cover" style="width: 120px; height: 120px; border-radius: 4px;" :preview-src-list="photos.map(a => '/uploads/' + a.filePath)" />
          </div>
        </div>
        <div v-if="videos.length > 0" style="margin-top: 16px;">
          <div class="detail-subtitle">现场视频 ({{ videos.length }})</div>
          <div style="display: flex; gap: 8px; flex-wrap: wrap;">
            <div v-for="att in videos" :key="att.id" style="width: 200px;">
              <video :src="'/uploads/' + att.filePath" controls style="width: 100%; border-radius: 4px;" />
              <div style="font-size: 12px; color: #999; margin-top: 4px;" v-if="att.duration">时长: {{ att.duration }}s | 大小: {{ formatSize(att.fileSize) }}</div>
            </div>
          </div>
        </div>

        <!-- 流转时间线 -->
        <div v-if="detail.flows && detail.flows.length > 0" style="margin-top: 16px;">
          <div class="detail-subtitle">处理流转记录</div>
          <el-timeline>
            <el-timeline-item v-for="flow in detail.flows" :key="flow.id" :timestamp="formatTime(flow.createdAt)" :type="flowType(flow.action)" :hollow="flow.action === 'reject'">
              <div>
                <strong>{{ flowLabel(flow.action) }}</strong>
                <span style="color: #8892A0; margin-left: 4px;">— {{ flow.operatorName || '系统' }}</span>
              </div>
              <div v-if="flow.comment" style="color: #8892A0; font-size: 13px; margin-top: 2px;">{{ flow.comment }}</div>
            </el-timeline-item>
          </el-timeline>
        </div>
      </template>
      <div v-else v-loading="detailLoading" style="min-height: 200px;"></div>
      <template #footer>
        <div style="display: flex; gap: 8px; justify-content: flex-end;">
          <el-button v-if="detail && canReview(detail)" type="warning" @click="detailVisible = false; openReviewDialog(detail)">审核</el-button>
          <el-button v-if="detail && detail.status === 'handling'" type="primary" @click="detailVisible = false; openHandleDialog(detail)">处理</el-button>
          <el-button v-if="detail && detail.status === 'completed'" type="success" @click="detailVisible = false; openAcceptDialog(detail)">验收</el-button>
          <el-button @click="detailVisible = false">关闭</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 审核弹窗 -->
    <el-dialog v-model="reviewVisible" title="隐患审核" width="500px" destroy-on-close>
      <el-form :model="reviewForm" label-width="80px">
        <el-form-item label="隐患标题"><strong>{{ reviewTarget?.title }}</strong></el-form-item>
        <el-form-item label="描述"><span style="color: #666;">{{ reviewTarget?.description || '无' }}</span></el-form-item>
        <el-form-item label="审核意见" prop="comment">
          <el-input v-model="reviewForm.comment" type="textarea" :rows="3" placeholder="请输入审核意见" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reviewVisible = false">取消</el-button>
        <el-button type="danger" @click="doReview('reject')" :loading="reviewSubmitting">驳回</el-button>
        <el-button type="success" @click="doReview('approve')" :loading="reviewSubmitting">通过</el-button>
      </template>
    </el-dialog>

    <!-- 处理弹窗 -->
    <el-dialog v-model="handleVisible" title="隐患处理" width="500px" destroy-on-close>
      <el-form :model="handleForm" label-width="80px">
        <el-form-item label="隐患标题"><strong>{{ handleTarget?.title }}</strong></el-form-item>
        <el-form-item label="处理结果" prop="result">
          <el-input v-model="handleForm.result" type="textarea" :rows="4" placeholder="请描述处理措施和结果" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="handleVisible = false">取消</el-button>
        <el-button type="primary" @click="doHandle" :loading="handleSubmitting">提交处理</el-button>
      </template>
    </el-dialog>

    <!-- 验收弹窗 -->
    <el-dialog v-model="acceptVisible" title="隐患验收" width="500px" destroy-on-close>
      <el-form :model="acceptForm" label-width="80px">
        <el-form-item label="隐患标题"><strong>{{ acceptTarget?.title }}</strong></el-form-item>
        <el-form-item label="处理结果" v-if="acceptTarget?.handleResult">
          <div style="white-space: pre-wrap; color: #666; background: #f5f7fa; padding: 8px 12px; border-radius: 4px;">{{ acceptTarget.handleResult }}</div>
        </el-form-item>
        <el-form-item label="验收意见">
          <el-input v-model="acceptForm.comment" type="textarea" :rows="2" placeholder="可选，验收意见" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="acceptVisible = false">取消</el-button>
        <el-button type="success" @click="doAccept" :loading="acceptSubmitting">确认验收</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/api/http'

// ===== 状态 =====
const loading = ref(false); const list = ref<any[]>([]); const page = ref(1); const pageSize = ref(20); const total = ref(0)
const searchForm = reactive({ status: '', urgency: '', keyword: '' })
const stats = reactive({ total: 0, pendingReview: 0, pendingHandle: 0, completed: 0, closed: 0 })

// 详情
const detailVisible = ref(false); const detailLoading = ref(false); const detail = ref<any>(null)
const photos = computed(() => (detail.value?.attachments || []).filter((a: any) => a.fileType === 'photo'))
const videos = computed(() => (detail.value?.attachments || []).filter((a: any) => a.fileType === 'video'))

// 审核
const reviewVisible = ref(false); const reviewSubmitting = ref(false)
const reviewTarget = ref<any>(null)
const reviewForm = reactive({ comment: '' })

// 处理
const handleVisible = ref(false); const handleSubmitting = ref(false)
const handleTarget = ref<any>(null)
const handleForm = reactive({ result: '' })

// 验收
const acceptVisible = ref(false); const acceptSubmitting = ref(false)
const acceptTarget = ref<any>(null)
const acceptForm = reactive({ comment: '' })

// ===== 统计卡片 =====
const statsCards = computed(() => [
  { key: 'total', label: '隐患总数', value: stats.total, color: '#409EFF', cssClass: 'blue' },
  { key: 'pendingReview', label: '待审核', value: stats.pendingReview, color: '#E6A23C', cssClass: 'orange' },
  { key: 'pendingHandle', label: '待处理', value: stats.pendingHandle, color: '#00D4FF', cssClass: 'cyan' },
  { key: 'completed', label: '已完成', value: stats.completed, color: '#67C23A', cssClass: 'green' },
  { key: 'closed', label: '已关闭', value: stats.closed, color: '#909399', cssClass: 'gray' },
])

// ===== 工具函数 =====
function urgencyTag(u: string) { return { normal: 'warning', important: 'danger', urgent: 'danger' }[u] || 'info' }
function urgencyLabel(u: string) { return { normal: '一般🟡', important: '重要🟠', urgent: '紧急🔴' }[u] || u }
function statusTag(s: string) { return { reported: 'info', reviewing: 'warning', handling: '', completed: 'success', closed: 'info' }[s] || 'info' }
function statusLabel(s: string) { return { reported: '已上报', reviewing: '审核中', handling: '处理中', completed: '已完成', closed: '已关闭' }[s] || s }
function flowLabel(a: string) { return { report: '上报隐患', review: '审核通过', reject: '审核驳回', handle: '处理完成', accept: '验收通过' }[a] || a }
function flowType(a: string) { return { report: 'primary', review: 'success', reject: 'danger', handle: 'primary', accept: 'success' }[a] || 'info' }
function canReview(row: any) { return row.status === 'reported' || row.status === 'reviewing' }
function formatTime(t: string | null) {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}
function formatSize(bytes: number | null) {
  if (!bytes) return '-'
  if (bytes < 1024) return bytes + 'B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + 'KB'
  return (bytes / (1024 * 1024)).toFixed(1) + 'MB'
}

// ===== 数据加载 =====
async function loadStats() {
  try {
    const data = await request.get('/hazards/stats/overview')
    Object.assign(stats, data)
  } catch { /* ignore */ }
}
async function loadData() {
  loading.value = true
  try {
    const params: any = { page: page.value, pageSize: pageSize.value }
    if (searchForm.status) params.status = searchForm.status
    if (searchForm.urgency) params.urgency = searchForm.urgency
    if (searchForm.keyword) params.keyword = searchForm.keyword
    const data = await request.get('/hazards', { params })
    list.value = data.list || []
    total.value = data.total || 0
  } finally { loading.value = false }
}
function resetSearch() { searchForm.status = ''; searchForm.urgency = ''; searchForm.keyword = ''; page.value = 1; loadData() }

async function viewDetail(row: any) {
  detailVisible.value = true; detailLoading.value = true; detail.value = null
  try {
    const data = await request.get(`/hazards/${row.id}`)
    detail.value = data
  } catch {
    detail.value = row
  } finally {
    detailLoading.value = false
  }
}

// ===== 审核 =====
function openReviewDialog(row: any) {
  reviewTarget.value = row; reviewForm.comment = ''
  reviewVisible.value = true
}
async function doReview(action: string) {
  reviewSubmitting.value = true
  try {
    await request.put(`/hazards/${reviewTarget.value.id}/review`, {
      action,
      comment: reviewForm.comment || (action === 'approve' ? '审核通过' : '审核驳回'),
    })
    ElMessage.success(action === 'approve' ? '审核通过' : '已驳回')
    reviewVisible.value = false; loadData(); loadStats()
  } finally { reviewSubmitting.value = false }
}

// ===== 处理 =====
function openHandleDialog(row: any) {
  handleTarget.value = row; handleForm.result = ''
  handleVisible.value = true
}
async function doHandle() {
  if (!handleForm.result) { ElMessage.warning('请填写处理结果'); return }
  handleSubmitting.value = true
  try {
    await request.put(`/hazards/${handleTarget.value.id}/handle`, { result: handleForm.result })
    ElMessage.success('处理完成')
    handleVisible.value = false; loadData(); loadStats()
  } finally { handleSubmitting.value = false }
}

// ===== 验收 =====
function openAcceptDialog(row: any) {
  acceptTarget.value = row; acceptForm.comment = ''
  acceptVisible.value = true
}
async function doAccept() {
  acceptSubmitting.value = true
  try {
    await request.put(`/hazards/${acceptTarget.value.id}/accept`, { comment: acceptForm.comment || null })
    ElMessage.success('验收完成')
    acceptVisible.value = false; loadData(); loadStats()
  } finally { acceptSubmitting.value = false }
}

onMounted(() => { loadStats(); loadData() })
</script>
<style scoped>
.hazard-list { padding: 16px; }
.search-card { margin-bottom: 16px; }
.table-card { cursor: default; }
.pagination-wrap { margin-top: 16px; display: flex; justify-content: flex-end; }
.stat-card { text-align: center; border-top: 3px solid transparent; }
.stat-card.blue { border-top-color: #409EFF; }
.stat-card.orange { border-top-color: #E6A23C; }
.stat-card.cyan { border-top-color: #00D4FF; }
.stat-card.green { border-top-color: #67C23A; }
.stat-card.gray { border-top-color: #909399; }
.stat-value { font-size: 28px; font-weight: 700; font-family: 'Courier New', monospace; }
.stat-label { font-size: 13px; color: #8892A0; margin-top: 4px; }
.detail-subtitle { font-size: 14px; font-weight: bold; color: #303133; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #EBEEF5; }
</style>
