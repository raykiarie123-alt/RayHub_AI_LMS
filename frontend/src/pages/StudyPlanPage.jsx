import { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import Layout from '../components/Layout';
import { progressApi } from '../services/progressApi';
import toast from 'react-hot-toast';
import { Calendar, Sparkles, CheckCircle, Circle, Trash2, Clock, Target } from 'lucide-react';

function GeneratePlanModal({ onClose }) {
  const [form, setForm] = useState({ available_hours_per_day: 3, learning_style: 'balanced' });
  const [loading, setLoading] = useState(false);
  const qc = useQueryClient();

  const handleGenerate = async () => {
    setLoading(true);
    try {
      await progressApi.generateStudyPlan(form);
      toast.success('Study plan generated!');
      qc.invalidateQueries(['study-plans']);
      onClose();
    } catch {
      toast.error('Failed to generate plan');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl w-full max-w-md p-6">
        <h2 className="text-lg font-semibold text-slate-900 mb-4">Generate AI Study Plan</h2>
        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Plan Title (optional)</label>
            <input value={form.title || ''} onChange={e => setForm(f => ({ ...f, title: e.target.value }))} placeholder="My CPA Study Plan"
              className="w-full px-3 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Exam Date (optional)</label>
            <input type="date" value={form.exam_date || ''} onChange={e => setForm(f => ({ ...f, exam_date: e.target.value }))}
              className="w-full px-3 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Study Hours per Day</label>
            <input type="number" min="0.5" max="12" step="0.5" value={form.available_hours_per_day}
              onChange={e => setForm(f => ({ ...f, available_hours_per_day: parseFloat(e.target.value) }))}
              className="w-full px-3 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Learning Style</label>
            <select value={form.learning_style} onChange={e => setForm(f => ({ ...f, learning_style: e.target.value }))}
              className="w-full px-3 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
              <option value="balanced">Balanced</option>
              <option value="visual">Visual</option>
              <option value="reading">Reading-focused</option>
              <option value="practice">Practice-heavy</option>
            </select>
          </div>
        </div>
        <div className="flex gap-2 mt-5">
          <button onClick={onClose} className="flex-1 px-4 py-2.5 border border-slate-200 rounded-lg text-sm text-slate-600">Cancel</button>
          <button onClick={handleGenerate} disabled={loading}
            className="flex-1 px-4 py-2.5 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-60 flex items-center justify-center gap-2">
            <Sparkles size={14} /> {loading ? 'Generating...' : 'Generate Plan'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default function StudyPlanPage() {
  const [showModal, setShowModal] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const qc = useQueryClient();

  const { data: plans, isLoading } = useQuery({
    queryKey: ['study-plans'],
    queryFn: () => progressApi.getMyStudyPlans().then(r => r.data)
  });

  const { data: planDetail } = useQuery({
    queryKey: ['study-plan', selectedPlan],
    queryFn: () => progressApi.getStudyPlan(selectedPlan).then(r => r.data),
    enabled: !!selectedPlan
  });

  const handleCompleteTask = async (planId, taskId) => {
    try {
      await progressApi.completeTask(planId, { task_id: taskId });
      toast.success('+10 XP earned!');
      qc.invalidateQueries(['study-plan', planId]);
      qc.invalidateQueries(['study-plans']);
    } catch {
      toast.error('Failed to complete task');
    }
  };

  const handleDeletePlan = async (planId) => {
    try {
      await progressApi.deleteStudyPlan(planId);
      toast.success('Plan deleted');
      if (selectedPlan === planId) setSelectedPlan(null);
      qc.invalidateQueries(['study-plans']);
    } catch {
      toast.error('Failed to delete plan');
    }
  };

  const taskTypeColor = {
    topic: 'bg-indigo-100 text-indigo-700',
    quiz: 'bg-emerald-100 text-emerald-700',
    flashcard: 'bg-purple-100 text-purple-700',
    revision: 'bg-amber-100 text-amber-700',
    past_paper: 'bg-red-100 text-red-700'
  };

  return (
    <Layout title="Study Plan">
      <div className="flex justify-between items-center mb-6">
        <p className="text-slate-500 text-sm">{plans?.length || 0} plans</p>
        <button onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700">
          <Sparkles size={16} /> Generate Plan
        </button>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-20">
          <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : (
        <div className="grid md:grid-cols-3 gap-6">
          {/* Plans list */}
          <div className="space-y-3">
            {plans?.map(plan => (
              <div key={plan.id}
                onClick={() => setSelectedPlan(plan.id)}
                className={`bg-white rounded-xl border p-4 cursor-pointer transition-all ${selectedPlan === plan.id ? 'border-indigo-400 shadow-md' : 'border-slate-100 hover:border-indigo-200 hover:shadow-sm'}`}>
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-slate-900 text-sm truncate">{plan.title}</p>
                    {plan.exam_date && (
                      <p className="text-xs text-slate-400 mt-0.5 flex items-center gap-1">
                        <Target size={11} /> Exam: {new Date(plan.exam_date).toLocaleDateString()}
                      </p>
                    )}
                  </div>
                  <button onClick={(e) => { e.stopPropagation(); handleDeletePlan(plan.id); }}
                    className="ml-2 p-1 text-slate-300 hover:text-red-500 transition-colors">
                    <Trash2 size={14} />
                  </button>
                </div>
                <div className="mt-3">
                  <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
                    <span>Progress</span>
                    <span>{plan.completion_percentage?.toFixed(0) || 0}%</span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-1.5">
                    <div className="bg-indigo-600 h-1.5 rounded-full transition-all" style={{ width: `${plan.completion_percentage || 0}%` }}></div>
                  </div>
                </div>
              </div>
            ))}

            {plans?.length === 0 && (
              <div className="text-center py-10 text-slate-400">
                <Calendar size={40} className="mx-auto mb-2 opacity-30" />
                <p className="text-sm">No study plans yet</p>
              </div>
            )}
          </div>

          {/* Plan detail */}
          <div className="md:col-span-2">
            {planDetail ? (
              <div className="bg-white rounded-xl border border-slate-100 shadow-sm">
                <div className="p-5 border-b border-slate-100">
                  <h2 className="font-semibold text-slate-900">{planDetail.title}</h2>
                  {planDetail.description && <p className="text-sm text-slate-500 mt-1">{planDetail.description}</p>}
                  <div className="flex gap-4 mt-3 text-xs text-slate-400">
                    <span className="flex items-center gap-1"><Clock size={11} /> {planDetail.available_hours_per_day}h/day</span>
                    {planDetail.exam_date && <span className="flex items-center gap-1"><Target size={11} /> {new Date(planDetail.exam_date).toLocaleDateString()}</span>}
                  </div>
                </div>
                <div className="p-5 max-h-[60vh] overflow-y-auto space-y-2">
                  {planDetail.tasks?.map(task => (
                    <div key={task.id}
                      className={`flex items-start gap-3 p-3 rounded-lg border transition-all ${task.is_completed ? 'bg-slate-50 border-slate-100 opacity-60' : 'bg-white border-slate-100 hover:border-indigo-200'}`}>
                      <button onClick={() => !task.is_completed && handleCompleteTask(planDetail.id, task.id)}
                        className={`mt-0.5 flex-shrink-0 ${task.is_completed ? 'text-emerald-500' : 'text-slate-300 hover:text-emerald-500'}`}>
                        {task.is_completed ? <CheckCircle size={18} /> : <Circle size={18} />}
                      </button>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <p className={`text-sm font-medium ${task.is_completed ? 'line-through text-slate-400' : 'text-slate-900'}`}>{task.title}</p>
                          <span className={`text-xs px-1.5 py-0.5 rounded-full font-medium ${taskTypeColor[task.task_type] || 'bg-slate-100 text-slate-600'}`}>
                            {task.task_type}
                          </span>
                        </div>
                        {task.description && <p className="text-xs text-slate-500 mt-0.5">{task.description}</p>}
                        <p className="text-xs text-slate-400 mt-1 flex items-center gap-1">
                          <Clock size={10} /> {task.estimated_hours}h
                          {task.scheduled_date && ` · Week ${task.week_number}, Day ${task.day_number}`}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-xl border border-slate-100 p-10 text-center text-slate-400">
                <Calendar size={40} className="mx-auto mb-2 opacity-30" />
                <p className="text-sm">Select a plan to view tasks</p>
              </div>
            )}
          </div>
        </div>
      )}

      {showModal && <GeneratePlanModal onClose={() => setShowModal(false)} />}
    </Layout>
  );
}