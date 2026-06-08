import { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import Layout from '../components/Layout';
import { resourceApi } from '../services/resourceApi';
import { useAuth } from '../hooks/useAuth';
import toast from 'react-hot-toast';
import {
  Upload,
  Video,
  Globe,
  FileText,
  Link as LinkIcon,
  Trash2,
  User,
  Layers,
  Search,
  Filter,
  BookOpen,
} from 'lucide-react';

const LEVEL_OPTIONS = ['foundation', 'intermediate', 'advanced'];

const levelColors = {
  foundation: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  intermediate: 'bg-amber-50 text-amber-700 border-amber-200',
  advanced: 'bg-rose-50 text-rose-700 border-rose-200',
};

const typeIcons = {
  pdf: FileText,
  youtube: Video,
  web: Globe,
  text: FileText,
  past_paper: BookOpen,
};

function UploadModal({ onClose, userLevel }) {
  const [tab, setTab] = useState('pdf');
  const [file, setFile] = useState(null);
  const [ytUrl, setYtUrl] = useState('');
  const [webUrl, setWebUrl] = useState('');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [resourceLevel, setResourceLevel] = useState(userLevel || 'foundation');
  const [loading, setLoading] = useState(false);
  const qc = useQueryClient();

  const allowedLevels = {
    foundation: ['foundation'],
    intermediate: ['foundation', 'intermediate'],
    advanced: ['foundation', 'intermediate', 'advanced'],
    'post-qualification': ['foundation', 'intermediate', 'advanced', 'post-qualification'],
  }[userLevel || 'foundation'] || ['foundation'];

  const handleUpload = async () => {
    if (tab === 'pdf' && !file) return toast.error('Please choose a file');
    if (tab === 'youtube' && !ytUrl) return toast.error('Please enter YouTube URL');
    if (tab === 'web' && !webUrl) return toast.error('Please enter a web URL');
    if (!title.trim()) return toast.error('Please enter a title');

    setLoading(true);
    try {
      if (tab === 'pdf') {
        const fd = new FormData();
        fd.append('file', file);
        fd.append('title', title || file.name);
        fd.append('description', description || '');
        fd.append('resource_type', 'pdf');
        fd.append('level', resourceLevel);
        await resourceApi.uploadDocument(fd);
        toast.success('Document uploaded successfully!');
      } else if (tab === 'youtube') {
        await resourceApi.ingestYouTube({ url: ytUrl, title, description, level: resourceLevel });
        toast.success('YouTube resource added!');
      } else if (tab === 'web') {
        await resourceApi.ingestWeb({ url: webUrl, title, description, level: resourceLevel });
        toast.success('Web resource added!');
      }
      qc.invalidateQueries({ queryKey: ['resources'] });
      onClose();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl w-full max-w-md p-6 shadow-xl">
        <h2 className="text-lg font-semibold text-slate-900 mb-4">Add Learning Resource</h2>

        <div className="flex gap-2 mb-4">
          {[['pdf', 'PDF', FileText], ['youtube', 'YouTube', Video], ['web', 'Web URL', Globe]].map(([key, label, Icon]) => (
            <button
              key={key}
              onClick={() => setTab(key)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                tab === key ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              <Icon size={14} /> {label}
            </button>
          ))}
        </div>

        <div className="space-y-3">
          <input
            value={title}
            onChange={e => setTitle(e.target.value)}
            placeholder="Resource title *"
            className="w-full px-3 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <textarea
            value={description}
            onChange={e => setDescription(e.target.value)}
            placeholder="Short description (optional)"
            rows={2}
            className="w-full px-3 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
          />

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Resource Level</label>
            <select
              value={resourceLevel}
              onChange={e => setResourceLevel(e.target.value)}
              className="w-full px-3 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              {allowedLevels.map(l => (
                <option key={l} value={l} className="capitalize">{l.charAt(0).toUpperCase() + l.slice(1)}</option>
              ))}
            </select>
          </div>

          {tab === 'pdf' && (
            <input
              type="file"
              accept=".pdf,.txt,.docx"
              onChange={e => setFile(e.target.files[0])}
              className="w-full text-sm text-slate-600 file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:bg-indigo-50 file:text-indigo-700 file:text-sm file:font-medium hover:file:bg-indigo-100"
            />
          )}
          {tab === 'youtube' && (
            <input
              value={ytUrl}
              onChange={e => setYtUrl(e.target.value)}
              placeholder="https://youtube.com/watch?v=..."
              className="w-full px-3 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          )}
          {tab === 'web' && (
            <input
              value={webUrl}
              onChange={e => setWebUrl(e.target.value)}
              placeholder="https://example.com"
              className="w-full px-3 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          )}
        </div>

        <div className="flex gap-2 mt-5">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2.5 border border-slate-200 rounded-lg text-sm text-slate-600 hover:bg-slate-50"
          >
            Cancel
          </button>
          <button
            onClick={handleUpload}
            disabled={loading}
            className="flex-1 px-4 py-2.5 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-60"
          >
            {loading ? 'Processing...' : 'Add Resource'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default function ResourcesPage() {
  const { user } = useAuth();
  const [showModal, setShowModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterLevel, setFilterLevel] = useState('all');
  const [filterType, setFilterType] = useState('all');
  const qc = useQueryClient();

  const { data: resources, isLoading } = useQuery({
    queryKey: ['resources'],
    queryFn: () => resourceApi.getResources().then(r => r.data),
  });

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this resource?')) return;
    try {
      await resourceApi.deleteDocument(id);
      toast.success('Resource deleted');
      qc.invalidateQueries({ queryKey: ['resources'] });
    } catch {
      toast.error('Delete failed');
    }
  };

  const filtered = resources?.filter(r => {
    const matchSearch = !searchQuery ||
      r.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.description?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchLevel = filterLevel === 'all' || r.level === filterLevel;
    const matchType = filterType === 'all' || r.resource_type === filterType;
    return matchSearch && matchLevel && matchType;
  }) || [];

  return (
    <Layout title="Resources">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5">
        <div>
          <p className="text-sm text-slate-500">
            <span className="font-semibold text-slate-700">{filtered.length}</span> resources available for your level
          </p>
          <p className="text-xs text-slate-400 mt-0.5">
            Shared by peers at your academic level and above
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 self-start sm:self-auto"
        >
          <Upload size={16} /> Add Resource
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-5">
        <div className="relative flex-1 min-w-48">
          <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            placeholder="Search resources..."
            className="w-full pl-9 pr-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        <select
          value={filterLevel}
          onChange={e => setFilterLevel(e.target.value)}
          className="px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
        >
          <option value="all">All Levels</option>
          {LEVEL_OPTIONS.map(l => (
            <option key={l} value={l} className="capitalize">{l.charAt(0).toUpperCase() + l.slice(1)}</option>
          ))}
        </select>
        <select
          value={filterType}
          onChange={e => setFilterType(e.target.value)}
          className="px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
        >
          <option value="all">All Types</option>
          <option value="pdf">PDF</option>
          <option value="youtube">YouTube</option>
          <option value="web">Web</option>
        </select>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-20">
          <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-20">
          <FileText size={48} className="mx-auto mb-3 text-slate-300" />
          <p className="text-slate-500 font-medium">No resources found</p>
          <p className="text-sm text-slate-400 mt-1">
            {searchQuery ? 'Try a different search' : 'Be the first to upload a resource for your level!'}
          </p>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map(resource => {
            const TypeIcon = typeIcons[resource.resource_type] || FileText;
            const isOwn = resource.uploader_id === user?.id;

            return (
              <div
                key={resource.id}
                className="bg-white rounded-xl border border-slate-100 p-5 shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="flex justify-between items-start mb-3">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-indigo-50 rounded-lg flex items-center justify-center">
                      <TypeIcon size={15} className="text-indigo-600" />
                    </div>
                    <span className={`px-2 py-0.5 rounded-md text-xs font-medium border capitalize ${levelColors[resource.level] || 'bg-slate-50 text-slate-600 border-slate-200'}`}>
                      {resource.level}
                    </span>
                  </div>
                  {resource.is_indexed && (
                    <span className="text-xs bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded-full border border-emerald-200">
                      Indexed
                    </span>
                  )}
                </div>

                <h3 className="font-semibold text-slate-900 mb-1.5 line-clamp-1">{resource.title}</h3>

                {resource.description && (
                  <p className="text-sm text-slate-500 mb-3 line-clamp-2">{resource.description}</p>
                )}

                {/* Uploader info */}
                <div className="flex items-center gap-1.5 mb-3 text-xs text-slate-400">
                  <User size={12} />
                  <span>
                    {resource.uploader_name
                      ? (isOwn ? 'You' : resource.uploader_name)
                      : 'Unknown'}
                  </span>
                  {resource.created_at && (
                    <>
                      <span>·</span>
                      <span>{new Date(resource.created_at).toLocaleDateString()}</span>
                    </>
                  )}
                </div>

                <div className="flex items-center justify-between pt-3 border-t border-slate-50">
                  {(isOwn || user?.role === 'admin') ? (
                    <button
                      onClick={() => handleDelete(resource.id)}
                      className="flex items-center gap-1 px-2.5 py-1.5 bg-red-50 text-red-700 rounded-lg text-xs hover:bg-red-100"
                    >
                      <Trash2 size={12} /> Delete
                    </button>
                  ) : (
                    <div />
                  )}

                  {resource.url ? (
                    <a
                      href={resource.url}
                      target="_blank"
                      rel="noreferrer"
                      className="flex items-center gap-1 px-2.5 py-1.5 bg-slate-100 text-slate-700 rounded-lg text-xs hover:bg-slate-200"
                    >
                      <LinkIcon size={12} /> Open
                    </a>
                  ) : resource.file_path ? (
                    <a
                      href={`http://127.0.0.1:8000/${resource.file_path}`}
                      target="_blank"
                      rel="noreferrer"
                      className="flex items-center gap-1 px-2.5 py-1.5 bg-slate-100 text-slate-700 rounded-lg text-xs hover:bg-slate-200"
                    >
                      <FileText size={12} /> View
                    </a>
                  ) : null}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {showModal && (
        <UploadModal
          onClose={() => setShowModal(false)}
          userLevel={user?.student_level || 'foundation'}
        />
      )}
    </Layout>
  );
}
