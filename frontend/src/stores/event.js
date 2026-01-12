import { defineStore } from 'pinia'
import { ref } from 'vue'
import request from '@/api/request'

export const useEventStore = defineStore('event', () => {
  // 运动项目列表
  const events = ref([])
  const eventsLoading = ref(false)
  
  // 项目组别
  const eventGroups = ref([])
  
  // 预置模板
  const templates = ref([])

  // 获取运动项目列表
  async function fetchEvents(params = {}) {
    eventsLoading.value = true
    try {
      const res = await request.get('/events', { params })
      events.value = res.data || res.items || res
      return events.value
    } catch (error) {
      console.error('获取运动项目列表失败:', error)
      return []
    } finally {
      eventsLoading.value = false
    }
  }

  // 获取单个项目详情
  async function fetchEvent(id) {
    const res = await request.get(`/events/${id}`)
    return res.data || res
  }

  // 创建运动项目
  async function createEvent(data) {
    const res = await request.post('/events', data)
    await fetchEvents()
    return res
  }

  // 更新运动项目
  async function updateEvent(id, data) {
    const res = await request.put(`/events/${id}`, data)
    await fetchEvents()
    return res
  }

  // 删除运动项目
  async function deleteEvent(id) {
    await request.delete(`/events/${id}`)
    await fetchEvents()
  }

  // 获取项目组别
  async function fetchEventGroups(eventId) {
    const res = await request.get(`/events/${eventId}/groups`)
    eventGroups.value = res.data || res
    return eventGroups.value
  }

  // 创建项目组别
  async function createEventGroup(eventId, data) {
    const res = await request.post(`/events/${eventId}/groups`, data)
    await fetchEventGroups(eventId)
    return res
  }

  // 更新项目组别
  async function updateEventGroup(eventId, groupId, data) {
    const res = await request.put(`/events/${eventId}/groups/${groupId}`, data)
    await fetchEventGroups(eventId)
    return res
  }

  // 删除项目组别
  async function deleteEventGroup(eventId, groupId) {
    await request.delete(`/events/${eventId}/groups/${groupId}`)
    await fetchEventGroups(eventId)
  }

  // 获取预置模板
  async function fetchTemplates() {
    try {
      const res = await request.get('/events/templates')
      templates.value = res.data || res
      return templates.value
    } catch (error) {
      console.error('获取预置模板失败:', error)
      return []
    }
  }

  // 从模板创建项目
  async function createFromTemplate(templateId) {
    const res = await request.post(`/events/templates/${templateId}/create`)
    await fetchEvents()
    return res
  }

  return {
    events,
    eventsLoading,
    eventGroups,
    templates,
    fetchEvents,
    fetchEvent,
    createEvent,
    updateEvent,
    deleteEvent,
    fetchEventGroups,
    createEventGroup,
    updateEventGroup,
    deleteEventGroup,
    fetchTemplates,
    createFromTemplate
  }
})
