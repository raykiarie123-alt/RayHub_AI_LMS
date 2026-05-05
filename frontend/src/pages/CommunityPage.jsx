import { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import Layout from '../components/Layout';
import { progressApi } from '../services/progressApi';
import { useAuth } from '../hooks/useAuth';
import toast from 'react-hot-toast';
import { MessageSquare, Heart, Plus, ChevronRight, Send, X } from 'lucide-react';

function NewPostModal({ onClose }) {
  const [form, setForm] = useState({ title: '', content: '', post_type: 'discussion' });
  const [loading, setLoading] = useState(false);
  const qc = useQueryClient();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await progressApi.createPost(form);
      toast.success('Post created!');
      qc.invalidateQueries(['posts']);
      onClose();
    } catch {
      toast.error('Failed to create post');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl w-full max-w-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-slate-900">New Post</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600"><X size={20} /></button>
        </div>
        <form onSubmit={handleSubmit} className="space-y-3">
          <select value={form.post_type} onChange={e => setForm(f => ({ ...f, post_type: e.target.value }))}
            className="w-full px-3 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
            <option value="discussion">Discussion</option>
            <option value="question">Question</option>
            <option value="tip">Study Tip</option>
            <option value="announcement">Announcement</option>
          </select>
          <input value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))} required
            placeholder="Post title..." className="w-full px-3 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          <textarea value={form.content} onChange={e => setForm(f => ({ ...f, content: e.target.value }))} required
            rows={5} placeholder="What's on your mind?"
            className="w-full px-3 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none" />
          <div className="flex gap-2">
            <button type="button" onClick={onClose} className="flex-1 px-4 py-2.5 border border-slate-200 rounded-lg text-sm text-slate-600">Cancel</button>
            <button type="submit" disabled={loading}
              className="flex-1 px-4 py-2.5 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-60">
              {loading ? 'Posting...' : 'Post'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function PostCard({ post, onSelect }) {
  const [liking, setLiking] = useState(false);
  const qc = useQueryClient();

  const handleLike = async (e) => {
    e.stopPropagation();
    setLiking(true);
    try {
      await progressApi.likePost(post.id);
      qc.invalidateQueries(['posts']);
    } finally {
      setLiking(false);
    }
  };

  const typeColor = {
    discussion: 'bg-blue-50 text-blue-700',
    question: 'bg-amber-50 text-amber-700',
    tip: 'bg-emerald-50 text-emerald-700',
    announcement: 'bg-purple-50 text-purple-700'
  };

  return (
    <div onClick={() => onSelect(post.id)} className="bg-white rounded-xl border border-slate-100 p-5 shadow-sm hover:shadow-md hover:border-indigo-200 transition-all cursor-pointer">
      <div className="flex items-start justify-between mb-2">
        <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${typeColor[post.post_type] || 'bg-slate-100 text-slate-600'}`}>
          {post.post_type}
        </span>
        {post.is_pinned && <span className="text-xs bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded-full">📌 Pinned</span>}
      </div>
      <h3 className="font-semibold text-slate-900 mb-1">{post.title}</h3>
      <p className="text-sm text-slate-500 line-clamp-2 mb-3">{post.content}</p>
      <div className="flex items-center justify-between text-xs text-slate-400">
        <span>by {post.author}</span>
        <div className="flex items-center gap-3">
          <button onClick={handleLike} disabled={liking} className="flex items-center gap-1 hover:text-red-500 transition-colors">
            <Heart size={13} /> {post.likes_count}
          </button>
          <span className="flex items-center gap-1">
            <MessageSquare size={13} /> {post.comments_count}
          </span>
        </div>
      </div>
    </div>
  );
}

function PostDetail({ postId, onClose }) {
  const [comment, setComment] = useState('');
  const [loading, setLoading] = useState(false);
  const qc = useQueryClient();

  const { data: post } = useQuery({
    queryKey: ['post', postId],
    queryFn: () => progressApi.getPost(postId).then(r => r.data)
  });

  const handleComment = async (e) => {
    e.preventDefault();
    if (!comment.trim()) return;
    setLoading(true);
    try {
      await progressApi.addComment(postId, { content: comment });
      setComment('');
      qc.invalidateQueries(['post', postId]);
    } catch {
      toast.error('Failed to add comment');
    } finally {
      setLoading(false);
    }
  };

  if (!post) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl w-full max-w-2xl max-h-[85vh] flex flex-col">
        <div className="p-5 border-b border-slate-100 flex items-start justify-between">
          <div>
            <h2 className="font-semibold text-slate-900">{post.title}</h2>
            <p className="text-xs text-slate-400 mt-0.5">by {post.author}</p>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 ml-4"><X size={20} /></button>
        </div>
        <div className="flex-1 overflow-y-auto p-5">
          <p className="text-sm text-slate-700 mb-6 leading-relaxed">{post.content}</p>
          <h3 className="font-medium text-slate-900 mb-3 text-sm">Comments ({post.comments?.length || 0})</h3>
          <div className="space-y-3">
            {post.comments?.map(c => (
              <div key={c.id} className="flex gap-3">
                <div className="w-7 h-7 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-700 font-semibold text-xs flex-shrink-0">
                  {c.author?.[0]?.toUpperCase()}
                </div>
                <div className="flex-1 bg-slate-50 rounded-xl p-3">
                  <p className="text-xs font-medium text-slate-700 mb-1">{c.author}</p>
                  <p className="text-sm text-slate-600">{c.content}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
        <form onSubmit={handleComment} className="p-4 border-t border-slate-100 flex gap-2">
          <input value={comment} onChange={e => setComment(e.target.value)} placeholder="Add a comment..."
            className="flex-1 px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          <button type="submit" disabled={loading || !comment.trim()}
            className="px-3 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-60">
            <Send size={16} />
          </button>
        </form>
      </div>
    </div>
  );
}

export default function CommunityPage() {
  const [showModal, setShowModal] = useState(false);
  const [selectedPost, setSelectedPost] = useState(null);
  const [filter, setFilter] = useState('');

  const { data: posts, isLoading } = useQuery({
    queryKey: ['posts', filter],
    queryFn: () => progressApi.getPosts(filter ? { post_type: filter } : {}).then(r => r.data)
  });

  return (
    <Layout title="Community">
      <div className="flex items-center justify-between mb-6">
        <div className="flex gap-2">
          {['', 'discussion', 'question', 'tip'].map(type => (
            <button key={type} onClick={() => setFilter(type)}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${filter === type ? 'bg-indigo-600 text-white' : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'}`}>
              {type || 'All'}
            </button>
          ))}
        </div>
        <button onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700">
          <Plus size={16} /> New Post
        </button>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-20">
          <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 gap-4">
          {posts?.map(post => <PostCard key={post.id} post={post} onSelect={setSelectedPost} />)}
        </div>
      )}

      {posts?.length === 0 && !isLoading && (
        <div className="text-center py-20 text-slate-400">
          <MessageSquare size={48} className="mx-auto mb-3 opacity-30" />
          <p className="font-medium">No posts yet</p>
          <p className="text-sm mt-1">Be the first to start a discussion!</p>
        </div>
      )}

      {showModal && <NewPostModal onClose={() => setShowModal(false)} />}
      {selectedPost && <PostDetail postId={selectedPost} onClose={() => setSelectedPost(null)} />}
    </Layout>
  );
}


