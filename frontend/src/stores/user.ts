import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login as loginApi, getUserProfile, logout as logoutApi } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(null)
  const menuList = ref([])

  async function login(loginForm) {
    const res = await loginApi(loginForm.username, loginForm.password)
    token.value = res.access_token
    localStorage.setItem('token', res.access_token)
    await getUserInfo()
    return res
  }

  async function getUserInfo() {
    const profile = await getUserProfile()
    userInfo.value = profile
    menuList.value = []
  }

  async function logout() {
    await logoutApi()
    token.value = ''
    userInfo.value = null
    menuList.value = []
    localStorage.removeItem('token')
  }

  return { token, userInfo, menuList, login, getUserInfo, logout }
})
