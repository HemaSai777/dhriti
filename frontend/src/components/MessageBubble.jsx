import React from 'react';
import { User, ShieldCheck, AlertCircle, FileText, CheckCircle2 } from 'lucide-react';
import CitationCard from './CitationCard';
import EscalationCard from './EscalationCard';

export default function MessageBubble({ message, onViewTicket }) {
  const isUser = message.sender === 'user';

  if (isUser) {
    return (
      <div className="flex justify-end mb-4">
        <div className="flex items-start space-x-2.5 max-w-2xl">
          <div className="bg-gov-700 text-white px-4 py-3 rounded-2xl rounded-tr-none shadow-sm text-sm leading-relaxed">
            {message.text}
          </div>
          <div className="w-8 h-8 rounded-full bg-slate-200 text-slate-700 flex items-center justify-center shrink-0 border border-slate-300">
            <User className="w-4 h-4" />
          </div>
        </div>
      </div>
    );
  }

  // Assistant Response
  const isSupported = message.status === 'SUPPORTED';
  const confidencePct = Math.round((message.confidence || 0.9) * 100);

  return (
    <div className="flex justify-start mb-6">
      <div className="flex items-start space-x-2.5 max-w-3xl w-full">
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-gov-600 to-teal-800 text-white flex items-center justify-center shrink-0 shadow-sm border border-teal-500/30 mt-1">
          <ShieldCheck className="w-4 h-4" />
        </div>

        <div className="flex-1">
          {/* Main Answer or Escalation Box */}
          <div className="bg-white rounded-2xl rounded-tl-none border border-slate-200 p-4 sm:p-5 shadow-sm">
            {/* Header: Verified vs Escalated Indicator */}
            <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-3 flex-wrap gap-2">
              <div className="flex items-center space-x-2">
                {isSupported ? (
                  <span className="flex items-center space-x-1 px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-300 text-xs font-bold">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                    <span>✓ Verified Answer</span>
                  </span>
                ) : (
                  <span className="flex items-center space-x-1 px-2.5 py-1 rounded-full bg-amber-50 text-amber-800 border border-amber-300 text-xs font-bold">
                    <AlertCircle className="w-3.5 h-3.5 text-amber-600" />
                    <span>⚠ Insufficient Evidence</span>
                  </span>
                )}

                {message.intent && (
                  <span className="text-[11px] font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                    Intent: {message.intent.replace('_', ' ')}
                  </span>
                )}
              </div>

              {/* Confidence Score Gauge */}
              <div className="flex items-center space-x-2">
                <span className="text-xs text-slate-500 font-medium">Confidence:</span>
                <div className="flex items-center space-x-1">
                  <span className={`text-xs font-extrabold ${
                    isSupported ? 'text-emerald-700' : 'text-amber-700'
                  }`}>
                    {confidencePct}%
                  </span>
                  <div className="w-16 h-2 bg-slate-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        isSupported ? 'bg-emerald-500' : 'bg-amber-500'
                      }`}
                      style={{ width: `${Math.min(100, Math.max(10, confidencePct))}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Answer Content */}
            {isSupported ? (
              <div className="text-sm text-slate-800 leading-relaxed space-y-2">
                <p className="whitespace-pre-line">{message.answer}</p>
              </div>
            ) : (
              <EscalationCard
                ticketId={message.ticket_id}
                reason={message.reason}
                confidence={message.confidence}
                threshold={message.threshold}
                intent={message.intent}
                onViewTicket={onViewTicket}
              />
            )}

            {/* Sources & Citations section (Only when supported) */}
            {isSupported && message.sources && message.sources.length > 0 && (
              <div className="mt-4 pt-3 border-t border-slate-100">
                <div className="flex items-center space-x-1.5 mb-2.5">
                  <FileText className="w-3.5 h-3.5 text-gov-600" />
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-600">
                    Verified Sources & Citations ({message.sources.length})
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
                  {message.sources.map((src, idx) => (
                    <CitationCard key={idx} source={src} index={idx} />
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
