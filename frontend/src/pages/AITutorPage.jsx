import { useState, useRef, useEffect } from "react";
import Layout from "../components/Layout";
import { ragApi } from "../services/ragApi";
import { documentApi } from "../services/documentApi";
import toast from "react-hot-toast";
import {
  Send,
  Bot,
  User,
  Trash2,
  Sparkles,
  History,
  Plus,
  Copy,
  Upload,
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const SUGGESTIONS = [
  "Explain the concept of double-entry bookkeeping",
  "What are the key IFRS standards for revenue recognition?",
  "How does audit risk assessment work?",
  "Explain the difference between direct and indirect costs",
  "What is the purpose of a trial balance?",
];

const INITIAL_MESSAGE = {
  role: "assistant",
  content:
    "Hello! I'm your RayHub AI CPA tutor. Ask me anything about accounting, auditing, taxation, finance, or any CPA topic.",
};

function Message({ msg }) {
  const isUser = msg.role === "user";

  const copyMessage = async () => {
    try {
      await navigator.clipboard.writeText(msg.content || "");
      toast.success("Response copied");
    } catch {
      toast.error("Failed to copy");
    }
  };

  return (
    <div className={`flex gap-3 ${isUser ? "flex-row-reverse" : ""}`}>
      <div
        className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
          isUser ? "bg-indigo-600" : "bg-emerald-100"
        }`}
      >
        {isUser ? (
          <User size={16} className="text-white" />
        ) : (
          <Bot size={16} className="text-emerald-700" />
        )}
      </div>

      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm ${
          isUser
            ? "bg-indigo-600 text-white rounded-tr-sm"
            : "bg-white border border-slate-100 text-slate-800 rounded-tl-sm shadow-sm"
        }`}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap">{msg.content}</p>
        ) : (
          <div className="prose prose-sm max-w-none prose-headings:text-slate-900 prose-p:text-slate-700 prose-li:text-slate-700">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {msg.content || ""}
            </ReactMarkdown>
          </div>
        )}

        {!isUser && (
          <button
            onClick={copyMessage}
            className="mt-3 flex items-center gap-1 text-xs text-indigo-600 hover:text-indigo-800"
          >
            <Copy size={13} />
            Copy response
          </button>
        )}

        {msg.sources && msg.sources.length > 0 && (
          <div className="mt-3 pt-2 border-t border-slate-200">
            <p className="text-xs text-slate-500 font-medium">Sources:</p>
            {msg.sources.map((source, index) => (
              <p key={index} className="text-xs text-slate-400 mt-0.5">
                • {source}
              </p>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default function AITutorPage() {
  const [messages, setMessages] = useState([INITIAL_MESSAGE]);
  const [history, setHistory] = useState([]);
  const [selectedChatId, setSelectedChatId] = useState(null);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [selectedResourceId, setSelectedResourceId] = useState("");
  const [uploading, setUploading] = useState(false);

  const bottomRef = useRef(null);

  const loadDocuments = async () => {
    try {
      const res = await documentApi.getDocuments();
      setDocuments(res.data || []);
    } catch {
      toast.error("Failed to load documents");
    }
  };

  const loadHistory = async () => {
    setHistoryLoading(true);

    try {
      const res = await ragApi.getHistory();

      const historyData = Array.isArray(res.data)
        ? res.data
        : res.data?.history || [];

      setHistory(historyData);
    } catch {
      toast.error("Failed to load chat history");
    } finally {
      setHistoryLoading(false);
    }
  };

  useEffect(() => {
    loadDocuments();
    loadHistory();
  }, []);

  const handleUpload = async (event) => {
  const file = event.target.files?.[0];

  if (!file) return;

  if (file.type !== "application/pdf") {
    toast.error("Please upload a PDF file only");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  setUploading(true);

  try {
    await ragApi.uploadPdf(formData);

    toast.success("PDF uploaded and indexed successfully");

    event.target.value = "";

    await loadDocuments();
  } catch (error) {
    toast.error(error.response?.data?.detail || "PDF upload failed");
  } finally {
    setUploading(false);
  }
};

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const startNewChat = () => {
    setSelectedChatId(null);
    setMessages([INITIAL_MESSAGE]);
    setInput("");
  };

  const openHistoryItem = (chat) => {
    setSelectedChatId(chat.id || null);

    setMessages([
      {
        role: "user",
        content: chat.question,
      },
      {
        role: "assistant",
        content: chat.answer,
        sources: chat.sources || [],
      },
    ]);
  };

  const deleteHistoryItem = async (event, chatId) => {
    event.stopPropagation();

    if (!chatId) {
      toast.error("This chat has no ID yet");
      return;
    }

    try {
      await ragApi.deleteChat(chatId);
      setHistory((prev) => prev.filter((chat) => chat.id !== chatId));

      if (selectedChatId === chatId) {
        startNewChat();
      }

      toast.success("Chat deleted");
    } catch {
      toast.error("Failed to delete chat");
    }
  };

  const sendMessage = async (text) => {
    const question = text || input.trim();

    if (!question || loading) return;

    setSelectedChatId(null);
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setInput("");
    setLoading(true);

    try {
      const res = selectedResourceId
        ? await ragApi.askResource({
            question,
            resource_id: Number(selectedResourceId),
            top_k: 5,
          })
        : await ragApi.ask({ question });

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: res.data.answer || "I could not generate a response.",
          sources: res.data.sources || [],
        },
      ]);

      await loadHistory();
    } catch (error) {
      const errorMessage =
        error.response?.data?.detail ||
        "Sorry, I encountered an error. Please try again.";

      toast.error(errorMessage);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `## Error\n${errorMessage}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="grid grid-cols-1 lg:grid-cols-[280px_1fr] gap-4 h-[calc(100vh-7rem)]">
        <aside className="bg-white border border-slate-100 rounded-2xl shadow-sm overflow-hidden flex flex-col">
          <div className="p-4 border-b border-slate-100 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <History size={18} className="text-indigo-600" />
              <h2 className="font-semibold text-slate-900">History</h2>
            </div>

            <button
              onClick={startNewChat}
              className="p-1.5 rounded-lg hover:bg-indigo-50 text-slate-500 hover:text-indigo-600"
              title="New chat"
            >
              <Plus size={16} />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-2">
            {historyLoading ? (
              <p className="text-xs text-slate-400 p-3">Loading history...</p>
            ) : history.length === 0 ? (
              <p className="text-xs text-slate-400 p-3">
                No previous AI Tutor chats yet.
              </p>
            ) : (
              <div className="space-y-1">
                {history.map((chat, index) => (
                  <button
                    key={chat.id || index}
                    onClick={() => openHistoryItem(chat)}
                    className={`group w-full text-left p-3 rounded-xl transition-colors ${
                      selectedChatId === chat.id
                        ? "bg-indigo-50 border border-indigo-100"
                        : "hover:bg-slate-50"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="min-w-0">
                        <p className="text-sm font-medium text-slate-800 line-clamp-2">
                          {chat.question}
                        </p>
                        <p className="text-xs text-slate-400 mt-1 line-clamp-1">
                          {chat.answer}
                        </p>
                      </div>

                      {chat.id && (
                        <span
                          onClick={(e) => deleteHistoryItem(e, chat.id)}
                          className="opacity-0 group-hover:opacity-100 p-1 rounded-md hover:bg-red-50 text-slate-400 hover:text-red-600"
                          title="Delete chat"
                        >
                          <Trash2 size={13} />
                        </span>
                      )}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </aside>

        <div className="flex flex-col min-h-0">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-emerald-100 rounded-xl flex items-center justify-center">
                <Bot size={20} className="text-emerald-700" />
              </div>


              <div>
                <h1 className="text-xl font-bold text-slate-900">AI Tutor</h1>
                <p className="text-xs text-slate-500">
                  Powered by your CPA study materials
                </p>
                <div className="mt-3 flex items-center gap-3 flex-wrap">
  <label className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 rounded-xl cursor-pointer hover:border-indigo-300 transition-colors text-sm">
    <Upload size={16} />

    <span>
      {uploading ? "Uploading PDF..." : "Upload PDF"}
    </span>

    <input
      type="file"
      accept=".pdf"
      className="hidden"
      onChange={handleUpload}
      disabled={uploading}
    />
  </label>

  {documents.length > 0 && (
    <select
      value={selectedResourceId}
      onChange={(e) => setSelectedResourceId(e.target.value)}
      className="px-3 py-2 border border-slate-200 rounded-xl text-sm bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
    >
      <option value="">Use all uploaded materials</option>

      {documents.map((doc) => (
        <option key={doc.id} value={doc.id}>
          {doc.title || doc.filename}
        </option>
      ))}
    </select>
  )}
</div>
              </div>
            </div>

            <button
              onClick={startNewChat}
              className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
            >
              <Plus size={14} /> New Chat
            </button>
          </div>

          {documents.length > 0 && (
            <div className="mb-3">
              <select
                value={selectedResourceId}
                onChange={(e) => setSelectedResourceId(e.target.value)}
                className="w-full md:w-80 px-3 py-2 border border-slate-200 rounded-xl text-sm bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">Ask from all available knowledge</option>
                {documents.map((doc) => (
                  <option key={doc.id} value={doc.id}>
                    {doc.title || doc.filename || `Document ${doc.id}`}
                  </option>
                ))}
              </select>
            </div>
          )}

          <div className="flex-1 overflow-y-auto bg-slate-50 rounded-2xl p-4 space-y-4 border border-slate-100">
            {messages.map((msg, index) => (
              <Message key={index} msg={msg} />
            ))}

            {loading && (
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-emerald-100 flex items-center justify-center">
                  <Bot size={16} className="text-emerald-700" />
                </div>

                <div className="bg-white border border-slate-100 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm">
                  <div className="flex gap-1">
                    {[0, 1, 2].map((item) => (
                      <div
                        key={item}
                        className="w-2 h-2 bg-slate-300 rounded-full animate-bounce"
                        style={{ animationDelay: `${item * 0.15}s` }}
                      />
                    ))}
                  </div>
                </div>
              </div>
            )}

            <div ref={bottomRef} />
          </div>

          {messages.length <= 1 && (
            <div className="flex gap-2 mt-3 flex-wrap">
              {SUGGESTIONS.slice(0, 3).map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => sendMessage(suggestion)}
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-white border border-slate-200 rounded-full text-xs text-slate-600 hover:border-indigo-300 hover:text-indigo-700 transition-colors"
                >
                  <Sparkles size={11} /> {suggestion.slice(0, 45)}...
                </button>
              ))}
            </div>
          )}

          <form
            onSubmit={(event) => {
              event.preventDefault();
              sendMessage();
            }}
            className="flex gap-3 mt-3"
          >
            <input
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Ask anything about CPA topics..."
              className="flex-1 px-4 py-3 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
              disabled={loading}
            />

            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="px-4 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 disabled:opacity-50 transition-colors"
            >
              <Send size={18} />
            </button>
          </form>
        </div>
      </div>
    </Layout>
  );
}