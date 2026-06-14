import request from './http'

export function login(username: string, password: string) {
  return request.post('/auth/login', { username, password })
}

export function getUserProfile() {
  return request.get('/auth/profile')
}

export function getMenuList() {
  return request.get('/auth/menu')
}

export function logout() {
  return request.post('/auth/logout')
}
