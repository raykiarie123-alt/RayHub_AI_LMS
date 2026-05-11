import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import Layout from '../components/Layout';
import { quizApi } from '../services/quizApi';
import { courseApi } from '../services/courseApi';
import toast from 'react-hot-toast';
import { 
  Layers, 
  Plus, 
  RotateCw, 
  CheckCircle, 
  XCircle, 
  Trash2, 
  ChevronRight,
  BookOpen,
  Sparkles
} from 'lucide-react';

function FlashcardCard({ flashcard, onReview, onDelete }) {
  const [flipped, setFlipped] = useState(false);

  return (
    <div className="relative">
      <div
        className={`bg-white rounded-xl border border-slate-100 shadow-sm cursor-pointer transition-all duration-300 min-h-48 ${
          flipped ? 'bg-indigo-50 border-indigo-200' : ''
        }`}
        onClick={() => setFlipped(!flipped)}
      >
        <div className="p-6">
          {!flipped ? (
            <div>
              <p className="text-xs text-slate-400 mb-2">Question</p>
              <p className="text-slate-900 font-medium">{flashcard.question}</p>
              <p className="text-xs text-slate-400 mt-4 flex items-center gap-1">
                Click to flip <RotateCw size={12} />
              </p>
            </div>
          ) : (
            <div>
              <p className="text-xs text-slate-400 mb-2">Answer</p>
              <p className="text-slate-900">{flashcard.answer}</p>
              <p className="text-xs text-slate-400 mt-4 flex items-center gap-1">
                Click to flip back <RotateCw size={12} />
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Action buttons */}
      <div className="absolute bottom-4 right-4 flex gap-2">
        <button
          onClick={(e) => { e.stopPropagation(); onDelete(flashcard.id); }}
          className="p-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100"
          title="Delete"
        >
          <Trash2 size={16} />
        </button>
      </div>

      {/* Review buttons */}
      <div className="absolute bottom-4 left-4 flex gap-2">
        <button
          onClick={(e) => { e.stopPropagation(); onReview(flashcard.id, 'hard'); }}
          className="p-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100"
          title="Hard"
        >
          <XCircle size={16} />
        </button>
        <button
          onClick={(e) => { e.stopPropagation(); onReview(flashcard.id, 'easy'); }}
          className="p-2 bg-emerald-50 text-emerald-600 rounded-lg hover:bg-emerald-100"
          title="Easy"
        >
          <CheckCircle size={16} />
        </button>
      </div>
    </div>
  );
}

function GenerateFlashcardsModal({ isOpen, onClose, courses }) {
  const [selectedCourse, setSelectedCourse] = useState('');
  const [selectedTopic, setSelectedTopic] = useState('');
  const [generating, setGenerating] = useState(false);

  const queryClient = useQueryClient();

  const handleGenerate = async () => {
    if (!selectedTopic) {
      toast.error('Please select a topic');
      return;
    }
    setGenerating(true);
    try {
      await quizApi.generateFlashcards({ topic_id: selectedTopic });
      toast.success('Flashcards generated!');
      queryClient.invalidateQueries(['flashcards']);
      onClose();
    } catch {
      toast.error('Failed to generate flashcards');
    } finally {
      setGenerating(false);
    }
  };

  if (!isOpen) return null;

  const selectedCourseData = courses?.find(c => c.id === selectedCourse);

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl p-6 w-full max-w-md">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Generate Flashcards</h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Course</label>
            <select
              value={selectedCourse}
              onChange={(e) => setSelectedCourse(e.target.value)}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">Select a course</option>
              {courses?.map(course => (
                <option key={course.id} value={course.id}>{course.title}</option>
              ))}
            </select>
          </div>

          {selectedCourseData && (
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Topic</label>
              <select
                value={selectedTopic}
                onChange={(e) => setSelectedTopic(e.target.value)}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">Select a topic</option>
                {selectedCourseData.units?.flatMap(unit => unit.topics || []).map(topic => (
                  <option key={topic.id} value={topic.id}>{topic.title}</option>
                ))}
              </select>
            </div>
          )}
        </div>

        <div className="flex gap-3 mt-6">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2 border border-slate-200 text-slate-700 rounded-lg hover:bg-slate-50"
          >
            Cancel
          </button>
          <button
            onClick={handleGenerate}
            disabled={generating || !selectedTopic}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-60"
          >
            <Sparkles size={16} />
            {generating ? 'Generating...' : 'Generate'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default function FlashcardsPage() {
  const [showGenerateModal, setShowGenerateModal] = useState(false);

  const queryClient = useQueryClient();

  const { data: flashcards, isLoading: flashcardsLoading } = useQuery({
    queryKey: ['flashcards'],
    queryFn: () => quizApi.getFlashcards().then(r => r.data)
  });

  const { data: courses } = useQuery({
    queryKey: ['courses'],
    queryFn: () => courseApi.getCourses().then(r => r.data)
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => quizApi.deleteFlashcard(id),
    onSuccess: () => {
      toast.success('Flashcard deleted');
      queryClient.invalidateQueries(['flashcards']);
    },
    onError: () => {
      toast.error('Failed to delete flashcard');
    }
  });

  const reviewMutation = useMutation({
    mutationFn: ({ id, rating }) => quizApi.reviewFlashcard({ flashcard_id: id, rating }),
    onSuccess: () => {
      toast.success('Review recorded');
      queryClient.invalidateQueries(['flashcards']);
    },
    onError: () => {
      toast.error('Failed to record review');
    }
  });

  const handleReview = (id, rating) => {
    reviewMutation.mutate({ id, rating });
  };

  const handleDelete = (id) => {
    if (confirm('Are you sure you want to delete this flashcard?')) {
      deleteMutation.mutate(id);
    }
  };

  return (
    <Layout>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Flashcards</h1>
          <p className="text-slate-500 mt-1">Study with spaced repetition</p>
        </div>
        <button
          onClick={() => setShowGenerateModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
        >
          <Plus size={18} />
          Generate
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-white rounded-xl border border-slate-100 p-4 shadow-sm">
          <div className="flex items-center gap-2 mb-2">
            <Layers size={18} className="text-indigo-500" />
            <p className="text-xs text-slate-500">Total Cards</p>
          </div>
          <p className="text-2xl font-bold text-slate-900">{flashcards?.length || 0}</p>
        </div>
        <div className="bg-white rounded-xl border border-slate-100 p-4 shadow-sm">
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle size={18} className="text-emerald-500" />
            <p className="text-xs text-slate-500">Mastered</p>
          </div>
          <p className="text-2xl font-bold text-slate-900">
            {flashcards?.filter(f => f.mastery_level === 'mastered').length || 0}
          </p>
        </div>
        <div className="bg-white rounded-xl border border-slate-100 p-4 shadow-sm">
          <div className="flex items-center gap-2 mb-2">
            <BookOpen size={18} className="text-amber-500" />
            <p className="text-xs text-slate-500">Learning</p>
          </div>
          <p className="text-2xl font-bold text-slate-900">
            {flashcards?.filter(f => f.mastery_level === 'learning').length || 0}
          </p>
        </div>
      </div>

      {/* Flashcards Grid */}
      {flashcardsLoading ? (
        <div className="flex justify-center py-20">
          <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : flashcards?.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {flashcards.map((flashcard) => (
            <FlashcardCard
              key={flashcard.id}
              flashcard={flashcard}
              onReview={handleReview}
              onDelete={handleDelete}
            />
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-slate-100 p-12 shadow-sm text-center">
          <Layers size={48} className="mx-auto mb-4 text-slate-300" />
          <p className="text-slate-500 mb-4">No flashcards yet</p>
          <button
            onClick={() => setShowGenerateModal(true)}
            className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            <Sparkles size={18} />
            Generate Your First Flashcards
          </button>
        </div>
      )}

      <GenerateFlashcardsModal
        isOpen={showGenerateModal}
        onClose={() => setShowGenerateModal(false)}
        courses={courses}
      />
    </Layout>
  );
}
