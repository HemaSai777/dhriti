import React, { useState } from 'react';
import { AlertTriangle, UserCheck, ArrowRight, Copy, Check, ShieldAlert, FileSearch } from 'lucide-react';

export default function EscalationCard({ ticketId, reason, confidence, threshold, intent, onViewTicket }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (ticketId) {
      navigator.clipboard.writeText(ticketId);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="bg-gradient-to-br from-amber-50 to-orange-50/50 rounded-xl border-2 border-amber-300 p-4 sm:p-5 shadow-sm text-slate-900 mt-3">
      {/* Alert Header */}
      <div className="flex items-start space-x-3">
        <div className="p-2.5 rounded-lg bg-amber-500 text-white shadow-sm shrink-0">
          <AlertTriangle className="w-5 h-5" />
        </div>
        <div className="flex-1">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <span className="text-xs font-extrabold uppercase tracking-wider text-amber-900 bg-amber-200/80 px-2 py-0.5 rounded border border-amber-300">
              ⚠️ VERIFIED INFORMATION NOT FOUND
            </span>
            <span className="text-xs font-semibold text-amber-800 bg-amber-100 px-2 py-0.5 rounded-full border border-amber-200">
              Confidence: {Math.round((confidence || 0.45) * 100)}% (Threshold: {Math.round((threshold || 0.75) * 100)}%)
            </span>
          </div>

          <h3 className="text-sm font-bold text-slate-900 mt-2">
            Human Officer Review Required
          </h3>
          <p className="text-xs text-slate-700 mt-1 leading-relaxed">
            I couldn't find sufficient supporting evidence in the verified knowledge base to answer this safely. To prevent misinformation on legal, scheme, and financial matters, the unverified answer has been discarded.
          </p>
        </div>
      </div>

      {/* Escalation Details Box */}
      <div className="mt-4 bg-white/90 rounded-lg p-3.5 border border-amber-200 space-y-2.5">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <div>
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">
              Official Grievance Ticket ID
            </span>
            <div className="flex items-center space-x-2 mt-0.5">
              <span className="text-base font-extrabold font-mono text-gov-800 tracking-tight">
                {ticketId || 'GRV-2026-PENDING'}
              </span>
              <button
                onClick={handleCopy}
                className="text-slate-400 hover:text-slate-600 p-1 rounded hover:bg-slate-100 transition-colors"
                title="Copy Ticket ID"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
              </button>
            </div>
          </div>

          <div className="text-right">
            <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">
              Routing Destination
            </span>
            <span className="text-xs font-semibold text-slate-800">
              PACS Nodal Officer & Registrar Desk
            </span>
          </div>
        </div>

        {reason && (
          <div className="text-[11px] text-slate-600 bg-amber-50/70 p-2 rounded border border-amber-200/60">
            <span className="font-semibold text-amber-900">Safety Gate Reason: </span>
            {reason}
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="mt-4 flex items-center justify-between flex-wrap gap-2 pt-1">
        <div className="text-[11px] text-slate-500 flex items-center gap-1.5">
          <UserCheck className="w-3.5 h-3.5 text-gov-600" />
          <span>Assigned to Cooperative Grievance Officer queue</span>
        </div>

        <div className="flex items-center space-x-2">
          {onViewTicket && (
            <button
              onClick={() => onViewTicket(ticketId)}
              className="px-3 py-1.5 rounded-lg bg-gov-700 hover:bg-gov-800 text-white text-xs font-bold transition-all shadow-sm flex items-center space-x-1.5"
            >
              <span>View Ticket in Portal</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
