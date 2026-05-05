import api from './api';

export const progressApi = {
  getMyProgress: () => api.get('/progress/me'),
  getSummary: () => api.get('/progress/summary'),
  updateProgress: (data) => api.post('/progress/update', data),
  getWeakAreas: () => api.get('/progress/weak-areas'),
  getRecommendations: () => api.get('/progress/recommendations'),

  // Gamification
  getGamificationProfile: () => api.get('/gamification/profile'),
  getLeaderboard: () => api.get('/gamification/leaderboard'),
  getBadges: () => api.get('/gamification/badges'),
  getStreak: () => api.get('/gamification/streak'),

  // Study Plans
  generateStudyPlan: (data) => api.post('/study-plans/generate', data),
  getMyStudyPlans: () => api.get('/study-plans/me'),
  getStudyPlan: (id) => api.get(`/study-plans/${id}`),
  completeTask: (planId, data) => api.post(`/study-plans/${planId}/complete-task`, data),
  deleteStudyPlan: (id) => api.delete(`/study-plans/${id}`),

  // Community
  getPosts: (params) => api.get('/community/posts', { params }),
  getPost: (id) => api.get(`/community/posts/${id}`),
  createPost: (data) => api.post('/community/posts', data),
  addComment: (postId, data) => api.post(`/community/posts/${postId}/comments`, data),
  likePost: (postId) => api.post(`/community/posts/${postId}/like`),
};