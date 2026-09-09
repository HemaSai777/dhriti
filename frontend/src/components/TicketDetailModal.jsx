import React, { useState } from 'react';
import { X, ShieldAlert, CheckCircle2, Clock, AlertTriangle, ArrowUpRight, Save, FileText, User } from 'lucide-react';
import { updateTicket } from '../services/api';

export default function TicketDetailModal({ ticket, onClose, onTicketUpdated }) {
  const [status, setStatus] = useState(ticket?.status || 'PENDING');
  const [officerNotes, setOfficerNotes] = useState(ticket?.officer_notes || '');
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  if (!ticket) return null;

  const handleStatusChange = async (newStatus) => {
    setStatus(newStatus);
    await handleSave(newStatus, officerNotes);
  };

  const handleSave = async (overrideStatus, notes) => {
    setSaving(true);
    setSaveSuccess(false);
    try {
      const updated = await updateTicket(ticket.id, {
        status: overrideStatus || status,
        officer_notes: notes !== undefined ? notes : officerNotes
      });
      if (onTicketUpdated) onTicketUpdated(updated);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 2500);
    } catch (err) {
      alert(`Error updating ticket: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  const candidateChunks = ticket.candidate_chunks || [];

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-3xl w-full overflow-hidden border border-slate-200 animate-in fade-in zoom-in duration-150">
        {/* Modal Header */}
        <div className="bg-slate-900 text-white px-6 py-4 flex items-center justify-between border-b border-slate-800">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-amber-500 text-white">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-base font-bold font-mono tracking-tight">{ticket.id}</h3>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ${
                  status === 'RESOLVED' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' :
                  status === 'UNDER_REVIEW' ? 'bg-blue-500/20 text-blue-300 border border-blue-500/40' :
                  status === 'ESCALATED' ? 'bg-purple-500/20 text-purple-300 border border-purple-500/40' :
                  'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                }`}>
                  {status.replace('_', ' ')}
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Created: {ticket.created_at} • Citizen ID: {ticket.user_id}
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Content */}
        <div className="p-6 space-y-6 max-h-[75vh] overflow-y-auto">
          {/* Query & Metadata */}
          <div>
            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1.5">
              Original Citizen Query
            </label>
            <div className="text-sm font-medium text-slate-900 bg-slate-50 p-3.5 rounded-xl border border-slate-200">
              "{ticket.query}"
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-3">
              <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
                <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">Intent</span>
                <span className="text-xs font-bold text-slate-800">{ticket.intent}</span>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
                <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">Language</span>
                <span className="text-xs font-bold text-slate-800 uppercase">{ticket.language}</span>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
                <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">Gate Confidence</span>
                <span className="text-xs font-bold text-amber-700">{Math.round((ticket.confidence || 0) * 100)}%</span>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
                <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">Required Threshold</span>
                <span className="text-xs font-bold text-slate-700">75% - 85%</span>
              </div>
            </div>
          </div>

          {/* Reason for Escalation */}
          {ticket.reason && (
            <div>
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1.5">
                Verification Failure Reason
              </label>
              <div className="text-xs text-amber-900 bg-amber-50 p-3 rounded-lg border border-amber-200 font-medium">
                {ticket.reason}
              </div>
            </div>
          )}

          {/* Candidate Chunks Retrieved */}
          <div>
            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1.5 flex items-center justify-between">
              <span>Retrieved Candidate Chunks ({candidateChunks.length})</span>
              <span className="text-[11px] font-normal text-slate-400">Scored below safety threshold</span>
            </label>

            {candidateChunks.length === 0 ? (
              <div className="text-xs text-slate-400 italic p-3 bg-slate-50 rounded-lg border border-dashed border-slate-200">
                No matching chunks found in verified index for this query.
              </div>
            ) : (
              <div className="space-y-2">
                {candidateChunks.map((chunk, idx) => (
                  <div key={idx} className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs">
                    <div className="flex items-center justify-between text-slate-700 font-semibold mb-1">
                      <span className="truncate">{chunk.title || 'Document'} (Page {chunk.page}, {chunk.section})</span>
                      <span className="text-[11px] font-bold text-slate-500 shrink-0 ml-2">
                        Match: {Math.round((chunk.score || 0) * 100)}%
                      </span>
                    </div>
                    <p className="text-slate-600 font-mono text-[11px] leading-relaxed">
                      "{chunk.excerpt || chunk.text}"
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Officer Actions & Status */}
          <div className="border-t border-slate-200 pt-5">
            <label className="text-xs font-bold text-slate-700 uppercase tracking-wider block mb-2.5">
              Cooperative Officer Actions
            </label>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 mb-4">
              <button
                type="button"
                onClick={() => handleStatusChange('RESOLVED')}
                className={`py-2 px-3 rounded-lg text-xs font-bold transition-all flex items-center justify-center space-x-1.5 border ${
                  status === 'RESOLVED'
                    ? 'bg-emerald-600 text-white border-emerald-700 shadow-sm'
                    : 'bg-white text-emerald-800 border-emerald-300 hover:bg-emerald-50'
                }`}
              >
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Mark Resolved</span>
              </button>

              <button
                type="button"
                onClick={() => handleStatusChange('UNDER_REVIEW')}
                className={`py-2 px-3 rounded-lg text-xs font-bold transition-all flex items-center justify-center space-x-1.5 border ${
                  status === 'UNDER_REVIEW'
                    ? 'bg-blue-600 text-white border-blue-700 shadow-sm'
                    : 'bg-white text-blue-800 border-blue-300 hover:bg-blue-50'
                }`}
              >
                <Clock className="w-3.5 h-3.5" />
                <span>Request Info / Review</span>
              </button>

              <button
                type="button"
                onClick={() => handleStatusChange('ESCALATED')}
                className={`py-2 px-3 rounded-lg text-xs font-bold transition-all flex items-center justify-center space-x-1.5 border ${
                  status === 'ESCALATED'
                    ? 'bg-purple-600 text-white border-purple-700 shadow-sm'
                    : 'bg-white text-purple-800 border-purple-300 hover:bg-purple-50'
                }`}
              >
                <ArrowUpRight className="w-3.5 h-3.5" />
                <span>Escalate to Registrar</span>
              </button>
            </div>

            {/* Officer Remarks */}
            <div>
              <label className="text-xs font-semibold text-slate-600 block mb-1">
                Official Case Remarks / Action Log
              </label>
              <textarea
                value={officerNotes}
                onChange={(e) => setOfficerNotes(e.target.value)}
                rows={3}
                placeholder="Enter remarks, action taken, verified gazette reference, or citizen communication..."
                className="w-full text-xs p-3 rounded-lg border border-slate-300 focus:border-gov-600 focus:outline-none"
              />
              
              <div className="flex justify-between items-center mt-2">
                {saveSuccess ? (
                  <span className="text-xs text-emerald-600 font-bold flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Saved successfully in database!</span>
                  </span>
                ) : <span />}

                <button
                  onClick={() => handleSave(status, officerNotes)}
                  disabled={saving}
                  className="px-4 py-1.5 rounded-lg bg-gov-700 hover:bg-gov-800 text-white text-xs font-bold transition-colors flex items-center space-x-1.5 shadow-sm"
                >
                  <Save className="w-3.5 h-3.5" />
                  <span>{saving ? 'Saving...' : 'Save Case Notes'}</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="bg-slate-50 px-6 py-3 border-t border-slate-200 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 text-xs font-bold text-slate-600 hover:text-slate-900 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
