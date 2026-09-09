import React, { useState, useEffect } from 'react';
import { 
  Users, AlertTriangle, CheckCircle2, Clock, ArrowUpRight, 
  Search, Filter, RefreshCw, Eye, ShieldCheck, FileSpreadsheet
} from 'lucide-react';
import { getTickets, getStats } from '../services/api';
import TicketDetailModal from './TicketDetailModal';

export default function OfficerDashboard({ initialSelectedTicketId }) {
  const [tickets, setTickets] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedTicket, setSelectedTicket] = useState(null);

  // Filters
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [intentFilter, setIntentFilter] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  const loadData = async () => {
    setLoading(true);
    try {
      const [ticketsData, statsData] = await Promise.all([
        getTickets({ status: statusFilter, intent: intentFilter, search: searchQuery }),
        getStats()
      ]);
      setTickets(ticketsData);
      setStats(statsData);

      // If an initial ticket ID was passed, open it immediately
      if (initialSelectedTicketId) {
        const found = ticketsData.find(t => t.id === initialSelectedTicketId);
        if (found) setSelectedTicket(found);
      }
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [statusFilter, intentFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    loadData();
  };

  const handleTicketUpdated = (updatedTicket) => {
    setTickets(prev => prev.map(t => t.id === updatedTicket.id ? updatedTicket : t));
    setSelectedTicket(updatedTicket);
    getStats().then(setStats).catch(() => {});
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      {/* Officer Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
        <div className="flex items-center space-x-3">
          <div className="p-3 rounded-xl bg-gov-700 text-white shadow-sm">
            <Users className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">
              Cooperative Officer Grievance & Escalation Portal
            </h1>
            <p className="text-xs text-slate-500 mt-0.5">
              Review citizen queries rejected by the Citation Safety Gate due to insufficient supporting evidence.
            </p>
          </div>
        </div>

        <button
          onClick={loadData}
          disabled={loading}
          className="flex items-center space-x-1.5 px-3.5 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold transition-colors w-fit"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-gov-600' : ''}`} />
          <span>Refresh Queue</span>
        </button>
      </div>

      {/* KPI Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-3">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Grievances</span>
            <AlertTriangle className="w-4 h-4 text-slate-400" />
          </div>
          <div className="text-2xl font-extrabold text-slate-900 mt-1">
            {stats?.total_tickets ?? '—'}
          </div>
          <span className="text-[10px] text-slate-400 mt-1 block">Escalated queries</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-amber-600 uppercase tracking-wider">Pending Action</span>
            <Clock className="w-4 h-4 text-amber-500" />
          </div>
          <div className="text-2xl font-extrabold text-amber-600 mt-1">
            {stats?.pending ?? '—'}
          </div>
          <span className="text-[10px] text-amber-700/80 mt-1 block">Awaiting officer initial review</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-blue-600 uppercase tracking-wider">Under Review</span>
            <Users className="w-4 h-4 text-blue-500" />
          </div>
          <div className="text-2xl font-extrabold text-blue-600 mt-1">
            {stats?.under_review ?? '—'}
          </div>
          <span className="text-[10px] text-blue-600/80 mt-1 block">Fact-checking in progress</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-purple-600 uppercase tracking-wider">Escalated (Tier 2)</span>
            <ArrowUpRight className="w-4 h-4 text-purple-500" />
          </div>
          <div className="text-2xl font-extrabold text-purple-600 mt-1">
            {stats?.escalated ?? '—'}
          </div>
          <span className="text-[10px] text-purple-600/80 mt-1 block">District Registrar queue</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-emerald-600 uppercase tracking-wider">Resolved</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="text-2xl font-extrabold text-emerald-600 mt-1">
            {stats?.resolved ?? '—'}
          </div>
          <span className="text-[10px] text-emerald-600/80 mt-1 block">Official order passed</span>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row items-center justify-between gap-3">
        {/* Search */}
        <form onSubmit={handleSearchSubmit} className="relative w-full md:w-80">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search Ticket ID or query words..."
            className="w-full text-xs pl-9 pr-3 py-2 rounded-lg border border-slate-300 focus:border-gov-600 focus:outline-none"
          />
          <Search className="w-4 h-4 text-slate-400 absolute left-2.5 top-2.5" />
        </form>

        {/* Filters */}
        <div className="flex items-center space-x-2.5 w-full md:w-auto overflow-x-auto">
          <div className="flex items-center space-x-1.5 text-xs text-slate-500">
            <Filter className="w-3.5 h-3.5" />
            <span className="font-medium">Status:</span>
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="text-xs border border-slate-300 rounded-lg py-1.5 px-2.5 bg-white text-slate-800 focus:outline-none"
          >
            <option value="ALL">All Statuses</option>
            <option value="PENDING">Pending Action</option>
            <option value="UNDER_REVIEW">Under Review</option>
            <option value="RESOLVED">Resolved</option>
            <option value="ESCALATED">Escalated</option>
          </select>

          <div className="flex items-center space-x-1.5 text-xs text-slate-500 ml-2">
            <span className="font-medium">Intent:</span>
          </div>
          <select
            value={intentFilter}
            onChange={(e) => setIntentFilter(e.target.value)}
            className="text-xs border border-slate-300 rounded-lg py-1.5 px-2.5 bg-white text-slate-800 focus:outline-none"
          >
            <option value="ALL">All Intents</option>
            <option value="PMFBY_CLAIM">PMFBY Claim</option>
            <option value="COOPERATIVE_BYLAW">Cooperative By-law</option>
            <option value="SCHEME_ELIGIBILITY">Scheme Eligibility</option>
            <option value="GRIEVANCE">Grievance</option>
          </select>
        </div>
      </div>

      {/* Tickets Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-bold uppercase tracking-wider">
                <th className="py-3 px-4">Ticket ID</th>
                <th className="py-3 px-4">Citizen Question</th>
                <th className="py-3 px-4">Intent</th>
                <th className="py-3 px-4">Lang</th>
                <th className="py-3 px-4">Confidence</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Created At</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-800">
              {loading ? (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-slate-400">
                    Loading grievance queue...
                  </td>
                </tr>
              ) : tickets.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-slate-400">
                    No grievance tickets match the selected filters.
                  </td>
                </tr>
              ) : (
                tickets.map((t) => (
                  <tr key={t.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3 px-4 font-mono font-bold text-gov-800">
                      {t.id}
                    </td>
                    <td className="py-3 px-4 font-medium max-w-xs truncate" title={t.query}>
                      {t.query}
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 text-[11px] font-semibold">
                        {t.intent}
                      </span>
                    </td>
                    <td className="py-3 px-4 uppercase font-semibold text-slate-500">
                      {t.language}
                    </td>
                    <td className="py-3 px-4">
                      <span className="font-extrabold text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                        {Math.round((t.confidence || 0) * 100)}%
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wide border ${
                        t.status === 'RESOLVED' ? 'bg-emerald-50 text-emerald-800 border-emerald-300' :
                        t.status === 'UNDER_REVIEW' ? 'bg-blue-50 text-blue-800 border-blue-300' :
                        t.status === 'ESCALATED' ? 'bg-purple-50 text-purple-800 border-purple-300' :
                        'bg-amber-50 text-amber-800 border-amber-300'
                      }`}>
                        {t.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-500 whitespace-nowrap text-[11px]">
                      {t.created_at}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => setSelectedTicket(t)}
                        className="px-2.5 py-1 rounded bg-gov-700 hover:bg-gov-800 text-white font-bold text-[11px] transition-colors flex items-center space-x-1 ml-auto shadow-sm"
                      >
                        <Eye className="w-3 h-3" />
                        <span>Inspect</span>
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Ticket Details Inspection Drawer */}
      {selectedTicket && (
        <TicketDetailModal
          ticket={selectedTicket}
          onClose={() => setSelectedTicket(null)}
          onTicketUpdated={handleTicketUpdated}
        />
      )}
    </div>
  );
}
