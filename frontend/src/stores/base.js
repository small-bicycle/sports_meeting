import { defineStore } from 'pinia'
import { ref } from 'vue'
import request from '@/api/request'

export const useBaseStore = defineStore('base', () => {
  // 年级列表
  const grades = ref([])
  const gradesLoading = ref(false)
  
  // 班级列表
  const classes = ref([])
  const classesLoading = ref(false)
  
  // 学生列表
  const students = ref([])
  const studentsLoading = ref(false)
  const studentTotal = ref(0)

  // 获取年级列表
  async function fetchGrades() {
    gradesLoading.value = true
    try {
      const res = await request.get('/grades')
      grades.value = res.data || res
      return grades.value
    } catch (error) {
      console.error('获取年级列表失败:', error)
      return []
    } finally {
      gradesLoading.value = false
    }
  }

  // 创建年级
  async function createGrade(data) {
    const res = await request.post('/grades', data)
    await fetchGrades()
    return res
  }

  // 更新年级
  async function updateGrade(id, data) {
    const res = await request.put(`/grades/${id}`, data)
    await fetchGrades()
    return res
  }

  // 删除年级
  async function deleteGrade(id) {
    await request.delete(`/grades/${id}`)
    await fetchGrades()
  }

  // 获取班级列表
  async function fetchClasses(gradeId = null) {
    classesLoading.value = true
    try {
      const params = gradeId ? { grade_id: gradeId } : {}
      const res = await request.get('/classes', { params })
      classes.value = res.data || res
      return classes.value
    } catch (error) {
      console.error('获取班级列表失败:', error)
      return []
    } finally {
      classesLoading.value = false
    }
  }

  // 创建班级
  async function createClass(data) {
    const res = await request.post('/classes', data)
    await fetchClasses()
    return res
  }

  // 更新班级
  async function updateClass(id, data) {
    const res = await request.put(`/classes/${id}`, data)
    await fetchClasses()
    return res
  }

  // 删除班级
  async function deleteClass(id) {
    await request.delete(`/classes/${id}`)
    await fetchClasses()
  }

  // 获取学生列表
  async function fetchStudents(params = {}) {
    studentsLoading.value = true
    try {
      const res = await request.get('/students', { params })
      students.value = res.data || res.items || res
      studentTotal.value = res.total || students.value.length
      return { items: students.value, total: studentTotal.value }
    } catch (error) {
      console.error('获取学生列表失败:', error)
      return { items: [], total: 0 }
    } finally {
      studentsLoading.value = false
    }
  }

  // 创建学生
  async function createStudent(data) {
    return await request.post('/students', data)
  }

  // 更新学生
  async function updateStudent(id, data) {
    return await request.put(`/students/${id}`, data)
  }

  // 删除学生
  async function deleteStudent(id) {
    await request.delete(`/students/${id}`)
  }

  // 批量导入学生
  async function importStudents(file) {
    const formData = new FormData()
    formData.append('file', file)
    return await request.post('/students/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }

  // 按班级批量导入学生
  async function importStudentsByClass(file, classId) {
    const formData = new FormData()
    formData.append('file', file)
    return await request.post(`/students/import-by-class?class_id=${classId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }

  return {
    grades,
    gradesLoading,
    classes,
    classesLoading,
    students,
    studentsLoading,
    studentTotal,
    fetchGrades,
    createGrade,
    updateGrade,
    deleteGrade,
    fetchClasses,
    createClass,
    updateClass,
    deleteClass,
    fetchStudents,
    createStudent,
    updateStudent,
    deleteStudent,
    importStudents,
    importStudentsByClass
  }
})
