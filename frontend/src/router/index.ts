import { createRouter, createWebHistory } from 'vue-router'

const routes: any = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { title: '登录', public: true },
  },
  {
    path: '/',
    component: () => import('@/views/layout/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '仪表盘', icon: 'Odometer' },
      },
      // 巡检管理
      {
        path: 'inspection/points',
        name: 'InspectionPoints',
        component: () => import('@/views/inspection/points.vue'),
        meta: { title: '巡检点管理', icon: 'Location' },
      },
      {
        path: 'inspection/positions',
        name: 'InspectionPositions',
        component: () => import('@/views/inspection/positions.vue'),
        meta: { title: '岗位管理', icon: 'User' },
      },
      {
        path: 'inspection/plans',
        name: 'InspectionPlans',
        component: () => import('@/views/inspection/plans.vue'),
        meta: { title: '巡检计划', icon: 'Calendar' },
      },
      {
        path: 'inspection/supervise',
        name: 'InspectionSupervise',
        component: () => import('@/views/inspection/supervise.vue'),
        meta: { title: '巡检监督', icon: 'Monitor' },
      },
      // 设备管理
      {
        path: 'equipment/list',
        name: 'EquipmentList',
        component: () => import('@/views/equipment/list.vue'),
        meta: { title: '设备档案', icon: 'Cpu' },
      },
      {
        path: 'equipment/tasks',
        name: 'CheckTasks',
        component: () => import('@/views/equipment/tasks.vue'),
        meta: { title: '检查任务', icon: 'List' },
      },
      {
        path: 'equipment/results',
        name: 'CheckResults',
        component: () => import('@/views/equipment/results.vue'),
        meta: { title: '检查结果', icon: 'DocumentChecked' },
      },
      // 隐患管理
      {
        path: 'hazard/list',
        name: 'HazardList',
        component: () => import('@/views/hazard/list.vue'),
        meta: { title: '隐患管理', icon: 'Warning' },
      },
      {
        path: 'hazard/audit',
        name: 'HazardAudit',
        component: () => import('@/views/hazard/audit.vue'),
        meta: { title: '隐患审核', icon: 'Checked' },
      },
      // 统计分析
      {
        path: 'statistics/inspection',
        name: 'StatsInspection',
        component: () => import('@/views/statistics/inspection.vue'),
        meta: { title: '巡检统计', icon: 'DataAnalysis' },
      },
      {
        path: 'statistics/equipment',
        name: 'StatsEquipment',
        component: () => import('@/views/statistics/equipment.vue'),
        meta: { title: '设备统计', icon: 'TrendCharts' },
      },
      {
        path: 'statistics/hazard',
        name: 'StatsHazard',
        component: () => import('@/views/statistics/hazard.vue'),
        meta: { title: '隐患统计', icon: 'PieChart' },
      },
      // 系统管理
      {
        path: 'system/users',
        name: 'SystemUsers',
        component: () => import('@/views/system/users.vue'),
        meta: { title: '用户管理', icon: 'UserFilled' },
      },
      {
        path: 'system/departments',
        name: 'SystemDepts',
        component: () => import('@/views/system/departments.vue'),
        meta: { title: '单位管理', icon: 'OfficeBuilding' },
      },
      {
        path: 'system/roles',
        name: 'SystemRoles',
        component: () => import('@/views/system/roles.vue'),
        meta: { title: '角色权限', icon: 'Key' },
      },
      // 实时监控大屏
      {
        path: 'screen',
        name: 'RealtimeScreen',
        component: () => import('@/views/screen/index.vue'),
        meta: { title: '实时监控大屏', icon: 'Screen' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫 - 权限校验
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.public) {
    next()
  } else {
    if (token) {
      next()
    } else {
      next('/login')
    }
  }
})

export default router

