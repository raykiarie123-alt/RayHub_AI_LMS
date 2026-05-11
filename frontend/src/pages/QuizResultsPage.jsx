import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import Layout from '../components/Layout';
import { quizApi } from '../services/quizApi';
import { CheckCircle, XCircle, Trophy, Clock, Brain, ArrowLeft } from 'lucide-react';

export default function QuizResultsPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const { data: results, isLoading } = useQuery({
    queryKey: ['quiz-results', id],
    queryFn: () => quizApi.getResults(id).then(r => r.data)
  });

  if (isLoading) return (
    <Layout>
      <div className="flex justify-center py-20">
        <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    </Layout>
  );

  const score = results?.score || 0;
  const total = results?.total_questions || 0;
  const percentage = total > 0 ? Math.round((score / total) * 100) : 0;
  const passed = percentage >= 70;

  return (
    <Layout>
      <div className="mb-6">
        <button onClick={() => navigate(-1)} className="text-sm text-indigo-600 hover:underline mb-2 block">
          ← Back
        </button>
        <h1 className="text-2xl font-bold text-slate-900">Quiz Results</h1>
        <p className="text-slate-500 mt-1">{results?.quiz_title || 'Quiz'}</p>
      </div>

      {/* Score Card */}
      <div className={`bg-white rounded-xl border ${passed ? 'border-emerald-200' : 'border-amber-200'} p-6 shadow-sm mb-6`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className={`w-16 h-16 rounded-full flex items-center justify-center ${passed ? 'bg-emerald-100' : 'bg-amber-100'}`}>
              {passed ? <Trophy size={32} className="text-emerald-600" /> : <Brain size={32} className="text-amber-600" />}
            </div>
            <div>
              <p className="text-3xl font-bold text-slate-900">{percentage}%</p>
              <p className={`text-sm font-medium ${passed ? 'text-emerald-600' : 'text-amber-600'}`}>
                {passed ? 'Passed!' : 'Keep practicing!'}
              </p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm text-slate-500">Score</p>
            <p className="text-lg font-semibold text-slate-900">{score} / {total}</p>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-white rounded-xl border border-slate-100 p-4 shadow-sm">
          <div className="flex items-center gap-2 mb-2">
            <Clock size={18} className="text-slate-400" />
            <p className="text-xs text-slate-500">Time Taken</p>
          </div>
          <p className="text-lg font-semibold text-slate-900">{results?.time_taken || 'N/A'}</p>
        </div>
        <div className="bg-white rounded-xl border border-slate-100 p-4 shadow-sm">
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle size={18} className="text-emerald-500" />
            <p className="text-xs text-slate-500">Correct</p>
          </div>
          <p className="text-lg font-semibold text-slate-900">{score}</p>
        </div>
        <div className="bg-white rounded-xl border border-slate-100 p-4 shadow-sm">
          <div className="flex items-center gap-2 mb-2">
            <XCircle size={18} className="text-red-500" />
            <p className="text-xs text-slate-500">Incorrect</p>
          </div>
          <p className="text-lg font-semibold text-slate-900">{total - score}</p>
        </div>
      </div>

      {/* Question Review */}
      <div className="bg-white rounded-xl border border-slate-100 p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-900 mb-4">Question Review</h2>
        <div className="space-y-4">
          {results?.answers?.map((answer, idx) => (
            <div
              key={idx}
              className={`p-4 rounded-lg border-2 ${
                answer.is_correct
                  ? 'border-emerald-200 bg-emerald-50'
                  : 'border-red-200 bg-red-50'
              }`}
            >
              <div className="flex items-start gap-3">
                <div className={`mt-0.5 ${answer.is_correct ? 'text-emerald-600' : 'text-red-600'}`}>
                  {answer.is_correct ? <CheckCircle size={18} /> : <XCircle size={18} />}
                </div>
                <div className="flex-1">
                  <p className="font-medium text-slate-900 mb-2">
                    Q{idx + 1}: {answer.question_text}
                  </p>
                  <div className="space-y-1 text-sm">
                    <p className="text-slate-600">
                      <span className="font-medium">Your answer:</span> {answer.user_answer}
                    </p>
                    {!answer.is_correct && (
                      <p className="text-emerald-700">
                        <span className="font-medium">Correct answer:</span> {answer.correct_answer}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Actions */}
      <div className="mt-6 flex gap-3">
        <Link
          to="/courses"
          className="flex items-center gap-2 px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
        >
          <ArrowLeft size={18} />
          Back to Courses
        </Link>
        <Link
          to="/quiz-history"
          className="px-6 py-2 border border-slate-200 text-slate-700 rounded-lg hover:bg-slate-50"
        >
          View History
        </Link>
      </div>
    </Layout>
  );
}
