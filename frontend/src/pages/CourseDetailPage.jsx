import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import Layout from '../components/Layout';
import { courseApi } from '../services/courseApi';
import { quizApi } from '../services/quizApi';
import { ragApi } from '../services/ragApi';
import toast from 'react-hot-toast';
import { ChevronDown, ChevronRight, Brain, Bot, BookOpen, FileText } from 'lucide-react';

function TopicItem({ topic }) {
  const [expanded, setExpanded] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [asking, setAsking] = useState(false);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');

  const handleGenerateQuiz = async () => {
    setGenerating(true);
    try {
      const res = await quizApi.generateQuiz({ topic_id: topic.id, number_of_questions: 5, difficulty: 'intermediate' });
      toast.success('Quiz generated!');
      window.location.href = `/quizzes/${res.data.id}/take`;
    } catch {
      toast.error('Failed to generate quiz');
    } finally {
      setGenerating(false);
    }
  };

  const handleAsk = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;
    setAsking(true);
    try {
      const res = await ragApi.askTopic({ question, topic_id: topic.id });
      setAnswer(res.data.answer);
    } catch {
      toast.error('Failed to get answer');
    } finally {
      setAsking(false);
    }
  };

  return (
    <div className="border border-slate-100 rounded-lg overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between p-4 hover:bg-slate-50 transition-colors text-left"
      >
        <div className="flex items-center gap-3">
          <div className="w-7 h-7 bg-indigo-50 rounded-lg flex items-center justify-center">
            <BookOpen size={14} className="text-indigo-600" />
          </div>
          <div>
            <p className="font-medium text-sm text-slate-900">{topic.title}</p>
            {topic.estimated_hours && (
              <p className="text-xs text-slate-400">{topic.estimated_hours}h estimated</p>
            )}
          </div>
        </div>
        {expanded ? <ChevronDown size={16} className="text-slate-400" /> : <ChevronRight size={16} className="text-slate-400" />}
      </button>

      {expanded && (
        <div className="px-4 pb-4 border-t border-slate-100 bg-slate-50/50">
          {topic.description && (
            <p className="text-sm text-slate-600 mt-3 mb-3">{topic.description}</p>
          )}
          {topic.content && (
            <div className="bg-white rounded-lg p-3 mb-3 text-sm text-slate-700 max-h-40 overflow-y-auto border border-slate-100">
              {topic.content}
            </div>
          )}

          {/* AI Q&A */}
          <form onSubmit={handleAsk} className="mb-3">
            <div className="flex gap-2">
              <input
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask AI about this topic..."
                className="flex-1 px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <button type="submit" disabled={asking}
                className="px-3 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700 disabled:opacity-60 flex items-center gap-1">
                <Bot size={14} /> {asking ? '...' : 'Ask'}
              </button>
            </div>
          </form>

          {answer && (
            <div className="bg-indigo-50 rounded-lg p-3 text-sm text-slate-700 mb-3 border border-indigo-100">
              <p className="font-medium text-indigo-800 mb-1">AI Answer:</p>
              {answer}
            </div>
          )}

          <div className="flex gap-2">
            <button onClick={handleGenerateQuiz} disabled={generating}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-600 text-white rounded-lg text-xs hover:bg-emerald-700 disabled:opacity-60">
              <Brain size={13} /> {generating ? 'Generating...' : 'Generate Quiz'}
            </button>
            <Link to={`/resources?topic_id=${topic.id}`}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-200 text-slate-700 rounded-lg text-xs hover:bg-slate-300">
              <FileText size={13} /> Resources
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}

export default function CourseDetailPage() {
  const { id } = useParams();
  const [expandedUnit, setExpandedUnit] = useState(null);

  const { data: course, isLoading } = useQuery({
    queryKey: ['course', id],
    queryFn: () => courseApi.getCourse(id).then(r => r.data)
  });

  if (isLoading) return (
    <Layout>
      <div className="flex justify-center py-20">
        <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    </Layout>
  );

  return (
    <Layout>
      <div className="mb-6">
        <Link to="/courses" className="text-sm text-indigo-600 hover:underline mb-2 block">← Back to Courses</Link>
        <h1 className="text-2xl font-bold text-slate-900">{course?.title}</h1>
        <p className="text-slate-500 mt-1">{course?.description}</p>
      </div>

      <div className="space-y-4">
        {course?.units?.map(unit => (
          <div key={unit.id} className="bg-white rounded-xl border border-slate-100 shadow-sm overflow-hidden">
            <button
              onClick={() => setExpandedUnit(expandedUnit === unit.id ? null : unit.id)}
              className="w-full flex items-center justify-between p-5 hover:bg-slate-50 transition-colors"
            >
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 bg-indigo-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">
                  {unit.order || '?'}
                </div>
                <div className="text-left">
                  <p className="font-semibold text-slate-900">{unit.title}</p>
                  <p className="text-xs text-slate-400">{unit.topics?.length || 0} topics</p>
                </div>
              </div>
              {expandedUnit === unit.id ? <ChevronDown size={18} className="text-slate-400" /> : <ChevronRight size={18} className="text-slate-400" />}
            </button>

            {expandedUnit === unit.id && (
              <div className="px-5 pb-5 space-y-2 border-t border-slate-100">
                {unit.topics?.length > 0 ? (
                  unit.topics.map(topic => <TopicItem key={topic.id} topic={topic} />)
                ) : (
                  <p className="text-sm text-slate-400 py-3">No topics yet.</p>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </Layout>
  );
}