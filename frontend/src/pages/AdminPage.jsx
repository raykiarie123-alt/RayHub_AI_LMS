import { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import Layout from '../components/Layout';
import api from '../services/api';
import toast from 'react-hot-toast';
import {
  Users,
  FileText,
  Brain,
  TrendingUp,
  Shield,
  CheckCircle,
  Bot,
  Activity,
  Flame,
  Medal,
  BarChart2,
  MessageSquare,
  RefreshCw,
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts';

function StatCard({ icon: Icon, label, value, color, sub }) {
  return (
    <div className="bg-white rounded-xl border border-slate-100 p-5 shadow-sm">
      <div className={`inline-flex items-center justify-center w-10 h-10 rounded-lg mb-3 ${color}`}>
        <Icon size={20} className="text-white" />
      </div>
      <p className="text-2xl font-bold text-slate-900">{value ?? '—'}</p>
      <p className="text-sm text-slate-500 mt-0.5">{label}</p>
      {sub && <p className="text-xs text-indigo-600 mt-1 font-medium">{sub}</p>}
    </div>
  );
}

const TABS = ['Overview', 'Students', 'Resources', 'AI Interactions'];

export default function AdminPage() {
  const [tab, setTab] = useState('Overview');
  const qc = useQueryClient();

  const { data: dashboard, isLoading: dashLoading } = useQuery({
    queryKey: ['admin-dashboard'],
    queryFn: () => api.get('/admin/dashboard').then(r => r.data),
  });

  const { data: analytics } = useQuery({
    queryKey: ['admin-analytics'],
    queryFn: () => api.get('/admin/analytics').then(r => r.data),
  });

  const { data: engagement } = useQuery({
    queryKey: ['admin-engagement'],
    queryFn: () => api.get('/admin/student-engagement').then(r => r.data),
  });

  const { data: users } = useQuery({
    queryKey: ['admin-users'],
    queryFn: () => api.get('/admin/users').then(r => r.data),
    enabled: tab === 'Students',
  });

  const { data: resources } = useQuery({
    queryKey: ['admin-resources'],
    queryFn: () => api.get('/admin/resources').then(r => r.data),
    enabled: tab === 'Resources',
  });

  const { data: aiInteractions } = useQuery({
    queryKey: ['admin-ai-interactions'],
    queryFn: () => api.get('/admin/ai-interactions').then(r => r.data),
    enabled: tab === 'AI Interactions',
  });

  const handleApprove = async (id) => {
    try {
      await api.post('/admin/resources/approve', null, { params: { resource_id: id } });
      toast.success('Resource approved');
      qc.invalidateQueries({ queryKey: ['admin-resources'] });
    } catch {
      toast.error('Approval failed');
    }
  };

  const topStudentsChartData = engagement?.top_students?.slice(0, 5).map((s, i) => ({
    name: `#${i + 1}`,
    xp: s.total_xp,
  })) || [];

  const levelColors = {
    foundation: '#10b981',
    intermediate: '#f59e0b',
    advanced: '#ef4444',
    'post-qualification': '#8b5cf6',
  };

  const levelDist = users ? Object.entries(
    users.reduce((acc, u) => {
      const lv = u.student_level || 'foundation';
      acc[lv] = (acc[lv] || 0) + 1;
      return acc;
    }, {})
  ).map(([name, value]) => ({ name, value })) : [];

  return (
    <Layout title="Admin Dashboard">
      <div className="flex items-center gap-2 mb-5 p-3 bg-amber-50 border border-amber-200 rounded-xl">
        <Shield size={16} className="text-amber-600" />
        <p className="text-sm text-amber-700 font-medium">Admin Panel — Manage platform content, users, and analytics</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 border-b border-slate-200 overflow-x-auto">
        {TABS.map(t => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2.5 text-sm font-medium whitespace-nowrap border-b-2 transition-colors ${
              tab === t
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-slate-500 hover:text-slate-900'
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {/* OVERVIEW TAB */}
      {tab === 'Overview' && (
        <div className="space-y-6">
          {dashLoading ? (
            <div className="flex justify-center py-12">
              <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
            </div>
          ) : (
            <>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                <StatCard icon={Users} label="Total Students" value={dashboard?.total_students || 0} color="bg-indigo-500" />
                <StatCard icon={Activity} label="Active Students" value={dashboard?.active_students || 0} color="bg-emerald-500" />
                <StatCard icon={FileText} label="Resources" value={dashboard?.total_resources || 0} color="bg-amber-500" />
                <StatCard icon={Brain} label="Quizzes Taken" value={dashboard?.total_quizzes_taken || 0} color="bg-purple-500" />
                <StatCard icon={CheckCircle} label="Topics Done" value={dashboard?.total_topics_completed || 0} color="bg-cyan-500" />
                <StatCard icon={Bot} label="AI Interactions" value={dashboard?.total_ai_interactions || 0} color="bg-rose-500" />
              </div>

              <div className="grid md:grid-cols-3 gap-5">
                {/* Quiz Analytics */}
                <div className="bg-white rounded-xl border border-slate-100 p-5 shadow-sm">
                  <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
                    <BarChart2 size={16} className="text-indigo-500" /> Quiz Analytics
                  </h3>
                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-500">Total Quizzes</span>
                      <span className="font-semibold">{analytics?.total_quizzes || 0}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-500">Completions</span>
                      <span className="font-semibold">{analytics?.quiz_completion_rate || 0}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-500">Avg Score</span>
                      <span className="font-semibold text-indigo-600">{analytics?.average_quiz_score || 0}%</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-500">Weak Areas</span>
                      <span className="font-semibold text-red-500">{analytics?.students_with_weak_areas || 0}</span>
                    </div>
                  </div>
                </div>

                {/* Resources Analytics */}
                <div className="bg-white rounded-xl border border-slate-100 p-5 shadow-sm">
                  <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
                    <FileText size={16} className="text-amber-500" /> Resources
                  </h3>
                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-500">Total</span>
                      <span className="font-semibold">{analytics?.total_resources || 0}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-500">Indexed (RAG)</span>
                      <span className="font-semibold text-emerald-600">{analytics?.indexed_resources || 0}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-500">Awaiting Approval</span>
                      <span className="font-semibold text-amber-600">—</span>
                    </div>
                  </div>
                </div>

                {/* AI Interactions */}
                <div className="bg-white rounded-xl border border-slate-100 p-5 shadow-sm">
                  <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
                    <Bot size={16} className="text-rose-500" /> AI Tutor Usage
                  </h3>
                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-500">Total Interactions</span>
                      <span className="font-semibold">{analytics?.total_ai_interactions || 0}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-500">Unique Users</span>
                      <span className="font-semibold">{analytics?.unique_ai_users || 0}</span>
                    </div>
                    <div className="mt-3 pt-3 border-t border-slate-100">
                      <p className="text-xs text-slate-400 font-medium mb-2">Top AI Users</p>
                      {analytics?.top_ai_users?.map((u, i) => (
                        <div key={i} className="flex justify-between text-xs text-slate-600 py-0.5">
                          <span className="truncate">{u.full_name}</span>
                          <span className="font-medium text-rose-600 ml-2">{u.interactions}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Engagement */}
              <div className="grid md:grid-cols-2 gap-5">
                <div className="bg-white rounded-xl border border-slate-100 p-5 shadow-sm">
                  <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
                    <Flame size={16} className="text-orange-500" /> Engagement
                  </h3>
                  <div className="space-y-3 mb-4">
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-500">Students with Active Streaks</span>
                      <span className="font-semibold text-orange-600">{engagement?.students_with_active_streaks || 0}</span>
                    </div>
                  </div>
                </div>

                <div className="bg-white rounded-xl border border-slate-100 p-5 shadow-sm">
                  <h3 className="font-semibold text-slate-900 mb-3 flex items-center gap-2">
                    <Medal size={16} className="text-amber-500" /> Top XP Earners
                  </h3>
                  <ResponsiveContainer width="100%" height={150}>
                    <BarChart data={topStudentsChartData} margin={{ top: 0, right: 0, bottom: 0, left: -20 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                      <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                      <YAxis tick={{ fontSize: 11 }} />
                      <Tooltip />
                      <Bar dataKey="xp" fill="#4f46e5" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* STUDENTS TAB */}
      {tab === 'Students' && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-slate-900">{users?.length || 0} Users</h2>
            <button
              onClick={() => qc.invalidateQueries({ queryKey: ['admin-users'] })}
              className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-indigo-600 px-3 py-1.5 rounded-lg hover:bg-indigo-50"
            >
              <RefreshCw size={14} /> Refresh
            </button>
          </div>

          {levelDist.length > 0 && (
            <div className="bg-white rounded-xl border border-slate-100 p-5 shadow-sm mb-5">
              <h3 className="font-semibold text-slate-900 mb-3 text-sm">Students by Level</h3>
              <div className="flex gap-3 flex-wrap">
                {levelDist.map(({ name, value }) => (
                  <div key={name} className="flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-50">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: levelColors[name] || '#64748b' }} />
                    <span className="text-sm capitalize text-slate-700">{name}</span>
                    <span className="text-sm font-bold text-slate-900">{value}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="bg-white rounded-xl border border-slate-100 shadow-sm overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="text-left px-4 py-3 text-xs font-medium text-slate-500">Name</th>
                    <th className="text-left px-4 py-3 text-xs font-medium text-slate-500">Role</th>
                    <th className="text-left px-4 py-3 text-xs font-medium text-slate-500">Level</th>
                    <th className="text-left px-4 py-3 text-xs font-medium text-slate-500">XP</th>
                    <th className="text-left px-4 py-3 text-xs font-medium text-slate-500">Quizzes</th>
                    <th className="text-left px-4 py-3 text-xs font-medium text-slate-500">AI Uses</th>
                    <th className="text-left px-4 py-3 text-xs font-medium text-slate-500">Rank</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-50">
                  {users?.map(user => (
                    <tr key={user.id} className="hover:bg-slate-50">
                      <td className="px-4 py-3">
                        <p className="font-medium text-slate-900">{user.full_name}</p>
                        <p className="text-xs text-slate-400">{user.email}</p>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                          user.role === 'admin' ? 'bg-red-100 text-red-700'
                          : user.role === 'tutor' ? 'bg-amber-100 text-amber-700'
                          : 'bg-blue-100 text-blue-700'
                        }`}>
                          {user.role}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <span className="text-xs text-slate-600 capitalize">{user.student_level || 'foundation'}</span>
                      </td>
                      <td className="px-4 py-3 font-medium text-indigo-600">{user.total_xp}</td>
                      <td className="px-4 py-3 text-slate-700">{user.quizzes_completed}</td>
                      <td className="px-4 py-3 text-rose-600 font-medium">{user.ai_interactions}</td>
                      <td className="px-4 py-3 text-xs text-slate-500">{user.rank}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* RESOURCES TAB */}
      {tab === 'Resources' && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-slate-900">{resources?.length || 0} Resources</h2>
          </div>
          <div className="bg-white rounded-xl border border-slate-100 shadow-sm overflow-hidden">
            <div className="divide-y divide-slate-50">
              {resources?.map(r => (
                <div key={r.id} className="flex items-center justify-between px-5 py-3.5 hover:bg-slate-50">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-slate-900 truncate">{r.title}</p>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className="text-xs text-slate-400 capitalize">{r.resource_type}</span>
                      <span className="text-xs text-slate-300">·</span>
                      <span className={`text-xs capitalize ${
                        r.level === 'advanced' ? 'text-rose-600' : r.level === 'intermediate' ? 'text-amber-600' : 'text-emerald-600'
                      }`}>{r.level}</span>
                      {r.is_indexed && (
                        <>
                          <span className="text-xs text-slate-300">·</span>
                          <span className="text-xs text-emerald-600">Indexed</span>
                        </>
                      )}
                    </div>
                  </div>
                  {r.is_approved ? (
                    <span className="flex items-center gap-1 text-xs text-emerald-600 ml-4">
                      <CheckCircle size={13} /> Approved
                    </span>
                  ) : (
                    <button
                      onClick={() => handleApprove(r.id)}
                      className="ml-4 text-xs px-3 py-1.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                    >
                      Approve
                    </button>
                  )}
                </div>
              ))}
              {!resources?.length && (
                <p className="text-center text-slate-400 text-sm py-10">No resources found</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* AI INTERACTIONS TAB */}
      {tab === 'AI Interactions' && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-slate-900 flex items-center gap-2">
              <MessageSquare size={18} className="text-rose-500" />
              Recent AI Tutor Interactions
            </h2>
            <div className="flex items-center gap-2 text-sm text-slate-500">
              <Bot size={14} />
              <span>{analytics?.total_ai_interactions || 0} total interactions</span>
            </div>
          </div>

          <div className="space-y-3">
            {aiInteractions?.map(item => (
              <div key={item.id} className="bg-white rounded-xl border border-slate-100 p-4 shadow-sm">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <div className="w-6 h-6 bg-indigo-100 rounded-full flex items-center justify-center">
                        <Users size={12} className="text-indigo-600" />
                      </div>
                      <span className="text-sm font-medium text-slate-900">{item.user_name}</span>
                      <span className="text-xs text-slate-400">
                        {item.created_at ? new Date(item.created_at).toLocaleDateString() : ''}
                      </span>
                    </div>
                    <div className="bg-indigo-50 rounded-lg p-3 mb-2">
                      <p className="text-xs font-medium text-indigo-700 mb-1">Question:</p>
                      <p className="text-sm text-slate-700">{item.question}</p>
                    </div>
                    <div className="bg-slate-50 rounded-lg p-3">
                      <p className="text-xs font-medium text-slate-500 mb-1">AI Response (preview):</p>
                      <p className="text-sm text-slate-600 line-clamp-2">{item.answer}</p>
                    </div>
                  </div>
                </div>
              </div>
            ))}
            {!aiInteractions?.length && (
              <div className="text-center py-12 text-slate-400">
                <Bot size={40} className="mx-auto mb-3 opacity-40" />
                <p>No AI interactions yet</p>
              </div>
            )}
          </div>
        </div>
      )}
    </Layout>
  );
}
