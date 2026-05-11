import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import Layout from '../components/Layout';
import { quizApi } from '../services/quizApi';
import { Brain, Clock, Trophy, CheckCircle, TrendingUp } from 'lucide-react';

export default function QuizHistoryPage() {
  const { data: history, isLoading } = useQuery({
    queryKey: ['quiz-history'],
    queryFn: () => quizApi.getHistory().then(r => r.data)
  });

  const totalQuizzes = history?.length || 0;
  const averageScore = history?.length > 0 
    ? Math.round(history.reduce((sum, h) => sum + (h.percentage || 0), 0) / history.length)
    : 0;
  const passedCount = history?.filter(h => h.percentage >= 70).length || 0;

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
        <h1 className="text-2xl font-bold text-slate-900">Quiz History</h1>
        <p className="text-slate-500 mt-1">View your past quiz attempts</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-white rounded-xl border border-slate-100 p-4 shadow-sm">
          <div className="flex items-center gap-2 mb-2">
            <Brain size={18} className="text-indigo-500" />
            <p className="text-xs text-slate-500">Total Quizzes</p>
          </div>
          <p className="text-2xl font-bold text-slate-900">{totalQuizzes}</p>
        </div>
        <div className="bg-white rounded-xl border border-slate-100 p-4 shadow-sm">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp size={18} className="text-emerald-500" />
            <p className="text-xs text-slate-500">Average Score</p>
          </div>
          <p className="text-2xl font-bold text-slate-900">{averageScore}%</p>
        </div>
        <div className="bg-white rounded-xl border border-slate-100 p-4 shadow-sm">
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle size={18} className="text-emerald-500" />
            <p className="text-xs text-slate-500">Passed</p>
          </div>
          <p className="text-2xl font-bold text-slate-900">{passedCount}</p>
        </div>
      </div>

      {/* History List */}
      <div className="bg-white rounded-xl border border-slate-100 shadow-sm">
        {history?.length > 0 ? (
          <div className="divide-y divide-slate-100">
            {history.map((attempt) => {
              const passed = attempt.percentage >= 70;
              return (
                <Link
                  key={attempt.id}
                  to={`/quizzes/${attempt.quiz_id}/results`}
                  className="block p-4 hover:bg-slate-50 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 mb-1">
                        <h3 className="font-medium text-slate-900 truncate">{attempt.quiz_title}</h3>
                        {passed && (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-emerald-100 text-emerald-700 rounded-full text-xs font-medium">
                            <CheckCircle size={12} /> Passed
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-4 text-xs text-slate-500">
                        <span className="flex items-center gap-1">
                          <Clock size={12} />
                          {attempt.completed_at || 'Recently'}
                        </span>
                        <span>Score: {attempt.score} / {attempt.total_questions}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <p className={`text-lg font-bold ${passed ? 'text-emerald-600' : 'text-amber-600'}`}>
                          {attempt.percentage}%
                        </p>
                      </div>
                      <Trophy size={18} className="text-slate-400" />
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        ) : (
          <div className="p-12 text-center">
            <Brain size={48} className="mx-auto mb-4 text-slate-300" />
            <p className="text-slate-500 mb-4">No quiz attempts yet</p>
            <Link
              to="/courses"
              className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
            >
              Take Your First Quiz
            </Link>
          </div>
        )}
      </div>
    </Layout>
  );
}
