import { useQuery } from '@tanstack/react-query';
import Layout from '../components/Layout';
import api from '../services/api';
import { Users, FileText, Brain, TrendingUp, Shield, CheckCircle } from 'lucide-react';

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

export default function AdminPage() {
  const { data: dashboard } = useQuery({
    queryKey: ['admin-dashboard'],
    queryFn: () => api.get('/admin/dashboard').then(r => r.data)
  });

  const { data: analytics } = useQuery({
    queryKey: ['admin-analytics'],
    queryFn: () => api.get('/admin/analytics').then(r => r.data)
  });

  const { data: users } = useQuery({
    queryKey: ['admin-users'],
    queryFn: () => api.get('/admin/users').then(r => r.data)
  });

  const { data: resources } = useQuery({
    queryKey: ['admin-resources'],
    queryFn: () => api.get('/admin/resources').then(r => r.data)
  });

  const handleApprove = async (id) => {
    try {
      await api.post('/admin/resources/approve', null, { params: { resource_id: id } });
    } catch {}
  };

  return (
    <Layout title="Admin Dashboard">
      <div className="flex items-center gap-2 mb-6 p-3 bg-amber-50 border border-amber-200 rounded-xl">
        <Shield size={16} className="text-amber-600" />
        <p className="text-sm text-amber-700 font-medium">Admin Panel — Manage platform content and users</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <StatCard icon={Users} label="Total Students" value={dashboard?.total_students || 0} color="bg-indigo-500" />
        <StatCard icon={Users} label="Active Students" value={dashboard?.active_students || 0} color="bg-emerald-500" />
        <StatCard icon={FileText} label="Total Resources" value={dashboard?.total_resources || 0} color="bg-amber-500" />
        <StatCard icon={Brain} label="Quizzes Taken" value={dashboard?.total_quizzes_taken || 0} color="bg-purple-500" />
      </div>

      {/* Analytics */}
      {analytics && (
        <div className="grid md:grid-cols-3 gap-4 mb-6">
          <div className="bg-white rounded-xl border border-slate-100 p-5 shadow-sm">
            <h3 className="font-semibold text-slate-900 mb-3 flex items-center gap-2"><TrendingUp size={16} className="text-indigo-500" /> Quiz Analytics</h3>
            <div className="space-y-2">
              <div className="flex justify-between text-sm"><span className="text-slate-500">Total Quizzes</span><span className="font-medium">{analytics.total_quizzes}</span></div>
              <div className="flex justify-between text-sm"><span className="text-slate-500">Completions</span><span className="font-medium">{analytics.quiz_completion_rate}</span></div>
              <div className="flex justify-between text-sm"><span className="text-slate-500">Avg Score</span><span className="font-medium">{analytics.average_quiz_score}%</span></div>
            </div>
          </div>
          <div className="bg-white rounded-xl border border-slate-100 p-5 shadow-sm">
            <h3 className="font-semibold text-slate-900 mb-3 flex items-center gap-2"><FileText size={16} className="text-amber-500" /> Resources</h3>
            <div className="space-y-2">
              <div className="flex justify-between text-sm"><span className="text-slate-500">Total</span><span className="font-medium">{analytics.total_resources}</span></div>
              <div className="flex justify-between text-sm"><span className="text-slate-500">Indexed</span><span className="font-medium">{analytics.indexed_resources}</span></div>
              <div className="flex justify-between text-sm"><span className="text-slate-500">Weak Areas</span><span className="font-medium text-red-500">{analytics.students_with_weak_areas}</span></div>
            </div>
          </div>
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-6">
        {/* Users table */}
        <div className="bg-white rounded-xl border border-slate-100 shadow-sm overflow-hidden">
          <div className="p-4 border-b border-slate-100">
            <h2 className="font-semibold text-slate-900 flex items-center gap-2"><Users size={16} /> Users</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50">
                <tr>
                  <th className="text-left px-4 py-2.5 text-xs font-medium text-slate-500">Name</th>
                  <th className="text-left px-4 py-2.5 text-xs font-medium text-slate-500">Role</th>
                  <th className="text-left px-4 py-2.5 text-xs font-medium text-slate-500">XP</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {users?.slice(0, 10).map(user => (
                  <tr key={user.id} className="hover:bg-slate-50">
                    <td className="px-4 py-2.5">
                      <p className="font-medium text-slate-900">{user.full_name}</p>
                      <p className="text-xs text-slate-400">{user.email}</p>
                    </td>
                    <td className="px-4 py-2.5">
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${user.role === 'admin' ? 'bg-red-100 text-red-700' : user.role === 'tutor' ? 'bg-amber-100 text-amber-700' : 'bg-blue-100 text-blue-700'}`}>
                        {user.role}
                      </span>
                    </td>
                    <td className="px-4 py-2.5 font-medium text-indigo-600">{user.total_xp}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Resources approval */}
        <div className="bg-white rounded-xl border border-slate-100 shadow-sm overflow-hidden">
          <div className="p-4 border-b border-slate-100">
            <h2 className="font-semibold text-slate-900 flex items-center gap-2"><FileText size={16} /> Resources</h2>
          </div>
          <div className="divide-y divide-slate-50 max-h-80 overflow-y-auto">
            {resources?.map(r => (
              <div key={r.id} className="flex items-center justify-between px-4 py-3">
                <div>
                  <p className="text-sm font-medium text-slate-900 truncate max-w-[180px]">{r.title}</p>
                  <p className="text-xs text-slate-400">{r.resource_type} · {r.is_indexed ? 'Indexed' : 'Not indexed'}</p>
                </div>
                {r.is_approved ? (
                  <span className="flex items-center gap-1 text-xs text-emerald-600"><CheckCircle size={12} /> Approved</span>
                ) : (
                  <button onClick={() => handleApprove(r.id)}
                    className="text-xs px-2.5 py-1 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
                    Approve
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </Layout>
  );
}


