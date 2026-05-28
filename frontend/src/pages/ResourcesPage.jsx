import { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import Layout from '../components/Layout';
import { resourceApi } from '../services/resourceApi';
import toast from 'react-hot-toast';
import {
  Upload,
  Video,
  Globe,
  FileText,
  Sparkles,
  Link as LinkIcon,
  Trash2,
  User,
  BookOpen,
  Layers,
} from 'lucide-react';

function UploadModal({ onClose }) {
  const [tab, setTab] = useState('pdf');
  const [file, setFile] = useState(null);
  const [ytUrl, setYtUrl] = useState('');
  const [webUrl, setWebUrl] = useState('');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);

  const [resourceLevel, setResourceLevel] = useState('foundation');

  const qc = useQueryClient();

  const handleUpload = async () => {
    if (tab === 'pdf' && !file) {
      toast.error('Please choose a file');
      return;
    }

    if (tab === 'youtube' && !ytUrl) {
      toast.error('Please enter YouTube URL');
      return;
    }

    if (tab === 'web' && !webUrl) {
      toast.error('Please enter web URL');
      return;
    }

    setLoading(true);

    try {
      if (tab === 'pdf') {
        const fd = new FormData();

        fd.append('file', file);
        fd.append('title', title || file.name);
        fd.append('description', description || 'Uploaded learning resource');
        fd.append('resource_type', 'pdf');

        // NEW
        fd.append('level', resourceLevel);

        await resourceApi.uploadDocument(fd);

        toast.success('Document uploaded successfully!');
      }

      if (tab === 'youtube') {
        await resourceApi.ingestYouTube({
          url: ytUrl,
          title,
          description,
          level: resourceLevel,
        });

        toast.success('YouTube resource added!');
      }

      if (tab === 'web') {
        await resourceApi.ingestWeb({
          url: webUrl,
          title,
          description,
          level: resourceLevel,
        });

        toast.success('Web resource added!');
      }

      qc.invalidateQueries({ queryKey: ['resources'] });

      onClose();
    } catch (err) {
      toast.error(
        err.response?.data?.detail || 'Upload failed'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl w-full max-w-md p-6 shadow-xl">
        <h2 className="text-lg font-semibold text-slate-900 mb-4">
          Add Learning Resource
        </h2>

        <div className="flex gap-2 mb-4">
          {[
            ['pdf', 'PDF', FileText],
            ['youtube', 'YouTube', Video],
            ['web', 'Web URL', Globe],
          ].map(([key, label, Icon]) => (
            <button
              key={key}
              onClick={() => setTab(key)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                tab === key
                  ? 'bg-indigo-600 text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              <Icon size={14} />
              {label}
            </button>
          ))}
        </div>

        <div className="space-y-3">
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Resource title"
            className="w-full px-3 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />

          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Short description"
            rows={3}
            className="w-full px-3 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />

          {/* LEVEL SELECTOR */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Resource Level
            </label>

            <select
              value={resourceLevel}
              onChange={(e) => setResourceLevel(e.target.value)}
              className="w-full px-3 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="foundation">Foundation</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </div>

          {tab === 'pdf' && (
            <input
              type="file"
              accept=".pdf,.txt,.docx"
              onChange={(e) => setFile(e.target.files[0])}
              className="w-full text-sm text-slate-600 file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:bg-indigo-50 file:text-indigo-700 file:text-sm file:font-medium hover:file:bg-indigo-100"
            />
          )}

          {tab === 'youtube' && (
            <input
              value={ytUrl}
              onChange={(e) => setYtUrl(e.target.value)}
              placeholder="YouTube URL"
              className="w-full px-3 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          )}

          {tab === 'web' && (
            <input
              value={webUrl}
              onChange={(e) => setWebUrl(e.target.value)}
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
  const [showModal, setShowModal] = useState(false);

  const qc = useQueryClient();

  const { data: resources, isLoading } = useQuery({
    queryKey: ['resources'],
    queryFn: () => resourceApi.getResources().then((r) => r.data),
  });

  const handleDelete = async (id) => {
    const confirmDelete = window.confirm(
      'Are you sure you want to delete this resource?'
    );

    if (!confirmDelete) return;

    try {
      await resourceApi.deleteDocument(id);

      toast.success('Resource deleted');

      qc.invalidateQueries({ queryKey: ['resources'] });
    } catch {
      toast.error('Delete failed');
    }
  };

  const levelColor = {
    foundation: 'bg-emerald-50 text-emerald-700',
    intermediate: 'bg-amber-50 text-amber-700',
    advanced: 'bg-rose-50 text-rose-700',
  };

  return (
    <Layout title="Resources">
      <div className="flex justify-between items-center mb-6">
        <div>
          <p className="text-slate-500 text-sm">
            {resources?.length || 0} resources available
          </p>

          <p className="text-xs text-slate-400 mt-1">
            Access resources based on your academic level
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700"
        >
          <Upload size={16} />
          Add Resource
        </button>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-20">
          <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {resources?.map((resource) => (
            <div
              key={resource.id}
              className="bg-white rounded-xl border border-slate-100 p-5 shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="flex justify-between items-center mb-3">
                <span
                  className={`px-2 py-1 rounded-lg text-xs font-medium ${
                    levelColor[resource.level]
                  }`}
                >
                  <div className="flex items-center gap-1">
                    <Layers size={12} />
                    {resource.level}
                  </div>
                </span>

                {resource.is_indexed && (
                  <span className="text-xs bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded-full">
                    Indexed
                  </span>
                )}
              </div>

              <h3 className="font-semibold text-slate-900 mb-2">
                {resource.title}
              </h3>

              <p className="text-sm text-slate-500 mb-4 line-clamp-3">
                {resource.description}
              </p>

              <div className="flex items-center justify-between">
                <button
                  onClick={() => handleDelete(resource.id)}
                  className="flex items-center gap-1 px-3 py-1.5 bg-red-50 text-red-700 rounded-lg text-xs hover:bg-red-100"
                >
                  <Trash2 size={12} />
                  Delete
                </button>

                {resource.url && (
                  <a
                    href={resource.url}
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center gap-1 px-3 py-1.5 bg-slate-100 text-slate-700 rounded-lg text-xs hover:bg-slate-200"
                  >
                    <LinkIcon size={12} />
                    Open
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {!isLoading && resources?.length === 0 && (
        <div className="text-center py-20">
          <FileText
            size={48}
            className="mx-auto mb-3 text-slate-300"
          />

          <p className="text-slate-500 font-medium">
            No resources available
          </p>

          <p className="text-sm text-slate-400 mt-1">
            Upload resources for your level
          </p>
        </div>
      )}

      {showModal && (
        <UploadModal onClose={() => setShowModal(false)} />
      )}
    </Layout>
  );
}