import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import Layout from '../components/Layout';
import {
  BookOpen, Brain, Bot, Trophy, TrendingUp, Flame,
  Calendar, Star, ArrowRight, Zap
} from 'lucide-react';

function StatCard({ icon: Icon, label, value, color, to }) {
  const content = (
    <div className={`bg-white rounded-xl p-5 border border-slate-100 shadow-sm hover:shadow-md transition-shadow ${to ? 'cursor-pointer' : ''}`}>
      <div className={`inline-flex items-center justify-center w-10 h-10 rounded-lg mb-3 ${color}`}>
        <Icon size={20} className="text-white" />
      </div>
      <p className="text-2xl font-bold text-slate-900">{value ?? '—'}</p>
      <p className="text-sm text-slate-500 mt-0.5">{label}</p>
    </div>
  );
  return to ? <Link to={to}>{content}</Link> : content;
}

export default function DashboardPage() {
  const { user } = useAuth();

  const { data: summary } = useQuery({
    queryKey: ['progress-summary'],
    queryFn: () => progressApi.getSummary().then(r => r.data)
  });

  const { data: recommendations } = useQuery({
    queryKey: ['recommendations'],
    queryFn: () => progressApi.getRecommendations().then(r => r.data)
  });

  const { data: courses } = useQuery({
    queryKey: ['courses'],
    queryFn: () => courseApi.getCourses().then(r => r.data)
  });

  const { data: gamification } = useQuery({
    queryKey: ['gamification'],
    queryFn: () => progressApi.getGamificationProfile().then(r => r.data)
  });

  return (
    <Layout>
      {/* Welcome header */}
      <div className="bg-gradient-to-r from-indigo-600 to-indigo-700 rounded-2xl p-6 mb-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Welcome back, {user?.full_name?.split(' ')[0]}! 👋</h1>
            <p className="text-indigo-200 mt-1">Ready to continue your CPA journey?</p>
          </div>
          <div className="text-right hidden sm:block">
            <div className="flex items-center gap-2 bg-white/20 rounded-xl px-4 py-2">
              <Flame className="w-5 h-5 text-orange-300" />
              <span className="font-bold text-lg">{summary?.current_streak || 0}</span>
              <span className="text-indigo-200 text-sm">day streak</span>
            </div>
          </div>
        </div>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <StatCard icon={BookOpen} label="Topics Completed" value={summary?.topics_completed || 0} color="bg-indigo-500" to="/progress" />
        <StatCard icon={Brain} label="Avg Quiz Score" value={summary?.average_quiz_score ? `${summary.average_quiz_score}%` : '—'} color="bg-emerald-500" to="/quizzes" />
        <StatCard icon={Zap} label="Total XP" value={summary?.total_xp || 0} color="bg-amber-500" to="/leaderboard" />
        <StatCard icon={Trophy} label="Level" value={`Level ${summary?.level || 1}`} color="bg-purple-500" to="/leaderboard" />
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        {/* Quick actions */}
        <div className="md:col-span-2">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-2 gap-3">
            {[
              { to: '/ai-tutor', icon: Bot, label: 'Ask AI Tutor', desc: 'Get instant answers', color: 'bg-indigo-50 text-indigo-700 border-indigo-100' },
              { to: '/quizzes', icon: Brain, label: 'Take a Quiz', desc: 'Test your knowledge', color: 'bg-emerald-50 text-emerald-700 border-emerald-100' },
              { to: '/study-plan', icon: Calendar, label: 'Study Plan', desc: 'AI-generated schedule', color: 'bg-amber-50 text-amber-700 border-amber-100' },
              { to: '/flashcards', icon: Star, label: 'Flashcards', desc: 'Spaced repetition', color: 'bg-purple-50 text-purple-700 border-purple-100' },
            ].map(({ to, icon: Icon, label, desc, color }) => (
              <Link key={to} to={to}
                className={`flex items-center gap-3 p-4 rounded-xl border ${color} hover:shadow-sm transition-shadow`}>
                <Icon size={22} />
                <div>
                  <p className="font-medium text-sm">{label}</p>
                  <p className="text-xs opacity-70">{desc}</p>
                </div>
              </Link>
            ))}
          </div>

          {/* Courses */}
          {courses && courses.length > 0 && (
            <div className="mt-6">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-lg font-semibold text-slate-900">Your Courses</h2>
                <Link to="/courses" className="text-sm text-indigo-600 hover:underline flex items-center gap-1">
                  View all <ArrowRight size={14} />
                </Link>
              </div>
              <div className="space-y-2">
                {courses.slice(0, 3).map(course => (
                  <Link key={course.id} to={`/courses/${course.id}`}
                    className="flex items-center justify-between p-4 bg-white rounded-xl border border-slate-100 hover:border-indigo-200 hover:shadow-sm transition-all">
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 bg-indigo-100 rounded-lg flex items-center justify-center">
                        <BookOpen size={16} className="text-indigo-600" />
                      </div>
                      <div>
                        <p className="font-medium text-sm text-slate-900">{course.title}</p>
                        <p className="text-xs text-slate-500">{course.description?.slice(0, 50)}...</p>
                      </div>
                    </div>
                    <ArrowRight size={16} className="text-slate-400" />
                  </Link>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Sidebar panel */}
        <div className="space-y-4">
          {/* Gamification profile */}
          {gamification && (
            <div className="bg-white rounded-xl border border-slate-100 p-5 shadow-sm">
              <h3 className="font-semibold text-slate-900 mb-3 flex items-center gap-2">
                <Trophy size={16} className="text-amber-500" /> Your Rank
              </h3>
              <div className="text-center py-2">
                <p className="text-3xl font-bold text-indigo-600">{gamification.total_xp}</p>
                <p className="text-sm text-slate-500">Total XP</p>
                <span className="inline-block mt-2 px-3 py-1 bg-indigo-50 text-indigo-700 rounded-full text-xs font-medium">
                  {gamification.rank}
                </span>
              </div>
              <div className="mt-3 pt-3 border-t border-slate-100">
                <p className="text-xs text-slate-500 text-center">{gamification.badges_count} badges earned</p>
              </div>
            </div>
          )}

          {/* Recommendations */}
          {recommendations && recommendations.length > 0 && (
            <div className="bg-white rounded-xl border border-slate-100 p-5 shadow-sm">
              <h3 className="font-semibold text-slate-900 mb-3 flex items-center gap-2">
                <TrendingUp size={16} className="text-emerald-500" /> Recommended
              </h3>
              <div className="space-y-2">
                {recommendations.slice(0, 3).map((rec, i) => (
                  <div key={i} className="p-3 bg-slate-50 rounded-lg">
                    <p className="text-sm font-medium text-slate-800">{rec.title}</p>
                    <p className="text-xs text-slate-500 mt-0.5">{rec.reason}</p>
                    <span className={`inline-block mt-1.5 text-xs px-2 py-0.5 rounded-full font-medium ${
                      rec.priority === 'high' ? 'bg-red-100 text-red-700' :
                      rec.priority === 'medium' ? 'bg-amber-100 text-amber-700' :
                      'bg-green-100 text-green-700'
                    }`}>{rec.priority}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}