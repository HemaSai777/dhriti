import React from 'react';
import { ShieldCheck, AlertOctagon, CheckCircle2, UserCheck, ArrowRight, Lock } from 'lucide-react';

export default function TrustBanner() {
  return (
    <div className="bg-gradient-to-r from-slate-900 via-gov-900 to-slate-900 border-b border-gov-700/50 py-3.5 px-4 text-white">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-3 text-xs">
        {/* Core Doctrine */}
        <div className="flex items-center space-x-3">
          <div className="p-1.5 rounded-md bg-amber-500/20 border border-amber-500/40 text-amber-400">
            <Lock className="w-4 h-4" />
          </div>
          <div>
            <div className="font-bold text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
              <span>Safety Rule:</span>
              <span className="text-white bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
                NO EVIDENCE → NO ANSWER → HUMAN ESCALATION
              </span>
            </div>
            <p className="text-slate-300 text-[11px] mt-0.5">
              Legal, financial, and PMFBY claims require strict grounding in verified government gazettes and by-laws.
            </p>
          </div>
        </div>

        {/* Verification Pipeline Diagram */}
        <div className="flex items-center space-x-2 bg-slate-950/70 px-3 py-1.5 rounded-lg border border-slate-800 text-[11px] text-slate-300">
          <span className="text-teal-400 font-semibold">1. Hybrid Retrieval</span>
          <ArrowRight className="w-3 h-3 text-slate-500" />
          <span className="text-teal-400 font-semibold">2. Entailment Gate</span>
          <ArrowRight className="w-3 h-3 text-slate-500" />
          <span className="flex items-center text-emerald-400 font-bold gap-1">
            <CheckCircle2 className="w-3 h-3" />
            <span>&ge; 75%/85% Verified Answer</span>
          </span>
          <span className="text-slate-600">|</span>
          <span className="flex items-center text-amber-400 font-bold gap-1">
            <AlertOctagon className="w-3 h-3" />
            <span>&lt; 75% Escalation Ticket</span>
          </span>
        </div>
      </div>
    </div>
  );
}
