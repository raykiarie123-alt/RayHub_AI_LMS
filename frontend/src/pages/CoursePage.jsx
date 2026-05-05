import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import Layout from '../components/Layout';
import { courseApi } from '../services/courseApi';
import { BookOpen, ChevronRight, Layers } from 'lucide-react';

export default function CoursesPage() {
  const { data: levels, isLoading: levelsLoading } = useQuery({
    queryKey: ['levels'],
    queryFn: () => courseApi.getLevels().then(r => r.data)
  });
  const { data: courses, isLoading: coursesLoading } = useQuery({
    queryKey: ['courses'],
    queryFn: () => courseApi.getCourses().then(r => r.data)
  });

  const loading = levelsLoading || coursesLoading;

  return (
    <Layout title="Courses">
      {loading ? (
        <div className="flex justify-center py-20">
          <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : (
        <div className="space-y-8">
          {levels?.map(level => {
            const levelCourses = courses?.filter(c => c.level_id === level.id) || [];
            return (
              <div key={level.id}>
                <div className="flex items-center gap-2 mb-4">
                  <Layers size={18} className="text-indigo-600" />
                  <h2 className="text-lg font-semibold text-slate-900">{level.name}</h2>
                  <span className="text-sm text-slate-400">— {level.description}</span>
                </div>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {levelCourses.map(course => (
                    <Link key={course.id} to={`/courses/${course.id}`}
                      className="bg-white rounded-xl border border-slate-100 p-5 hover:border-indigo-300 hover:shadow-md transition-all group">
                      <div className="w-10 h-10 bg-indigo-100 rounded-xl flex items-center justify-center mb-3 group-hover:bg-indigo-200 transition-colors">
                        <BookOpen size={18} className="text-indigo-600" />
                      </div>
                      <h3 className="font-semibold text-slate-900 mb-1">{course.title}</h3>
                      <p className="text-sm text-slate-500 mb-3 line-clamp-2">{course.description}</p>
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-slate-400">{course.units?.length || 0} units</span>
                        <ChevronRight size={16} className="text-slate-400 group-hover:text-indigo-600 transition-colors" />
                      </div>
                    </Link>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </Layout>
  );
}