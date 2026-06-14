<template>
  <div class="hazard-audit">
    <!-- 统计 -->
    <el-row :gutter="16" style="margin-bottom: 16px;">
      <el-col :span="8">
        <el-card shadow="hover" class="audit-stat orange"><div class="stat-num">{{ list.length }}</div><div class="stat-lbl">待审核隐患</div></el-card>
      </el-col>
    </el-row>

    <!-- 待审核列表 -->
    <el-card v-if="list.length > 0">
      <el-table :data="list" v-loading="loading" stripe @row-click="showDetail" style="cursor: pointer">
        <el-table-column prop="title" label="隐患标题" min-width="220" show-overflow-tooltip />
        <el-table-column label="紧急程度" width="100">
          <template #default="{ row }">
            <el-tag :type="row.urgency === 'urgent' ? 'danger' : 'warning'" size="small">{{ urgencyLabel(row.urgency) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="来源" width="80">
          <template #default="{ row }">{{ row.source === 'patrol' ? '巡检' : '设备' }}</template>
        </el-table-column>
        <el-table-column prop="reporterName" label="上报人" width="100" />
        <el-table-column label="上报时间" width="160">
          <template #default="{ row }">{{ formatTime(row.createdAt) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }" @click.stop>
            <el-button link type="primary" size="small" @click.stop="showDetail(row)">查看</el-button>
            <el-button type="success" size="small" @click.stop="openReview(row)">通过</el-button>
            <el-button type="danger" size="small" @click.stop="openReject(row)">驳回</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    <el-empty v-else description="暂无待审核隐患" />

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="隐患详情" width="750px" destroy-on-close>
      <template v-if="detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="标题" :span="2">{{ detail.title }}</el-descriptions-item>
          <el-descriptions-item label="紧急程度">
            <el-tag :type="detail.urgency === 'urgent' ? 'danger' : 'warning'" size="small">{{ urgencyLabel(detail.urgency) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="来源">{{ detail.source === 'patrol' ? '巡检' : '设备检查' }}</el-descriptions-item>
          <el-descriptions-item label="上报人">{{ detail.reporterName || '-' }}</el-descriptions-item>
          <el-descriptions-item label="巡检点">{{ detail.point_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="关联设备">{{ detail.equipName || '-' }}</el-descriptions-item>
          <el-descriptions-item label="上报时间">{{ formatTime(detail.createdAt) }}</el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">
            <div style="white-space: pre-wrap; max-height: 120px; overflow-y: auto;">{{ detail.description || '无' }}</div>
          </el-descriptions-item>
        </el-descriptions>

        <!-- 附件 -->
        <div v-if="detail.attachments && detail.attachments.length > 0" style="margin-top: 16px;">
          <div class="subtitle">现场照片/视频 ({{ detail.attachments.length }})</div>
          <div style="display: flex; gap: 8px; flex-wrap: wrap;">
            <template v-for="att in detail.attachments" :key="att.id">
              <el-image v-if="att.fileType === 'photo'" :src="'/uploads/' + att.filePath" fit="cover" style="width: 120px; height: 120px; border-radius: 4px;" :preview-src-list="detail.attachments.filter((a: any) => a.fileType === 'photo').map((a: any) => '/uploads/' + a.filePath)" />
              <video v-else-if="att.fileType === 'video'" :src="'/uploads/' + att.filePath" controls style="width: 200px; height: 120px; border-radius: 4px;" />
            </template>
          </div>
        </div>
      </template>
      <div v-else v-loading="detailLoading" style="min-height: 200px;"></div>
      <template #footer>
        <el-button type="danger" @click="detailVisible = false; openReject(detail)">驳回</el-button>
        <el-button type="success" @click="detailVisible = false; openReview(detail)">通过</el-button>
      </template>
    </el-dialog>

    <!-- 审核/驳回弹窗 -->
    <el-dialog v-model="reviewVisible" :title="reviewAction === 'approve' ? '审核通过' : '审核驳回'" width="500px" destroy-on-close>
      <el-form label-width="80px">
        <el-form-item label="隐患标题"><strong>{{ reviewTarget?.title }}</strong></el-form-item>
        <el-form-item label="审核意见">
          <el-input v-model="reviewComment" type="textarea" :rows="3" :placeholder="reviewAction === 'approve' ? '可选，审核通过意见' : '请填写驳回原因'" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reviewVisible = false">取消</el-button>
        <el-button :type="reviewAction === 'approve' ? 'success' : 'danger'" @click="doReview" :loading="reviewSubmitting">
          {{ reviewAction === 'approve' ? '确认通过' : '确认驳回' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/api/http'

const loading = ref(false); const list = ref<any[]>([])

// 详情
const detailVisible = ref(false); const detailLoading = ref(false); const detail = ref<any>(null)

// 审核
const reviewVisible = ref(false); const reviewSubmitting = ref(false)
const reviewTarget = ref<any>(null); const reviewAction = ref('approve'); const reviewComment = ref('')

function urgencyLabel(u: string) { return { normal: '一般🟡', important: '重要🟠', urgent: '紧急🔴' }[u] || u }
function formatTime(t: string | null) {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

async function loadData() {
  loading.value = true
  try {
    // 加载已上报和审核中的隐患
    const data = await request.get('/hazards', { params: { status: 'reported,reviewing', pageSize: 100 } })
    list.value = data.list || []
  } finally { loading.value = false }
}

async function showDetail(row: any) {
  detailVisible.value = true; detailLoading.value = true; detail.value = null
  try {
    detail.value = await request.get(`/hazards/${row.id}`)
  } catch {
    detail.value = row
  } finally { detailLoading.value = false }
}

function openReview(row: any) {
  reviewTarget.value = row; reviewAction.value = 'approve'; reviewComment.value = ''
  reviewVisible.value = true
}
function openReject(row: any) {
  reviewTarget.value = row; reviewAction.value = 'reject'; reviewComment.value = ''
  reviewVisible.value = true
}

async function doReview() {
  if (reviewAction.value === 'reject' && !reviewComment.value) {
    ElMessage.warning('驳回时请填写原因'); return
  }
  reviewSubmitting.value = true
  try {
    await request.put(`/hazards/${reviewTarget.value.id}/review`, {
      action: reviewAction.value,
      comment: reviewComment.value || (reviewAction.value === 'approve' ? '审核通过' : '审核驳回'),
    })
    ElMessage.success(reviewAction.value === 'approve' ? '审核通过' : '已驳回')
    reviewVisible.value = false; loadData()
  } finally { reviewSubmitting.value = false }
}

onMounted(() => { loadData() })
</script>
<style scoped>
.hazard-audit { padding: 16px; }
.audit-stat { text-align: center; border-top: 3px solid transparent; }
.audit-stat.orange { border-top-color: #E6A23C; }
.stat-num { font-size: 32px; font-weight: 700; font-family: 'Courier New', monospace; color: #E6A23C; }
.stat-lbl { font-size: 13px; color: #8892A0; margin-top: 4px; }
.subtitle { font-size: 14px; font-weight: bold; color: #303133; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #EBEEF5; }
</style>
