import { useQuery } from '@tanstack/react-query';
import { useAuth } from '../hooks/useAuth';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import { progressApi } from '../services/progressApi';
import { 
  BookOpen, 
  Brain, 
  Clock, 
  Flame, 
  Sparkles, 
  Upload, 
  Bot, 
  Target,
  TrendingUp,
  Calendar,
  CheckCircle
} from 'lucide-react';

function StatCard({ icon: Icon, label, value, color, onClick }) {
  return (
    <div 
      onClick={onClick}
      className={`bg-white rounded-xl border border-slate-100 p-5 shadow-sm cursor-pointer hover:shadow-md transition-all ${onClick ? 'hover:border-indigo-200' : ''}`}
    >
      <div className={`inline-flex items-center justify-center w-10 h-10 rounded-lg mb-3 ${color}`}>
        <Icon size={20} className="text-white" />
      </div>
      <p className="text-2xl font-bold text-slate-900">{value ?? '—'}</p>
      <p className="text-sm text-slate-500 mt-0.5">{label}</p>
    </div>
  );
}

function QuickActionCard({ icon: Icon, label, description, onClick, color }) {
  return (
    <button
      onClick={onClick}
      className="bg-white rounded-xl border border-slate-100 p-5 shadow-sm hover:shadow-md hover:border-indigo-200 transition-all text-left w-full"
    >
      <div className={`inline-flex items-center justify-center w-10 h-10 rounded-lg mb-3 ${color}`}>
        <Icon size={20} className="text-white" />
      </div>
      <h3 className="font-semibold text-slate-900 text-sm">{label}</h3>
      <p className="text-xs text-slate-500 mt-1">{description}</p>
    </button>
  );
}

function ActivityItem({ activity }) {
  const getIcon = () => {
    switch (activity.type) {
      case 'task_completed': return <CheckCircle size={16} className="text-emerald-500" />;
      case 'quiz_attempt': return <Brain size={16} className="text-indigo-500" />;
      case 'resource_added': return <Upload size={16} className="text-amber-500" />;
      case 'plan_created': return <Calendar size={16} className="text-purple-500" />;
      default: return <TrendingUp size={16} className="text-slate-400" />;
    }
  };

  return (
    <div className="flex items-start gap-3 p-3 bg-slate-50 rounded-lg">
      <div className="mt-0.5">{getIcon()}</div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-slate-900">{activity.title}</p>
        <p className="text-xs text-slate-500">{activity.description}</p>
      </div>
      <span className="text-xs text-slate-400 whitespace-nowrap">{activity.time}</span>
    </div>
  );
}

export default function DashboardPage() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const { data: summary } = useQuery({
    queryKey: ['progress-summary'],
    queryFn: () => progressApi.getSummary().then(r => r.data)
  });

  const { data: recentActivity } = useQuery({
    queryKey: ['recent-activity'],
    queryFn: () => progressApi.getMyProgress().then(r => r.data?.slice(0, 5) || [])
  });

  const { data: plans } = useQuery({
    queryKey: ['study-plans'],
    queryFn: () => progressApi.getMyStudyPlans().then(r => r.data)
  });

  const currentPlan = plans?.[0];

  const quickActions = [
    { 
      icon: Sparkles, 
      label: 'Generate Study Plan', 
      description: 'Create AI-powered study schedule',
      onClick: () => navigate('/study-plan'),
      color: 'bg-indigo-500'
    },
    { 
      icon: Brain, 
      label: 'Take a Quiz', 
      description: 'Test your knowledge',
      onClick: () => navigate('/courses'),
      color: 'bg-emerald-500'
    },
    { 
      icon: Upload, 
      label: 'Upload Resource', 
      description: 'Add PDFs, videos, or notes',
      onClick: () => navigate('/resources'),
      color: 'bg-amber-500'
    },
    { 
      icon: Bot, 
      label: 'Ask AI Tutor', 
      description: 'Get answers from your materials',
      onClick: () => navigate('/ai-tutor'),
      color: 'bg-purple-500'
    }
  ];

  const mockActivity = recentActivity?.length > 0 ? recentActivity : [
    { type: 'task_completed', title: 'Completed Task', description: 'Double-entry bookkeeping', time: '2h ago' },
    { type: 'quiz_attempt', title: 'Quiz Attempt', description: 'IFRS Revenue Recognition', time: '5h ago' },
    { type: 'resource_added', title: 'Resource Added', description: 'Audit Standards PDF', time: '1d ago' },
  ];

  return (
    <Layout title="Dashboard">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900">Welcome back, {user?.full_name?.split(' ')[0] || 'Student'}!</h1>
        <p className="text-slate-500 mt-1">Continue your CPA learning journey</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <StatCard 
          icon={BookOpen} 
          label="Topics Completed" 
          value={summary?.topics_completed || 0} 
          color="bg-indigo-500"
          onClick={() => navigate('/progress')}
        />
        <StatCard 
          icon={Brain} 
          label="Avg Quiz Score" 
          value={summary?.average_quiz_score ? `${summary.average_quiz_score}%` : '—'} 
          color="bg-emerald-500"
          onClick={() => navigate('/progress')}
        />
        <StatCard 
          icon={Clock} 
          label="Study Time" 
          value={summary?.total_study_time_minutes ? `${Math.round(summary.total_study_time_minutes / 60)}h` : '0h'} 
          color="bg-amber-500"
        />
        <StatCard 
          icon={Flame} 
          label="Current Streak" 
          value={`${summary?.current_streak || 0} days`} 
          color="bg-orange-500"
          onClick={() => navigate('/progress')}
        />
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        {/* Quick Actions */}
        <div className="md:col-span-2">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-2 gap-4">
            {quickActions.map((action, i) => (
              <QuickActionCard key={i} {...action} />
            ))}
          </div>
        </div>

        {/* Current Study Plan */}
        <div>
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Current Study Plan</h2>
          {currentPlan ? (
            <div className="bg-white rounded-xl border border-slate-100 p-5 shadow-sm">
              <div className="flex items-center gap-2 mb-3">
                <Target size={18} className="text-indigo-600" />
                <h3 className="font-semibold text-slate-900">{currentPlan.title}</h3>
              </div>
              <div className="mb-3">
                <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
                  <span>Progress</span>
                  <span>{currentPlan.completion_percentage?.toFixed(0) || 0}%</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2">
                  <div className="bg-indigo-600 h-2 rounded-full transition-all" style={{ width: `${currentPlan.completion_percentage || 0}%` }}></div>
                </div>
              </div>
              <button 
                onClick={() => navigate('/study-plan')}
                className="w-full px-4 py-2 bg-indigo-50 text-indigo-700 rounded-lg text-sm font-medium hover:bg-indigo-100 transition-colors"
              >
                View Plan
              </button>
            </div>
          ) : (
            <div className="bg-white rounded-xl border border-slate-100 p-5 shadow-sm text-center">
              <Calendar size={40} className="mx-auto mb-3 text-slate-300" />
              <p className="text-sm text-slate-500 mb-3">No active study plan</p>
              <button 
                onClick={() => navigate('/study-plan')}
                className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors"
              >
                Create Plan
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="mt-6">
        <h2 className="text-lg font-semibold text-slate-900 mb-4">Recent Activity</h2>
        <div className="bg-white rounded-xl border border-slate-100 p-5 shadow-sm">
          <div className="space-y-3">
            {mockActivity.map((activity, i) => (
              <ActivityItem key={i} activity={activity} />
            ))}
          </div>
        </div>
      </div>
    </Layout>
  );
}