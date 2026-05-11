import { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import Layout from '../components/Layout';
import { resourceApi } from '../services/resourceApi';
import toast from 'react-hot-toast';
import { Upload, Video, Globe, FileText, Sparkles, Link as LinkIcon } from 'lucide-react';

function UploadModal({ onClose }) {
  const [tab, setTab] = useState('pdf');
  const [file, setFile] = useState(null);
  const [ytUrl, setYtUrl] = useState('');
  const [webUrl, setWebUrl] = useState('');
  const [title, setTitle] = useState('');
  const [loading, setLoading] = useState(false);
  const qc = useQueryClient();

  const handleUpload = async () => {
    setLoading(true);
    try {
      if (tab === 'pdf' && file) {
        const fd = new FormData();
        fd.append('file', file);
        if (title) fd.append('title', title);
        await resourceApi.uploadDocument(fd);
        toast.success('Document uploaded and indexed!');
      } else if (tab === 'youtube' && ytUrl) {
        await resourceApi.ingestYouTube({ url: ytUrl, title });
        toast.success('YouTube video ingested!');
      } else if (tab === 'web' && webUrl) {
        await resourceApi.ingestWeb({ url: webUrl, title });
        toast.success('Web page ingested!');
      }
      qc.invalidateQueries(['resources']);
      onClose();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl w-full max-w-md p-6">
        <h2 className="text-lg font-semibold text-slate-900 mb-4">Add Resource</h2>

        <div className="flex gap-2 mb-4">
          {[['pdf', 'PDF', FileText], ['youtube', 'YouTube', Video], ['web', 'Web URL', Globe]].map(([key, label, Icon]) => (
            <button key={key} onClick={() => setTab(key)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${tab === key ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`}>
              <Icon size={14} /> {label}
            </button>
          ))}
        </div>

        <div className="space-y-3">
          <input value={title} onChange={e => setTitle(e.target.value)} placeholder="Title (optional)"
            className="w-full px-3 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />

          {tab === 'pdf' && (
            <input type="file" accept=".pdf,.txt,.docx" onChange={e => setFile(e.target.files[0])}
              className="w-full text-sm text-slate-600 file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:bg-indigo-50 file:text-indigo-700 file:text-sm file:font-medium hover:file:bg-indigo-100" />
          )}
          {tab === 'youtube' && (
            <input value={ytUrl} onChange={e => setYtUrl(e.target.value)} placeholder="YouTube URL"
              className="w-full px-3 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          )}
          {tab === 'web' && (
            <input value={webUrl} onChange={e => setWebUrl(e.target.value)} placeholder="https://..."
              className="w-full px-3 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          )}
        </div>

        <div className="flex gap-2 mt-5">
          <button onClick={onClose} className="flex-1 px-4 py-2.5 border border-slate-200 rounded-lg text-sm text-slate-600 hover:bg-slate-50">Cancel</button>
          <button onClick={handleUpload} disabled={loading}
            className="flex-1 px-4 py-2.5 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-60">
            {loading ? 'Processing...' : 'Add Resource'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default function ResourcesPage() {
  const [showModal, setShowModal] = useState(false);
  const [summarizing, setSummarizing] = useState(null);
  const qc = useQueryClient();

  const { data: resources, isLoading } = useQuery({
    queryKey: ['resources'],
    queryFn: () => resourceApi.getResources().then(r => r.data)
  });

  const handleSummarize = async (id) => {
    setSummarizing(id);
    try {
      await resourceApi.summarizeResource(id);
      toast.success('Summary generated!');
      qc.invalidateQueries(['resources']);
    } catch {
      toast.error('Summarization failed');
    } finally {
      setSummarizing(null);
    }
  };

  const typeIcon = { pdf: FileText, youtube: Video, web: Globe };
  const typeColor = { pdf: 'bg-red-50 text-red-700', youtube: 'bg-red-100 text-red-800', web: 'bg-blue-50 text-blue-700' };

  return (
    <Layout title="Resources">
      <div className="flex justify-between items-center mb-6">
        <p className="text-slate-500 text-sm">{resources?.length || 0} resources available</p>
        <button onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700">
          <Upload size={16} /> Add Resource
        </button>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-20">
          <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {resources?.map(resource => {
            const Icon = typeIcon[resource.resource_type] || FileText;
            const colorClass = typeColor[resource.resource_type] || 'bg-slate-50 text-slate-700';
            return (
              <div key={resource.id} className="bg-white rounded-xl border border-slate-100 p-5 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-3">
                  <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium ${colorClass}`}>
                    <Icon size={12} /> {resource.resource_type?.toUpperCase()}
                  </div>
                  {resource.is_indexed && (
                    <span className="text-xs bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded-full">Indexed</span>
                  )}
                </div>
                <h3 className="font-semibold text-slate-900 mb-1 line-clamp-2">{resource.title}</h3>
                {resource.summary && (
                  <p className="text-xs text-slate-500 line-clamp-3 mb-3">{resource.summary}</p>
                )}
                <div className="flex gap-2 mt-3">
                  <button onClick={() => handleSummarize(resource.id)} disabled={summarizing === resource.id}
                    className="flex items-center gap-1 px-2.5 py-1.5 bg-indigo-50 text-indigo-700 rounded-lg text-xs hover:bg-indigo-100 disabled:opacity-60">
                    <Sparkles size={12} /> {summarizing === resource.id ? '...' : 'Summarize'}
                  </button>
                  {resource.url && (
                    <a href={resource.url} target="_blank" rel="noreferrer"
                      className="flex items-center gap-1 px-2.5 py-1.5 bg-slate-100 text-slate-600 rounded-lg text-xs hover:bg-slate-200">
                      <LinkIcon size={12} /> Open
                    </a>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {resources?.length === 0 && !isLoading && (
        <div className="text-center py-20 text-slate-400">
          <FileText size={48} className="mx-auto mb-3 opacity-30" />
          <p className="font-medium">No resources yet</p>
          <p className="text-sm mt-1">Upload PDFs, add YouTube videos, or ingest web pages</p>
        </div>
      )}

      {showModal && <UploadModal onClose={() => setShowModal(false)} />}
    </Layout>
  );
}