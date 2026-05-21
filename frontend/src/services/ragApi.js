import api from "./api";

export const ragApi = {
  ask: (data) => api.post("/rag/ask", data),

  askResource: (data) =>
    api.post("/rag/ask", {
      question: data.question,
    }),

  getHistory: () => api.get("/rag/history"),

  deleteChat: (chatId) => api.delete(`/rag/history/${chatId}`),

  uploadPdf: (formData) =>
    api.post("/rag/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }),
};