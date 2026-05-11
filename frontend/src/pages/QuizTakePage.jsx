import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import Layout from '../components/Layout';
import { quizApi } from '../services/quizApi';
import toast from 'react-hot-toast';
import { Brain, ChevronRight, CheckCircle, Clock } from 'lucide-react';

export default function QuizTakePage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [answers, setAnswers] = useState({});
  const [currentQuestion, setCurrentQuestion] = useState(0);

  const { data: quiz, isLoading } = useQuery({
    queryKey: ['quiz', id],
    queryFn: () => quizApi.getQuiz(id).then(r => r.data)
  });

  const submitMutation = useMutation({
    mutationFn: (data) => quizApi.submitQuiz(id, data),
    onSuccess: (res) => {
      toast.success('Quiz submitted successfully!');
      navigate(`/quizzes/${id}/results`);
      queryClient.invalidateQueries(['quiz-history']);
    },
    onError: () => {
      toast.error('Failed to submit quiz');
    }
  });

  const handleAnswer = (questionId, answer) => {
    setAnswers(prev => ({ ...prev, [questionId]: answer }));
  };

  const handleSubmit = () => {
    const unanswered = quiz?.questions?.filter(q => !answers[q.id]);
    if (unanswered?.length > 0) {
      toast.error('Please answer all questions before submitting');
      return;
    }
    submitMutation.mutate({ answers });
  };

  if (isLoading) return (
    <Layout>
      <div className="flex justify-center py-20">
        <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    </Layout>
  );

  const questions = quiz?.questions || [];
  const currentQ = questions[currentQuestion];
  const progress = ((currentQuestion + 1) / questions.length) * 100;

  return (
    <Layout>
      <div className="mb-6">
        <button onClick={() => navigate(-1)} className="text-sm text-indigo-600 hover:underline mb-2 block">
          ← Back
        </button>
        <h1 className="text-2xl font-bold text-slate-900">{quiz?.title || 'Quiz'}</h1>
        <p className="text-slate-500 mt-1">Question {currentQuestion + 1} of {questions.length}</p>
      </div>

      {/* Progress bar */}
      <div className="mb-6">
        <div className="w-full bg-slate-100 rounded-full h-2">
          <div className="bg-indigo-600 h-2 rounded-full transition-all" style={{ width: `${progress}%` }}></div>
        </div>
      </div>

      {currentQ ? (
        <div className="bg-white rounded-xl border border-slate-100 p-6 shadow-sm">
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-slate-900 mb-4">{currentQ.question_text}</h2>
            
            {currentQ.options?.length > 0 ? (
              <div className="space-y-3">
                {currentQ.options.map((option, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleAnswer(currentQ.id, option)}
                    className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                      answers[currentQ.id] === option
                        ? 'border-indigo-600 bg-indigo-50'
                        : 'border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                        answers[currentQ.id] === option
                          ? 'border-indigo-600 bg-indigo-600'
                          : 'border-slate-300'
                      }`}>
                        {answers[currentQ.id] === option && <CheckCircle size={14} className="text-white" />}
                      </div>
                      <span className="text-slate-700">{option}</span>
                    </div>
                  </button>
                ))}
              </div>
            ) : (
              <textarea
                value={answers[currentQ.id] || ''}
                onChange={(e) => handleAnswer(currentQ.id, e.target.value)}
                placeholder="Type your answer here..."
                className="w-full p-4 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 min-h-32"
              />
            )}
          </div>

          <div className="flex justify-between items-center pt-4 border-t border-slate-100">
            <button
              onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
              disabled={currentQuestion === 0}
              className="px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>

            {currentQuestion === questions.length - 1 ? (
              <button
                onClick={handleSubmit}
                disabled={submitMutation.isPending}
                className="flex items-center gap-2 px-6 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-60"
              >
                <Brain size={18} />
                {submitMutation.isPending ? 'Submitting...' : 'Submit Quiz'}
              </button>
            ) : (
              <button
                onClick={() => setCurrentQuestion(Math.min(questions.length - 1, currentQuestion + 1))}
                className="flex items-center gap-2 px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
              >
                Next
                <ChevronRight size={18} />
              </button>
            )}
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-slate-100 p-6 shadow-sm text-center">
          <p className="text-slate-500">No questions available for this quiz.</p>
        </div>
      )}

      {/* Question navigator */}
      <div className="mt-6 bg-white rounded-xl border border-slate-100 p-4 shadow-sm">
        <p className="text-sm font-medium text-slate-700 mb-3">Jump to question:</p>
        <div className="flex flex-wrap gap-2">
          {questions.map((_, idx) => (
            <button
              key={idx}
              onClick={() => setCurrentQuestion(idx)}
              className={`w-8 h-8 rounded-lg text-sm font-medium ${
                currentQuestion === idx
                  ? 'bg-indigo-600 text-white'
                  : answers[questions[idx].id]
                  ? 'bg-emerald-100 text-emerald-700'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {idx + 1}
            </button>
          ))}
        </div>
      </div>
    </Layout>
  );
}
