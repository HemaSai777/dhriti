import React from 'react';
import { ShieldCheck, Globe, Users, BookOpen, MessageSquare, WifiOff, Wifi } from 'lucide-react';

export default function Header({ 
  activeTab, 
  setActiveTab, 
  selectedLanguage, 
  setSelectedLanguage,
  isOffline,
  setIsOffline
}) {
  const languages = [
    { code: 'en', label: 'English' },
    { code: 'ta', label: 'தமிழ்' },
    { code: 'hi', label: 'हिन्दी' }
  ];

  return (
    <header className="bg-slate-900 border-b border-slate-800 text-white sticky top-0 z-40 shadow-md">
      {/* Top emergency / public-service bar */}
      <div className="bg-gov-800 px-4 py-1 text-xs text-gov-100 flex justify-between items-center border-b border-gov-700">
        <div className="flex items-center space-x-2">
          <span className="inline-block w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span className="font-medium tracking-wide">OFFICIAL PUBLIC SERVICE ASSISTANCE • CITATION-GATED VERIFICATION</span>
        </div>
        <div className="flex items-center space-x-4">
          <button
            onClick={() => setIsOffline(!isOffline)}
            className={`flex items-center space-x-1 px-2 py-0.5 rounded text-xs transition-colors ${
              isOffline ? 'bg-amber-600 text-white font-semibold' : 'text-slate-300 hover:text-white'
            }`}
            title="Toggle Offline Kiosk Mode"
          >
            {isOffline ? <WifiOff className="w-3 h-3" /> : <Wifi className="w-3 h-3 text-emerald-400" />}
            <span>{isOffline ? 'Offline Kiosk Active' : 'Online Mode'}</span>
          </button>
          <span className="text-slate-400">PACS / PMFBY Helpline: 1800-180-1551</span>
        </div>
      </div>

      {/* Main Header */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo & Identity */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('chat')}>
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-gov-500 to-teal-700 flex items-center justify-center shadow-lg border border-teal-400/30">
              <ShieldCheck className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xl font-bold tracking-tight text-white">SAHAYA</span>
                <span className="text-xs px-2 py-0.5 rounded-full bg-gov-700 text-teal-200 border border-gov-600 font-medium">
                  सहाय
                </span>
                <span className="text-xs px-2 py-0.5 rounded-full bg-gov-700 text-teal-200 border border-gov-600 font-medium">
                  சகாயா
                </span>
              </div>
              <p className="text-xs text-slate-400 font-normal">
                Multilingual Cooperative Governance & Legal Assistance
              </p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="hidden md:flex space-x-1 bg-slate-800/80 p-1 rounded-xl border border-slate-700">
            <button
              onClick={() => setActiveTab('chat')}
              className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === 'chat'
                  ? 'bg-gov-600 text-white shadow-sm'
                  : 'text-slate-300 hover:text-white hover:bg-slate-700/50'
              }`}
            >
              <MessageSquare className="w-3.5 h-3.5" />
              <span>Citizen Assistant</span>
            </button>

            <button
              onClick={() => setActiveTab('officer')}
              className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === 'officer'
                  ? 'bg-gov-600 text-white shadow-sm'
                  : 'text-slate-300 hover:text-white hover:bg-slate-700/50'
              }`}
            >
              <Users className="w-3.5 h-3.5" />
              <span>Officer Portal</span>
            </button>

            <button
              onClick={() => setActiveTab('documents')}
              className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === 'documents'
                  ? 'bg-gov-600 text-white shadow-sm'
                  : 'text-slate-300 hover:text-white hover:bg-slate-700/50'
              }`}
            >
              <BookOpen className="w-3.5 h-3.5" />
              <span>Verified Documents</span>
            </button>
          </nav>

          {/* Right Controls: Trust badge + Language Selector */}
          <div className="flex items-center space-x-3">
            <div className="hidden lg:flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-emerald-950/60 border border-emerald-500/40 text-emerald-400 text-xs">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span className="font-semibold">Verified Knowledge Base</span>
            </div>

            {/* Language Selector */}
            <div className="flex items-center bg-slate-800 border border-slate-700 rounded-lg p-0.5">
              <Globe className="w-3.5 h-3.5 text-slate-400 ml-2 mr-1" />
              <select
                value={selectedLanguage}
                onChange={(e) => setSelectedLanguage(e.target.value)}
                className="bg-transparent text-xs font-medium text-slate-200 py-1 pr-2 pl-1 rounded focus:outline-none cursor-pointer"
              >
                {languages.map((l) => (
                  <option key={l.code} value={l.code} className="bg-slate-900 text-white">
                    {l.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
