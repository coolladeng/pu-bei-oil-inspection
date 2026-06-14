<template>
  <div class="login-container">
    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="bg-circle c1"></div>
      <div class="bg-circle c2"></div>
      <div class="bg-grid"></div>
    </div>

    <!-- 登录卡片 -->
    <div class="login-card">
      <div class="login-header">
        <div class="logo-icon">
          <el-icon :size="48" color="#00D4FF">
            <Platform />
          </el-icon>
        </div>
        <h1 class="login-title">葡北油库安全巡检及红网监察系统</h1>
        <p class="login-subtitle">Oilfield Inspection & Equipment Management</p>
      </div>

      <el-form
        ref="formRef"
        :model="loginForm"
        :rules="rules"
        class="login-form"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            size="large"
            :prefix-icon="User"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            show-password
            :prefix-icon="Lock"
          />
        </el-form-item>

        <el-form-item>
          <div class="login-options">
            <el-checkbox v-model="rememberMe">记住密码</el-checkbox>
            <el-link type="primary" :underline="false">忘记密码?</el-link>
          </div>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="login-btn"
            @click="handleLogin"
          >
            {{ loading ? '登录中...' : '登 录' }}
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-footer">
        <span>版本 v1.0.0</span>
        <span>|</span>
        <span>Phase 1 - 基础框架</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { User, Lock } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

const formRef = ref<FormInstance>()
const loading = ref(false)
const rememberMe = ref(false)

const loginForm = reactive({
  username: '',
  password: '',
})

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' },
  ],
}

async function handleLogin() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await userStore.login(loginForm)
    ElMessage.success('登录成功')
    router.push('/')
  } catch (error) {
    console.error('登录失败:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0A1628;
  overflow: hidden;
}

.bg-decoration {
  position: absolute;
  inset: 0;
  overflow: hidden;
  z-index: 0;
}

.bg-circle {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.15;
}

.c1 {
  width: 600px;
  height: 600px;
  background: #00D4FF;
  top: -200px;
  right: -100px;
}

.c2 {
  width: 500px;
  height: 500px;
  background: #7B61FF;
  bottom: -150px;
  left: -100px;
}

.bg-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(0, 212, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 212, 255, 0.03) 1px, transparent 1px);
  background-size: 50px 50px;
}

.login-card {
  position: relative;
  z-index: 1;
  width: 420px;
  padding: 48px 40px;
  background: rgba(19, 34, 56, 0.85);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(0, 212, 255, 0.15);
  border-radius: 16px;
  box-shadow:
    0 0 40px rgba(0, 212, 255, 0.08),
    0 20px 60px rgba(0, 0, 0, 0.3);
}

.login-header {
  text-align: center;
  margin-bottom: 36px;
}

.logo-icon {
  margin-bottom: 16px;
  animation: pulse-glow 3s ease-in-out infinite;
}

.login-title {
  font-size: 26px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 8px;
  letter-spacing: 2px;
}

.login-subtitle {
  font-size: 12px;
  color: #8892A0;
  letter-spacing: 1px;
}

.login-form {
  margin-top: 28px;
}

.login-options {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.login-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  letter-spacing: 4px;
  border: none;
  background: linear-gradient(135deg, #00D4FF 0%, #0099CC 100%);
  border-radius: 8px;
  transition: all 0.3s;
}

.login-btn:hover {
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.4);
  transform: translateY(-1px);
}

.login-footer {
  margin-top: 24px;
  text-align: center;
  font-size: 12px;
  color: #8892A0;
  display: flex;
  justify-content: center;
  gap: 8px;
}

@keyframes pulse-glow {
  0%, 100% { filter: drop-shadow(0 0 8px rgba(0, 212, 255, 0.3)); }
  50% { filter: drop-shadow(0 0 20px rgba(0, 212, 255, 0.6)); }
}

/* 覆盖 el-input 样式以适配深色主题 */
:deep(.el-input__wrapper) {
  background: rgba(10, 22, 40, 0.8);
  border: 1px solid #1E3A5F;
  border-radius: 8px;
  box-shadow: none !important;
  transition: all 0.3s;
}

:deep(.el-input__wrapper:hover) {
  border-color: #00D4FF;
}

:deep(.el-input__wrapper.is-focus) {
  border-color: #00D4FF;
  box-shadow: 0 0 0 2px rgba(0, 212, 255, 0.15) !important;
}

:deep(.el-input__inner) {
  color: #fff;
}

:deep(.el-checkbox__label) {
  color: #8892A0;
}

:deep(.el-link--primary) {
  color: #00D4FF;
}
</style>
