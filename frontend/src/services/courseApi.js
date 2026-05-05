import api from './api';

export const courseApi = {
  getLevels: () => api.get('/levels/'),
  getCourses: (levelId) => api.get('/courses/', { params: levelId ? { level_id: levelId } : {} }),
  getCourse: (id) => api.get(`/courses/${id}`),
  getUnits: (courseId) => api.get('/units/', { params: courseId ? { course_id: courseId } : {} }),
  getUnit: (id) => api.get(`/units/${id}`),
  getTopics: (unitId) => api.get('/topics/', { params: unitId ? { unit_id: unitId } : {} }),
  getTopic: (id) => api.get(`/topics/${id}`),
  createCourse: (data) => api.post('/courses/', data),
  createUnit: (data) => api.post('/units/', data),
  createTopic: (data) => api.post('/topics/', data),
};