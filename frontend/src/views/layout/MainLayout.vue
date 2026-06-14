<template>
  <div class="layout-container">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '220px'" class="layout-aside">
      <div class="aside-header">
        <el-icon :size="28" color="#00D4FF"><Platform /></el-icon>
        <span v-show="!isCollapse" class="aside-title">储运销售葡北油库</span>
      </div>

      <el-menu
        :default-active="currentRoute"
        :collapse="isCollapse"
        :unique-opened="true"
        router
        class="aside-menu"
        background-color="#0A1628"
        text-color="#8892A0"
        active-text-color="#00D4FF"
      >
        <!-- 仪表盘 -->
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <template #title>仪表盘</template>
        </el-menu-item>

        <!-- 巡检管理 -->
        <el-sub-menu index="inspection">
          <template #title>
            <el-icon><Location /></el-icon>
            <span>巡检管理</span>
          </template>
          <el-menu-item index="/inspection/points">巡检点管理</el-menu-item>
          <el-menu-item index="/inspection/positions">岗位管理</el-menu-item>
          <el-menu-item index="/inspection/plans">巡检计划</el-menu-item>
          <el-menu-item index="/inspection/supervise">巡检监督</el-menu-item>
        </el-sub-menu>

        <!-- 设备管理 -->
        <el-sub-menu index="equipment">
          <template #title>
            <el-icon><Cpu /></el-icon>
            <span>设备管理</span>
          </template>
          <el-menu-item index="/equipment/list">设备档案</el-menu-item>
          <el-menu-item index="/equipment/tasks">检查任务</el-menu-item>
          <el-menu-item index="/equipment/results">检查结果</el-menu-item>
        </el-sub-menu>

        <!-- 隐患管理 -->
        <el-sub-menu index="hazard">
          <template #title>
            <el-icon><Warning /></el-icon>
            <span>隐患管理</span>
          </template>
          <el-menu-item index="/hazard/list">隐患列表</el-menu-item>
          <el-menu-item index="/hazard/audit">隐患审核</el-menu-item>
        </el-sub-menu>

        <!-- 统计分析 -->
        <el-sub-menu index="statistics">
          <template #title>
            <el-icon><DataAnalysis /></el-icon>
            <span>统计分析</span>
          </template>
          <el-menu-item index="/statistics/inspection">巡检统计</el-menu-item>
          <el-menu-item index="/statistics/equipment">设备统计</el-menu-item>
          <el-menu-item index="/statistics/hazard">隐患统计</el-menu-item>
        </el-sub-menu>

        <!-- 实时监控大屏 -->
        <el-menu-item index="/screen">
          <el-icon><Monitor /></el-icon>
          <template #title>实时监控大屏</template>
        </el-menu-item>

        <!-- 系统管理 -->
        <el-sub-menu index="system">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统管理</span>
          </template>
          <el-menu-item index="/system/departments">单位管理</el-menu-item>
          <el-menu-item index="/system/users">用户管理</el-menu-item>
          <el-menu-item index="/system/roles">角色权限</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <!-- 主内容区 -->
    <el-main class="layout-main">
      <!-- 顶部栏 -->
      <div class="main-header">
        <div class="header-left">
          <el-icon
            :size="20"
            class="collapse-btn"
            @click="isCollapse = !isCollapse"
          ><Fold v-if="!isCollapse" /><Expand v-else /></el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="header-right">
          <!-- 全屏按钮 -->
          <el-icon :size="18" class="header-icon" @click="toggleFullscreen">
            <FullScreen />
          </el-icon>

          <!-- 用户信息 -->
          <el-dropdown trigger="click">
            <div class="user-info">
              <el-avatar :size="32" class="user-avatar">
                <el-icon><UserFilled /></el-icon>
              </el-avatar>
              <span class="user-name">{{ userStore.userInfo?.real_name || '管理员' }}</span>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>个人中心</el-dropdown-item>
                <el-dropdown-item>修改密码</el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>

      <!-- 内容区 -->
      <div class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </el-main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const isCollapse = ref(false)

const currentTitle = computed(() => {
  return (route.meta.title as string) || '首页'
})

const currentRoute = computed(() => route.path)

function toggleFullscreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
  } else {
    document.exitFullscreen()
  }
}

async function handleLogout() {
  await ElMessageBox.confirm('确认退出登录?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  })
  await userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout-container {
  display: flex;
  height: 100vh;
  width: 100vw;
}

.layout-aside {
  background: #0D1B2E;
  border-right: 1px solid var(--border-color);
  transition: width 0.3s ease;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.aside-header {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
}

.aside-title {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  white-space: nowrap;
  letter-spacing: 2px;
}

.aside-menu {
  flex: 1;
  overflow-y: auto;
  border-right: none;
  background: #0D1B2E;
}

:deep(.el-menu) {
  border-right: none;
}

:deep(.el-menu-item),
:deep(.el-sub-menu__title) {
  color: #8892A0;
  transition: all 0.3s;
}

:deep(.el-menu-item:hover),
:deep(.el-sub-menu__title:hover) {
  background: rgba(0, 212, 255, 0.08) !important;
  color: #00D4FF;
}

:deep(.el-menu-item.is-active) {
  background: rgba(0, 212, 255, 0.12) !important;
  color: #00D4FF;
  border-right: 3px solid #00D4FF;
}

:deep(.el-popper.is-light) {
  background: #132238;
  border: 1px solid var(--border-color);
}

.layout-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
  overflow: hidden;
  padding: 0;
}

.main-header {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  background: rgba(13, 27, 46, 0.8);
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
  backdrop-filter: blur(10px);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.collapse-btn {
  cursor: pointer;
  color: #8892A0;
  transition: color 0.3s;
}

.collapse-btn:hover {
  color: #00D4FF;
}

:deep(.el-breadcrumb__item .el-breadcrumb__inner) {
  color: #8892A0;
}

:deep(.el-breadcrumb__item:last-child .el-breadcrumb__inner) {
  color: #00D4FF;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-icon {
  cursor: pointer;
  color: #8892A0;
  transition: color 0.3s;
}

.header-icon:hover {
  color: #00D4FF;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #8892A0;
}

.user-info:hover {
  color: #fff;
}

.user-avatar {
  background: linear-gradient(135deg, #00D4FF, #7B61FF);
  color: #fff;
}

.user-name {
  font-size: 14px;
}

.main-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

/* 页面过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

