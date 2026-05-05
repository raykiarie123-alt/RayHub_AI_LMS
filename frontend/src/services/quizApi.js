import api from './api';

export const quizApi = {
  generateQuiz: (data) => api.post('/quizzes/generate', data),
  getQuizzes: (params) => api.get('/quizzes/', { params }),
  getQuiz: (id) => api.get(`/quizzes/${id}`),
  submitQuiz: (id, data) => api.post(`/quizzes/${id}/submit`, data),
  getResults: (id) => api.get(`/quizzes/${id}/results`),
  getHistory: () => api.get('/quizzes/me/history'),

  // Flashcards
  generateFlashcards: (data) => api.post('/flashcards/generate', data),
  getFlashcards: (params) => api.get('/flashcards/', { params }),
  reviewFlashcard: (data) => api.post('/flashcards/review', data),
  deleteFlashcard: (id) => api.delete(`/flashcards/${id}`),
};