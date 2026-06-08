import { useState, useRef, useEffect } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import Layout from '../components/Layout';
import { progressApi } from '../services/progressApi';
import api from '../services/api';
import { useAuth } from '../hooks/useAuth';
import toast from 'react-hot-toast';
import {
  MessageSquare,
  Heart,
  Plus,
  Send,
  X,
  AtSign,
  Tag,
  GraduationCap,
  Clock,
  Users,
  ChevronDown,
} from 'lucide-react';

const LEVEL_COLORS = {
  foundation: 'bg-emerald-100 text-emerald-700',
  intermediate: 'bg-amber-100 text-amber-700',
  advanced: 'bg-rose-100 text-rose-700',
  'post-qualification': 'bg-purple-100 text-purple-700',
};

const TYPE_COLORS = {
  discussion: 'bg-blue-50 text-blue-700',
  question: 'bg-amber-50 text-amber-700',
  tip: 'bg-emerald-50 text-emerald-700',
  announcement: 'bg-purple-50 text-purple-700',
};

function timeAgo(dateStr) {
  if (!dateStr) return '';
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}

function AuthorBadge({ name, username, cpaLevel, studentLevel, size = 'sm' }) {
  const levelKey = (studentLevel || cpaLevel || 'foundation').toLowerCase().replace(/\s+/g, '-');
  const colorClass = LEVEL_COLORS[levelKey] || 'bg-slate-100 text-slate-600';
  const initials = name ? name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase() : '??';

  return (
    <div className="flex items-center gap-2">
      <div className={`${size === 'sm' ? 'w-7 h-7 text-xs' : 'w-9 h-9 text-sm'} bg-indigo-100 rounded-full flex items-center justify-center text-indigo-700 font-bold flex-shrink-0`}>
        {initials}
      </div>
      <div className="min-w-0">
        <div className="flex items-center gap-1.5">
          <span className="text-sm font-medium text-slate-900 dark:text-white">{name}</span>
          {username && <span className="text-xs text-slate-400">@{username}</span>}
        </div>
        <span className={`inline-block text-xs px-1.5 py-0.5 rounded-md font-medium mt-0.5 ${colorClass}`}>
          {cpaLevel || studentLevel || 'Foundation'}
        </span>
      </div>
    </div>
  );
}

function MentionInput({ value, onChange, placeholder, className, onKeyDown }) {
  const [mentionQuery, setMentionQuery] = useState('');
  const [mentionUsers, setMentionUsers] = useState([]);
  const [showMentions, setShowMentions] = useState(false);
  const inputRef = useRef(null);
  const mentionTimeout = useRef(null);

  const handleChange = (e) => {
    const val = e.target.value;
    onChange(val);

    const cursorPos = e.target.selectionStart;
    const textBefore = val.slice(0, cursorPos);
    const mentionMatch = textBefore.match(/@(\w*)$/);

    if (mentionMatch) {
      const query = mentionMatch[1];
      setMentionQuery(query);
      clearTimeout(mentionTimeout.current);
      mentionTimeout.current = setTimeout(async () => {
        if (query.length >= 1) {
          try {
            const res = await api.get('/community/users/search', { params: { q: query } });
            setMentionUsers(res.data || []);
            setShowMentions(true);
          } catch {
            setMentionUsers([]);
          }
        }
      }, 300);
    } else {
      setShowMentions(false);
    }
  };

  const selectMention = (user) => {
    const cursorPos = inputRef.current.selectionStart;
    const textBefore = value.slice(0, cursorPos);
    const textAfter = value.slice(cursorPos);
    const newText = textBefore.replace(/@\w*$/, `@${user.username} `) + textAfter;
    onChange(newText);
    setShowMentions(false);
    inputRef.current.focus();
  };

  return (
    <div className="relative flex-1">
      <input
        ref={inputRef}
        value={value}
        onChange={handleChange}
        onKeyDown={onKeyDown}
        placeholder={placeholder}
        className={className}
      />
      {showMentions && mentionUsers.length > 0 && (
        <div className="absolute bottom-full left-0 right-0 mb-1 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl shadow-lg z-20 max-h-40 overflow-y-auto">
          {mentionUsers.map(u => (
            <button
              key={u.id}
              type="button"
              onClick={() => selectMention(u)}
              className="w-full flex items-center gap-2 px-3 py-2 hover:bg-slate-50 dark:hover:bg-slate-700 text-left"
            >
              <div className="w-6 h-6 bg-indigo-100 rounded-full flex items-center justify-center text-xs text-indigo-700 font-bold">
                {u.full_name[0]}
              </div>
              <div>
                <p className="text-sm font-medium text-slate-900 dark:text-white">{u.full_name}</p>
                <p className="text-xs text-slate-400">@{u.username} · {u.cpa_level}</p>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

function NewPostModal({ onClose }) {
  const [form, setForm] = useState({ title: '', content: '', post_type: 'discussion', tags: [] });
  const [tagInput, setTagInput] = useState('');
  const [loading, setLoading] = useState(false);
  const qc = useQueryClient();

  const addTag = () => {
    const t = tagInput.trim();
    if (t && !form.tags.includes(t)) {
      setForm(f => ({ ...f, tags: [...f.tags, t] }));
    }
    setTagInput('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.title.trim() || !form.content.trim()) {
      toast.error('Please fill in title and content');
      return;
    }
    setLoading(true);
    try {
      await progressApi.createPost(form);
      toast.success('Post created!');
      qc.invalidateQueries({ queryKey: ['posts'] });
      onClose();
    } catch {
      toast.error('Failed to create post');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-slate-900 rounded-2xl w-full max-w-lg shadow-xl">
        <div className="p-5 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white">New Community Post</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600"><X size={20} /></button>
        </div>

        <form onSubmit={handleSubmit} className="p-5 space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-slate-500 mb-1">Type</label>
              <select
                value={form.post_type}
                onChange={e => setForm(f => ({ ...f, post_type: e.target.value }))}
                className="w-full px-3 py-2 border border-slate-200 dark:border-slate-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:bg-slate-800 dark:text-white"
              >
                <option value="discussion">Discussion</option>
                <option value="question">Question</option>
                <option value="tip">Study Tip</option>
                <option value="announcement">Announcement</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-500 mb-1">Title</label>
            <input
              value={form.title}
              onChange={e => setForm(f => ({ ...f, title: e.target.value }))}
              required
              placeholder="What's this about?"
              className="w-full px-3 py-2.5 border border-slate-200 dark:border-slate-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:bg-slate-800 dark:text-white"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-500 mb-1">
              Content <span className="text-slate-400 font-normal">(use @username to mention)</span>
            </label>
            <textarea
              value={form.content}
              onChange={e => setForm(f => ({ ...f, content: e.target.value }))}
              required
              rows={4}
              placeholder="Share your thoughts... Use @username to mention someone"
              className="w-full px-3 py-2.5 border border-slate-200 dark:border-slate-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:bg-slate-800 dark:text-white resize-none"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-500 mb-1">Tags</label>
            <div className="flex gap-2">
              <input
                value={tagInput}
                onChange={e => setTagInput(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); addTag(); } }}
                placeholder="Add a tag and press Enter"
                className="flex-1 px-3 py-2 border border-slate-200 dark:border-slate-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:bg-slate-800 dark:text-white"
              />
              <button type="button" onClick={addTag} className="px-3 py-2 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 rounded-lg text-sm hover:bg-slate-200">
                Add
              </button>
            </div>
            {form.tags.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-2">
                {form.tags.map(t => (
                  <span key={t} className="flex items-center gap-1 px-2 py-0.5 bg-indigo-50 text-indigo-700 rounded-full text-xs">
                    #{t}
                    <button type="button" onClick={() => setForm(f => ({ ...f, tags: f.tags.filter(x => x !== t) }))}>
                      <X size={10} />
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>

          <div className="flex gap-2 pt-2">
            <button type="button" onClick={onClose} className="flex-1 px-4 py-2.5 border border-slate-200 dark:border-slate-700 rounded-lg text-sm text-slate-600 dark:text-slate-400 hover:bg-slate-50">
              Cancel
            </button>
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

function PostDetail({ postId, onClose }) {
  const [comment, setComment] = useState('');
  const [loading, setLoading] = useState(false);
  const qc = useQueryClient();
  const { user } = useAuth();

  const { data: post } = useQuery({
    queryKey: ['post', postId],
    queryFn: () => progressApi.getPost(postId).then(r => r.data),
  });

  const handleComment = async (e) => {
    e.preventDefault();
    if (!comment.trim()) return;
    setLoading(true);
    try {
      await progressApi.addComment(postId, { content: comment });
      setComment('');
      qc.invalidateQueries({ queryKey: ['post', postId] });
      qc.invalidateQueries({ queryKey: ['posts'] });
    } catch {
      toast.error('Failed to add comment');
    } finally {
      setLoading(false);
    }
  };

  if (!post) return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
    </div>
  );

  const levelKey = (post.author_student_level || 'foundation').toLowerCase();

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-slate-900 rounded-2xl w-full max-w-2xl max-h-[88vh] flex flex-col shadow-2xl">
        <div className="p-5 border-b border-slate-100 dark:border-slate-800">
          <div className="flex items-start justify-between gap-3">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-2">
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${TYPE_COLORS[post.post_type] || 'bg-slate-100 text-slate-600'}`}>
                  {post.post_type}
                </span>
                {post.tags?.map(t => (
                  <span key={t} className="text-xs text-indigo-600 dark:text-indigo-400">#{t}</span>
                ))}
              </div>
              <h2 className="font-semibold text-slate-900 dark:text-white text-lg">{post.title}</h2>
            </div>
            <button onClick={onClose} className="text-slate-400 hover:text-slate-600 ml-2 flex-shrink-0"><X size={20} /></button>
          </div>

          <div className="mt-3 flex items-center gap-3">
            <AuthorBadge
              name={post.author}
              username={post.author_username}
              cpaLevel={post.author_cpa_level}
              studentLevel={post.author_student_level}
            />
            <span className="text-xs text-slate-400 flex items-center gap-1">
              <Clock size={11} /> {timeAgo(post.created_at)}
            </span>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-5">
          <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed mb-6 whitespace-pre-wrap">
            {post.content}
          </p>

          <div className="flex items-center gap-4 mb-5 pb-5 border-b border-slate-100 dark:border-slate-800">
            <span className="flex items-center gap-1.5 text-sm text-slate-500">
              <Heart size={14} className="text-red-400" /> {post.likes_count} likes
            </span>
            <span className="flex items-center gap-1.5 text-sm text-slate-500">
              <MessageSquare size={14} className="text-indigo-400" /> {post.comments?.length || 0} comments
            </span>
          </div>

          <h3 className="font-medium text-slate-900 dark:text-white mb-4 text-sm flex items-center gap-2">
            <Users size={14} /> Responses
          </h3>
          <div className="space-y-4">
            {post.comments?.length === 0 && (
              <p className="text-sm text-slate-400 text-center py-4">No responses yet. Be the first!</p>
            )}
            {post.comments?.map(c => {
              const commentLevelKey = (c.author_student_level || 'foundation').toLowerCase();
              return (
                <div key={c.id} className="flex gap-3">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 ${
                    LEVEL_COLORS[commentLevelKey] || 'bg-slate-100 text-slate-600'
                  }`}>
                    {c.author?.[0]?.toUpperCase()}
                  </div>
                  <div className="flex-1 bg-slate-50 dark:bg-slate-800 rounded-xl p-3">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-semibold text-slate-800 dark:text-slate-200">{c.author}</span>
                      {c.author_username && (
                        <span className="text-xs text-slate-400">@{c.author_username}</span>
                      )}
                      {c.author_cpa_level && (
                        <span className={`text-xs px-1.5 py-0.5 rounded-md font-medium ${LEVEL_COLORS[commentLevelKey] || 'bg-slate-100 text-slate-600'}`}>
                          {c.author_cpa_level}
                        </span>
                      )}
                      <span className="text-xs text-slate-400 ml-auto">{timeAgo(c.created_at)}</span>
                    </div>
                    <p className="text-sm text-slate-600 dark:text-slate-300 whitespace-pre-wrap">{c.content}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <form onSubmit={handleComment} className="p-4 border-t border-slate-100 dark:border-slate-800 flex gap-2">
          <MentionInput
            value={comment}
            onChange={setComment}
            placeholder="Write a response... Use @username to mention"
            className="flex-1 px-3 py-2.5 border border-slate-200 dark:border-slate-700 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:bg-slate-800 dark:text-white"
          />
          <button
            type="submit"
            disabled={loading || !comment.trim()}
            className="px-4 py-2.5 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 disabled:opacity-60 flex-shrink-0"
          >
            <Send size={16} />
          </button>
        </form>
      </div>
    </div>
  );
}

function PostCard({ post, onSelect }) {
  const [liking, setLiking] = useState(false);
  const qc = useQueryClient();
  const levelKey = (post.author_student_level || 'foundation').toLowerCase();

  const handleLike = async (e) => {
    e.stopPropagation();
    setLiking(true);
    try {
      await progressApi.likePost(post.id);
      qc.invalidateQueries({ queryKey: ['posts'] });
    } finally {
      setLiking(false);
    }
  };

  return (
    <div
      onClick={() => onSelect(post.id)}
      className="bg-white dark:bg-slate-900 rounded-xl border border-slate-100 dark:border-slate-800 p-5 shadow-sm hover:shadow-md hover:border-indigo-200 dark:hover:border-indigo-700 transition-all cursor-pointer"
    >
      <div className="flex items-start gap-2 mb-3">
        <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${TYPE_COLORS[post.post_type] || 'bg-slate-100 text-slate-600'}`}>
          {post.post_type}
        </span>
        {post.is_pinned && <span className="text-xs bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded-full">📌 Pinned</span>}
      </div>

      <h3 className="font-semibold text-slate-900 dark:text-white mb-1 line-clamp-2">{post.title}</h3>
      <p className="text-sm text-slate-500 dark:text-slate-400 line-clamp-2 mb-3">{post.content}</p>

      {post.tags?.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-3">
          {post.tags.slice(0, 3).map(t => (
            <span key={t} className="text-xs text-indigo-600 dark:text-indigo-400">#{t}</span>
          ))}
        </div>
      )}

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${LEVEL_COLORS[levelKey] || 'bg-slate-100 text-slate-600'}`}>
            {post.author?.[0]?.toUpperCase()}
          </div>
          <div>
            <span className="text-xs font-medium text-slate-700 dark:text-slate-300">{post.author}</span>
            {post.author_cpa_level && (
              <span className={`ml-1.5 text-xs px-1.5 py-0.5 rounded-md ${LEVEL_COLORS[levelKey] || 'bg-slate-100 text-slate-600'}`}>
                {post.author_cpa_level}
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center gap-3 text-xs text-slate-400">
          <span className="flex items-center gap-1">{timeAgo(post.created_at)}</span>
          <button onClick={handleLike} disabled={liking} className="flex items-center gap-1 hover:text-red-500 transition-colors">
            <Heart size={12} /> {post.likes_count}
          </button>
          <span className="flex items-center gap-1">
            <MessageSquare size={12} /> {post.comments_count}
          </span>
        </div>
      </div>
    </div>
  );
}

export default function CommunityPage() {
  const [showModal, setShowModal] = useState(false);
  const [selectedPost, setSelectedPost] = useState(null);
  const [filter, setFilter] = useState('');
  const [levelFilter, setLevelFilter] = useState('');

  const { data: posts, isLoading } = useQuery({
    queryKey: ['posts', filter, levelFilter],
    queryFn: () => progressApi.getPosts(
      Object.assign({}, filter ? { post_type: filter } : {}, levelFilter ? { cpa_level: levelFilter } : {})
    ).then(r => r.data),
  });

  return (
    <Layout title="Community">
      <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 mb-5">
        <div className="flex gap-2 flex-wrap">
          {[['', 'All'], ['discussion', 'Discussion'], ['question', 'Questions'], ['tip', 'Tips']].map(([type, label]) => (
            <button
              key={type}
              onClick={() => setFilter(type)}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                filter === type
                  ? 'bg-indigo-600 text-white'
                  : 'bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700'
              }`}
            >
              {label}
            </button>
          ))}
        </div>

        <div className="flex gap-2 sm:ml-auto">
          <select
            value={levelFilter}
            onChange={e => setLevelFilter(e.target.value)}
            className="px-3 py-1.5 border border-slate-200 dark:border-slate-700 rounded-lg text-sm bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">All Levels</option>
            <option value="foundation">Foundation</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
            <option value="post-qualification">Post-Qualification</option>
          </select>

          <button
            onClick={() => setShowModal(true)}
            className="flex items-center gap-2 px-4 py-1.5 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700"
          >
            <Plus size={15} /> Post
          </button>
        </div>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-20">
          <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : (
        <div className="grid md:grid-cols-2 gap-4">
          {posts?.map(post => (
            <PostCard key={post.id} post={post} onSelect={setSelectedPost} />
          ))}
        </div>
      )}

      {posts?.length === 0 && !isLoading && (
        <div className="text-center py-20 text-slate-400 dark:text-slate-600">
          <MessageSquare size={48} className="mx-auto mb-3 opacity-30" />
          <p className="font-medium">No posts yet</p>
          <p className="text-sm mt-1">Be the first to start a discussion!</p>
          <button
            onClick={() => setShowModal(true)}
            className="mt-4 px-5 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700"
          >
            Create First Post
          </button>
        </div>
      )}

      {showModal && <NewPostModal onClose={() => setShowModal(false)} />}
      {selectedPost && <PostDetail postId={selectedPost} onClose={() => setSelectedPost(null)} />}
    </Layout>
  );
}
