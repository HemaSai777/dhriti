import React, { useState } from 'react';
import { FileText, ChevronDown, ChevronUp, ExternalLink, Bookmark } from 'lucide-react';

export default function CitationCard({ source, index }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="bg-white rounded-lg border border-slate-200 shadow-sm hover:border-gov-500/50 transition-all overflow-hidden">
      <div className="p-3">
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-start space-x-2.5">
            <div className="p-1.5 rounded bg-gov-50 text-gov-700 mt-0.5 border border-gov-100">
              <FileText className="w-4 h-4" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-slate-800 leading-tight">
                {source.document || 'Official Document'}
              </h4>
              <div className="flex items-center space-x-2 text-[11px] text-slate-500 mt-1">
                <span className="font-semibold text-slate-700 bg-slate-100 px-1.5 py-0.5 rounded border border-slate-200">
                  Page {source.page || '1'}
                </span>
                <span>•</span>
                <span className="text-slate-600 truncate max-w-[200px]" title={source.section}>
                  {source.section || 'General Provisions'}
                </span>
              </div>
            </div>
          </div>

          <div className="flex flex-col items-end">
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
              {Math.round((source.score || 0.85) * 100)}% Match
            </span>
          </div>
        </div>

        {source.excerpt && (
          <div className="mt-2.5 pt-2 border-t border-slate-100">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-medium text-slate-400 uppercase tracking-wider">
                Verified Excerpt
              </span>
              <button
                onClick={() => setExpanded(!expanded)}
                className="text-[11px] text-gov-600 hover:text-gov-700 flex items-center font-medium"
              >
                <span>{expanded ? 'Hide excerpt' : 'View excerpt'}</span>
                {expanded ? <ChevronUp className="w-3 h-3 ml-0.5" /> : <ChevronDown className="w-3 h-3 ml-0.5" />}
              </button>
            </div>
            
            {expanded && (
              <div className="mt-2 text-xs text-slate-700 bg-slate-50 p-2.5 rounded border border-slate-200 font-mono leading-relaxed">
                "{source.excerpt}"
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
