import { useQuery } from '@tanstack/react-query';
import Layout from '../components/Layout';
import { progressApi } from '../services/progressApi';
import { RadialBarChart, RadialBar, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { TrendingUp, BookOpen, Brain, Clock, Flame, Trophy, AlertTriangle } from 'lucide-react';

function StatCard({ icon: Icon, label, value, color }) {
  return (
    <div className="bg-white rounded-xl border border-slate-100 p-5 shadow-sm">
      <div className={`inline-flex items-center justify-center w-10 h-10 rounded-lg mb-3 ${color}`}>
        <Icon size={20} className="text-white" />
      </div>
      <p className="text-2xl font-bold text-slate-900">{value ?? '—'}</p>
      <p className="text-sm text-slate-500 mt-0.5">{label}</p>
    </div>
  );
}

export default function ProgressPage() {
  const { data: summary } = useQuery({
    queryKey: ['progress-summary'],
    queryFn: () => progressApi.getSummary().then(r => r.data)
  });

  const { data: weakAreas } = useQuery({
    queryKey: ['weak-areas'],
    queryFn: () => progressApi.getWeakAreas().then(r => r.data)
  });

  const { data: progress } = useQuery({
    queryKey: ['my-progress'],
    queryFn: () => progressApi.getMyProgress().then(r => r.data)
  });

  const { data: badges } = useQuery({
    queryKey: ['badges'],
    queryFn: () => progressApi.getBadges().then(r => r.data)
  });

  const chartData = progress?.filter(p => p.quiz_attempts_count > 0).slice(0, 8).map(p => ({
    name: p.topic_id ? `Topic ${p.topic_id}` : 'Unknown',
    score: Math.round(p.average_quiz_score),
    attempts: p.quiz_attempts_count
  })) || [];

  return (
    <Layout title="Progress">
      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <StatCard icon={BookOpen} label="Topics Completed" value={summary?.topics_completed || 0} color="bg-indigo-500" />
        <StatCard icon={Brain} label="Avg Quiz Score" value={summary?.average_quiz_score ? `${summary.average_quiz_score}%` : '—'} color="bg-emerald-500" />
        <StatCard icon={Clock} label="Study Time" value={summary?.total_study_time_minutes ? `${Math.round(summary.total_study_time_minutes / 60)}h` : '0h'} color="bg-amber-500" />
        <StatCard icon={Flame} label="Current Streak" value={`${summary?.current_streak || 0} days`} color="bg-orange-500" />
      </div>

      <div className="grid md:grid-cols-2 gap-6 mb-6">
        {/* Score chart */}
        <div className="bg-white rounded-xl border border-slate-100 p-5 shadow-sm">
          <h2 className="font-semibold text-slate-900 mb-4">Quiz Performance by Topic</h2>
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 10 }} />
                <Tooltip />
                <Bar dataKey="score" fill="#4f46e5" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-48 text-slate-400 text-sm">
              No quiz data yet. Take some quizzes!
            </div>
          )}
        </div>

        {/* XP & Rank */}
        <div className="bg-white rounded-xl border border-slate-100 p-5 shadow-sm">
          <h2 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
            <Trophy size={16} className="text-amber-500" /> Rank & XP
          </h2>
          <div className="text-center py-4">
            <div className="inline-flex items-center justify-center w-24 h-24 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full text-white mb-4">
              <div>
                <p className="text-2xl font-bold">{summary?.level || 1}</p>
                <p className="text-xs opacity-80">Level</p>
              </div>
            </div>
            <p className="text-3xl font-bold text-slate-900">{summary?.total_xp || 0} XP</p>
            <span className="inline-block mt-2 px-3 py-1 bg-indigo-50 text-indigo-700 rounded-full text-sm font-medium">
              {summary?.rank || 'Beginner'}
            </span>
          </div>
          <div className="grid grid-cols-2 gap-3 mt-4">
            <div className="bg-slate-50 rounded-lg p-3 text-center">
              <p className="text-lg font-bold text-slate-900">{summary?.current_streak || 0}</p>
              <p className="text-xs text-slate-500">Current Streak</p>
            </div>
            <div className="bg-slate-50 rounded-lg p-3 text-center">
              <p className="text-lg font-bold text-slate-900">{summary?.longest_streak || 0}</p>
              <p className="text-xs text-slate-500">Best Streak</p>
            </div>
          </div>
        </div>
      </div>

      {/* Weak Areas */}
      {weakAreas && weakAreas.length > 0 && (
        <div className="bg-white rounded-xl border border-red-100 p-5 shadow-sm mb-6">
          <h2 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
            <AlertTriangle size={16} className="text-red-500" /> Areas Needing Attention
          </h2>
          <div className="grid md:grid-cols-2 gap-3">
            {weakAreas.map((area, i) => (
              <div key={i} className="flex items-center justify-between p-3 bg-red-50 rounded-lg border border-red-100">
                <div>
                  <p className="text-sm font-medium text-slate-900">{area.topic_title}</p>
                  <p className="text-xs text-slate-500">{area.unit_title} · {area.attempts} attempts</p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold text-red-600">{area.average_score?.toFixed(0)}%</p>
                  <p className="text-xs text-red-400">avg score</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Badges */}
      {badges && badges.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-100 p-5 shadow-sm">
          <h2 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
            <Trophy size={16} className="text-amber-500" /> Badges
          </h2>
          <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
            {badges.map((badge, i) => (
              <div key={i} className={`text-center p-3 rounded-xl border ${badge.earned ? 'border-amber-200 bg-amber-50' : 'border-slate-100 bg-slate-50 opacity-50'}`}>
                <div className="text-2xl mb-1">{badge.icon || '🏆'}</div>
                <p className="text-xs font-medium text-slate-700 leading-tight">{badge.name}</p>
                {badge.earned && <p className="text-xs text-amber-600 mt-0.5">Earned</p>}
              </div>
            ))}
          </div>
        </div>
      )}
    </Layout>
  );
}