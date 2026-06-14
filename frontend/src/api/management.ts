import request from './http'

export function getDepartments(params?) {
  return request.get('/departments', { params })
}

export function createDepartment(data) {
  return request.post('/departments', data)
}

export function updateDepartment(id, data) {
  return request.put(`/departments/${id}`, data)
}

export function deleteDepartment(id) {
  return request.delete(`/departments/${id}`)
}

export function getUsers(params?) {
  return request.get('/users', { params })
}

export function createUser(data) {
  return request.post('/users', data)
}

export function updateUser(id, data) {
  return request.put(`/users/${id}`, data)
}

export function deleteUser(id) {
  return request.delete(`/users/${id}`)
}

export function getRunPoints(params?) {
  return request.get('/run-points', { params })
}

export function createRunPoint(data) {
  return request.post('/run-points', data)
}

export function updateRunPoint(id, data) {
  return request.put(`/run-points/${id}`, data)
}

export function deleteRunPoint(id) {
  return request.delete(`/run-points/${id}`)
}
