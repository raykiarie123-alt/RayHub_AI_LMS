import { useState, useRef, useEffect } from 'react';
import Layout from '../components/Layout';
import { ragApi } from '../services/ragApi';
import toast from 'react-hot-toast';
import { Send, Bot, User, Trash2, Sparkles } from 'lucide-react';

function Message({ msg }) {
  const isUser = msg.role === 'user';
  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${isUser ? 'bg-indigo-600' : 'bg-emerald-100'}`}>
        {isUser ? <User size={16} className="text-white" /> : <Bot size={16} className="text-emerald-700" />}
      </div>
      <div className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm ${isUser ? 'bg-indigo-600 text-white rounded-tr-sm' : 'bg-white border border-slate-100 text-slate-800 rounded-tl-sm shadow-sm'}`}>
        {msg.content}
        {msg.sources && msg.sources.length > 0 && (
          <div className="mt-2 pt-2 border-t border-slate-200">
            <p className="text-xs text-slate-500 font-medium">Sources:</p>
            {msg.sources.map((s, i) => (
              <p key={i} className="text-xs text-slate-400 mt-0.5">• {s}</p>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

const SUGGESTIONS = [
  "Explain the concept of double-entry bookkeeping",
  "What are the key IFRS standards for revenue recognition?",
  "How does audit risk assessment work?",
  "Explain the difference between direct and indirect costs",
  "What is the purpose of a trial balance?",
];

export default function AITutorPage() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: "Hello! I'm your AI CPA tutor powered by your study materials. Ask me anything about accounting, auditing, taxation, or any CPA topic. I'll search through your resources to give you accurate answers." }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async (text) => {
    const question = text || input.trim();
    if (!question || loading) return;

    setMessages(prev => [...prev, { role: 'user', content: question }]);
    setInput('');
    setLoading(true);

    try {
      const res = await ragApi.ask({ question });
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: res.data.answer,
        sources: res.data.sources
      }]);
    } catch {
      toast.error('Failed to get answer');
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="flex flex-col h-[calc(100vh-7rem)]">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-emerald-100 rounded-xl flex items-center justify-center">
              <Bot size={20} className="text-emerald-700" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-900">AI Tutor</h1>
              <p className="text-xs text-slate-500">Powered by your study materials</p>
            </div>
          </div>
          <button onClick={() => setMessages([messages[0]])} className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-slate-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors">
            <Trash2 size={14} /> Clear
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto bg-slate-50 rounded-2xl p-4 space-y-4 border border-slate-100">
          {messages.map((msg, i) => <Message key={i} msg={msg} />)}
          {loading && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-emerald-100 flex items-center justify-center">
                <Bot size={16} className="text-emerald-700" />
              </div>
              <div className="bg-white border border-slate-100 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm">
                <div className="flex gap-1">
                  {[0, 1, 2].map(i => (
                    <div key={i} className="w-2 h-2 bg-slate-300 rounded-full animate-bounce" style={{ animationDelay: `${i * 0.15}s` }}></div>
                  ))}
                </div>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Suggestions */}
        {messages.length <= 1 && (
          <div className="flex gap-2 mt-3 flex-wrap">
            {SUGGESTIONS.slice(0, 3).map((s, i) => (
              <button key={i} onClick={() => sendMessage(s)}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-white border border-slate-200 rounded-full text-xs text-slate-600 hover:border-indigo-300 hover:text-indigo-700 transition-colors">
                <Sparkles size={11} /> {s.slice(0, 40)}...
              </button>
            ))}
          </div>
        )}

        {/* Input */}
        <form onSubmit={(e) => { e.preventDefault(); sendMessage(); }} className="flex gap-3 mt-3">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask anything about CPA topics..."
            className="flex-1 px-4 py-3 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
            disabled={loading}
          />
          <button type="submit" disabled={loading || !input.trim()}
            className="px-4 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 disabled:opacity-50 transition-colors">
            <Send size={18} />
          </button>
        </form>
      </div>
    </Layout>
  );
}