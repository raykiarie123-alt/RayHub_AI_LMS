import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import Layout from '../components/Layout';
import { quizApi } from '../services/quizApi';
import { resourceApi } from '../services/resourceApi';
import toast from 'react-hot-toast';
import {
  Layers,
  Plus,
  RotateCw,
  CheckCircle,
  XCircle,
  Trash2,
  Sparkles,
  FileText,
  BookOpen,
  X,
} from 'lucide-react';

function FlashcardCard({ flashcard, onReview, onDelete }) {
  const [flipped, setFlipped] = useState(false);

  const masteryLevel = flashcard.interval_days >= 7 ? 'mastered' : flashcard.review_count > 0 ? 'learning' : 'new';
  const masteryColor = {
    mastered: 'border-emerald-200 bg-emerald-50/30',
    learning: 'border-amber-200 bg-amber-50/30',
    new: 'border-slate-100',
  }[masteryLevel] || 'border-slate-100';

  return (
    <div className={`relative bg-white dark:bg-slate-900 rounded-xl border shadow-sm cursor-pointer transition-all duration-200 hover:shadow-md min-h-52 ${masteryColor}`}
      onClick={() => setFlipped(!flipped)}>
      <div className="p-5 h-full flex flex-col">
        {!flipped ? (
          <>
            <p className="text-xs text-slate-400 mb-2 font-medium uppercase tracking-wide">Question</p>
            <p className="text-slate-900 dark:text-white font-medium flex-1 leading-relaxed">{flashcard.front || flashcard.question}</p>
            <p className="text-xs text-indigo-500 mt-4 flex items-center gap-1">
              <RotateCw size={11} /> Click to reveal answer
            </p>
          </>
        ) : (
          <>
            <p className="text-xs text-slate-400 mb-2 font-medium uppercase tracking-wide">Answer</p>
            <p className="text-slate-700 dark:text-slate-300 flex-1 leading-relaxed">{flashcard.back || flashcard.answer}</p>
            <div className="flex gap-2 mt-4">
              <button
                onClick={e => { e.stopPropagation(); onReview(flashcard.id, 'hard'); }}
                className="flex items-center gap-1 px-3 py-1.5 bg-red-50 text-red-600 rounded-lg text-xs hover:bg-red-100"
              >
                <XCircle size={13} /> Hard
              </button>
              <button
                onClick={e => { e.stopPropagation(); onReview(flashcard.id, 'easy'); }}
                className="flex items-center gap-1 px-3 py-1.5 bg-emerald-50 text-emerald-600 rounded-lg text-xs hover:bg-emerald-100"
              >
                <CheckCircle size={13} /> Easy
              </button>
            </div>
          </>
        )}
      </div>

      <button
        onClick={e => { e.stopPropagation(); onDelete(flashcard.id); }}
        className="absolute top-3 right-3 p-1.5 bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700 text-slate-400 rounded-lg hover:bg-red-50 hover:text-red-600 hover:border-red-200 transition-colors"
      >
        <Trash2 size={13} />
      </button>

      {masteryLevel === 'mastered' && (
        <span className="absolute top-3 left-3 text-xs bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded-full">Mastered</span>
      )}
    </div>
  );
}

function GenerateFromResourceModal({ isOpen, onClose, resources }) {
  const [selectedResourceId, setSelectedResourceId] = useState('');
  const [numCards, setNumCards] = useState(10);
  const [generating, setGenerating] = useState(false);
  const queryClient = useQueryClient();

  const handleGenerate = async () => {
    if (!selectedResourceId) {
      toast.error('Please select a resource');
      return;
    }
    setGenerating(true);
    try {
      const res = await quizApi.generateFlashcards({
        resource_id: parseInt(selectedResourceId),
        number_of_cards: numCards,
      });
      const count = Array.isArray(res.data) ? res.data.length : numCards;
      toast.success(`${count} flashcards generated!`);
      await queryClient.invalidateQueries({ queryKey: ['flashcards'] });
      await queryClient.refetchQueries({ queryKey: ['flashcards'] });
      onClose();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to generate flashcards');
    } finally {
      setGenerating(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-slate-900 rounded-2xl w-full max-w-md p-6 shadow-xl">
        <div className="flex items-center justify-between mb-5">
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white flex items-center gap-2">
            <Sparkles size={18} className="text-indigo-600" /> Generate Flashcards
          </h3>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
            <X size={20} />
          </button>
        </div>

        <p className="text-sm text-slate-500 mb-4">
          Select one of your uploaded resources to generate flashcards from its content.
        </p>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
              Resource
            </label>
            {resources?.length === 0 ? (
              <div className="p-4 border border-dashed border-slate-200 rounded-lg text-center">
                <FileText size={24} className="mx-auto mb-2 text-slate-300" />
                <p className="text-sm text-slate-500">No resources uploaded yet.</p>
                <p className="text-xs text-slate-400 mt-1">Go to Resources and upload a PDF first.</p>
              </div>
            ) : (
              <select
                value={selectedResourceId}
                onChange={e => setSelectedResourceId(e.target.value)}
                className="w-full px-3 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:bg-slate-800 dark:border-slate-700 dark:text-white"
              >
                <option value="">— Select a resource —</option>
                {resources?.map(r => (
                  <option key={r.id} value={r.id}>
                    {r.title} ({r.resource_type?.toUpperCase()}) · {r.level}
                  </option>
                ))}
              </select>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
              Number of Cards
            </label>
            <select
              value={numCards}
              onChange={e => setNumCards(parseInt(e.target.value))}
              className="w-full px-3 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:bg-slate-800 dark:border-slate-700 dark:text-white"
            >
              {[5, 10, 15, 20].map(n => (
                <option key={n} value={n}>{n} cards</option>
              ))}
            </select>
          </div>
        </div>

        <div className="flex gap-3 mt-6">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2.5 border border-slate-200 text-slate-700 rounded-lg hover:bg-slate-50 text-sm"
          >
            Cancel
          </button>
          <button
            onClick={handleGenerate}
            disabled={generating || !selectedResourceId || resources?.length === 0}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-60 text-sm font-medium"
          >
            <Sparkles size={15} />
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

  const { data: flashcards, isLoading } = useQuery({
    queryKey: ['flashcards'],
    queryFn: () => quizApi.getFlashcards().then(r => r.data),
  });

  const { data: resources } = useQuery({
    queryKey: ['resources'],
    queryFn: () => resourceApi.getResources().then(r => r.data),
  });

  const deleteMutation = useMutation({
    mutationFn: id => quizApi.deleteFlashcard(id),
    onSuccess: () => {
      toast.success('Flashcard deleted');
      queryClient.invalidateQueries({ queryKey: ['flashcards'] });
    },
    onError: () => toast.error('Failed to delete'),
  });

  const reviewMutation = useMutation({
    mutationFn: ({ id, rating }) => quizApi.reviewFlashcard({
      flashcard_id: id,
      quality: rating === 'easy' ? 5 : 1,
    }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['flashcards'] }),
    onError: () => toast.error('Failed to record review'),
  });

  const mastered = flashcards?.filter(f => (f.interval_days || 1) >= 7).length || 0;
  const learning = flashcards?.filter(f => (f.review_count || 0) > 0 && (f.interval_days || 1) < 7).length || 0;

  return (
    <Layout title="Flashcards">
      <div className="mb-5 flex items-center justify-between">
        <p className="text-sm text-slate-500 dark:text-slate-400">Spaced repetition study cards from your resources</p>
        <button
          onClick={() => setShowGenerateModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700"
        >
          <Plus size={16} /> Generate from Resource
        </button>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-100 dark:border-slate-800 p-4 shadow-sm">
          <div className="flex items-center gap-2 mb-1">
            <Layers size={16} className="text-indigo-500" />
            <p className="text-xs text-slate-500 dark:text-slate-400">Total</p>
          </div>
          <p className="text-2xl font-bold text-slate-900 dark:text-white">{flashcards?.length || 0}</p>
        </div>
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-100 dark:border-slate-800 p-4 shadow-sm">
          <div className="flex items-center gap-2 mb-1">
            <CheckCircle size={16} className="text-emerald-500" />
            <p className="text-xs text-slate-500 dark:text-slate-400">Mastered</p>
          </div>
          <p className="text-2xl font-bold text-emerald-600">{mastered}</p>
        </div>
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-100 dark:border-slate-800 p-4 shadow-sm">
          <div className="flex items-center gap-2 mb-1">
            <BookOpen size={16} className="text-amber-500" />
            <p className="text-xs text-slate-500 dark:text-slate-400">Learning</p>
          </div>
          <p className="text-2xl font-bold text-amber-600">{learning}</p>
        </div>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-20">
          <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : flashcards?.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {flashcards.map(fc => (
            <FlashcardCard
              key={fc.id}
              flashcard={fc}
              onReview={(id, rating) => reviewMutation.mutate({ id, rating })}
              onDelete={id => { if (confirm('Delete this flashcard?')) deleteMutation.mutate(id); }}
            />
          ))}
        </div>
      ) : (
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-100 dark:border-slate-800 p-12 shadow-sm text-center">
          <Layers size={48} className="mx-auto mb-4 text-slate-300" />
          <p className="text-slate-500 dark:text-slate-400 mb-2 font-medium">No flashcards yet</p>
          <p className="text-sm text-slate-400 mb-5">
            Upload a resource first, then generate flashcards from it.
          </p>
          <button
            onClick={() => setShowGenerateModal(true)}
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm font-medium"
          >
            <Sparkles size={16} /> Generate Flashcards
          </button>
        </div>
      )}

      <GenerateFromResourceModal
        isOpen={showGenerateModal}
        onClose={() => setShowGenerateModal(false)}
        resources={resources || []}
      />
    </Layout>
  );
}
