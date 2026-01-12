import request from './request'

// 登录
export function login(data) {
  return request.post('/auth/login', data)
}

// 登出
export function logout() {
  return request.post('/auth/logout')
}

// 修改密码
export function changePassword(data) {
  return request.put('/auth/password', data)
}

// 获取当前用户信息
export function getCurrentUser() {
  return request.get('/auth/me')
}
