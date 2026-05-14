import api from './api';

export const documentApi = {
  upload: (formData) =>
    api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }),

  getDocuments: () => api.get('/documents/'),
  deleteDocument: (id) => api.delete(`/documents/${id}`),
};