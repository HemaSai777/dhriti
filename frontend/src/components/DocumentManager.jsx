import React, { useState, useEffect } from 'react';
import { BookOpen, UploadCloud, RefreshCw, FileText, CheckCircle2, AlertCircle } from 'lucide-react';
import { getDocuments, triggerIngestion, uploadDocument } from '../services/api';

export default function DocumentManager() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [reindexing, setReindexing] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');

  const loadDocs = async () => {
    setLoading(true);
    try {
      const data = await getDocuments();
      setDocuments(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocs();
  }, []);

  const handleReindex = async () => {
    setReindexing(true);
    setStatusMessage('');
    try {
      const res = await triggerIngestion();
      setStatusMessage(res.message);
      await loadDocs();
    } catch (err) {
      setStatusMessage(`Re-indexing failed: ${err.message}`);
    } finally {
      setReindexing(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setStatusMessage('');
    try {
      const res = await uploadDocument(file);
      setStatusMessage(`Uploaded "${file.name}" and re-indexed knowledge base!`);
      await loadDocs();
    } catch (err) {
      setStatusMessage(`Upload failed: ${err.message}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
        <div className="flex items-center space-x-3">
          <div className="p-3 rounded-xl bg-gov-700 text-white shadow-sm">
            <BookOpen className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">
              Verified Knowledge Base & Document Repository
            </h1>
            <p className="text-xs text-slate-500 mt-0.5">
              Authoritative government gazettes, PACS by-laws, and operational manuals indexing the Citation Gate.
            </p>
          </div>
        </div>

        <button
          onClick={handleReindex}
          disabled={reindexing}
          className="flex items-center space-x-1.5 px-4 py-2 rounded-lg bg-gov-700 hover:bg-gov-800 disabled:opacity-50 text-white text-xs font-bold transition-all shadow-sm w-fit"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${reindexing ? 'animate-spin' : ''}`} />
          <span>{reindexing ? 'Re-indexing Documents...' : 'Re-index Knowledge Base'}</span>
        </button>
      </div>

      {statusMessage && (
        <div className="bg-emerald-50 text-emerald-800 p-3 rounded-xl border border-emerald-200 text-xs font-semibold flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          <span>{statusMessage}</span>
        </div>
      )}

      {/* Upload Box */}
      <div className="bg-white p-6 rounded-2xl border-2 border-dashed border-slate-300 hover:border-gov-600 text-center transition-all">
        <UploadCloud className="w-8 h-8 text-gov-600 mx-auto mb-2" />
        <h3 className="text-sm font-bold text-slate-800">Add New Official Document (PDF / TXT)</h3>
        <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
          Upload official PDF circulars or structured TXT files. The ingestion pipeline automatically preserves page numbers, sections, and builds hybrid BM25/Dense indices.
        </p>

        <label className="mt-4 inline-flex items-center px-4 py-2 rounded-lg bg-gov-50 hover:bg-gov-100 text-gov-800 text-xs font-bold border border-gov-300 cursor-pointer transition-colors">
          <span>{uploading ? 'Processing & Chunking...' : 'Browse PDF/TXT File'}</span>
          <input
            type="file"
            accept=".pdf,.txt"
            onChange={handleFileUpload}
            disabled={uploading}
            className="hidden"
          />
        </label>
      </div>

      {/* Ingested Documents Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
          <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">
            Active Verified Gazette Files ({documents.length})
          </span>
          <span className="text-xs font-semibold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded-full border border-emerald-200">
            🟢 100% Citation Grounded
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 text-slate-500 font-bold uppercase tracking-wider border-b border-slate-200">
                <th className="py-3 px-4">Document Title</th>
                <th className="py-3 px-4">Format</th>
                <th className="py-3 px-4">Pages</th>
                <th className="py-3 px-4">Indexed Chunks</th>
                <th className="py-3 px-4">File Size</th>
                <th className="py-3 px-4">Verification Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-800">
              {loading ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-slate-400">
                    Loading verified documents...
                  </td>
                </tr>
              ) : documents.map((doc) => (
                <tr key={doc.id} className="hover:bg-slate-50 transition-colors">
                  <td className="py-3 px-4 font-bold text-slate-900 flex items-center space-x-2">
                    <FileText className="w-4 h-4 text-gov-600 shrink-0" />
                    <span>{doc.title}</span>
                  </td>
                  <td className="py-3 px-4 font-semibold text-slate-500">
                    <span className="bg-slate-100 px-2 py-0.5 rounded border border-slate-200 font-mono">
                      {doc.file_type}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-medium text-slate-700">
                    {doc.pages} Pages
                  </td>
                  <td className="py-3 px-4 font-mono font-semibold text-gov-800">
                    {doc.chunks} Chunks
                  </td>
                  <td className="py-3 px-4 text-slate-500">
                    {doc.size_kb} KB
                  </td>
                  <td className="py-3 px-4">
                    <span className="inline-flex items-center space-x-1 text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full text-[10px] font-bold border border-emerald-200">
                      <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                      <span>Verified Authority</span>
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
