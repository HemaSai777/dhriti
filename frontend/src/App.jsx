import React, { useState } from 'react';
import Header from './components/Header';
import TrustBanner from './components/TrustBanner';
import ChatInterface from './components/ChatInterface';
import OfficerDashboard from './components/OfficerDashboard';
import DocumentManager from './components/DocumentManager';

export default function App() {
  const [activeTab, setActiveTab] = useState('chat'); // 'chat', 'officer', 'documents'
  const [selectedLanguage, setSelectedLanguage] = useState('en');
  const [isOffline, setIsOffline] = useState(false);
  const [selectedTicketId, setSelectedTicketId] = useState(null);

  const handleViewTicket = (ticketId) => {
    setSelectedTicketId(ticketId);
    setActiveTab('officer');
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-100 text-slate-900">
      {/* Civic Public Service Header */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        selectedLanguage={selectedLanguage}
        setSelectedLanguage={setSelectedLanguage}
        isOffline={isOffline}
        setIsOffline={setIsOffline}
      />

      {/* Safety Gate Architecture Doctrine */}
      <TrustBanner />

      {/* Offline Mode Alert Bar */}
      {isOffline && (
        <div className="bg-amber-600 text-white px-4 py-2 text-center text-xs font-bold shadow-inner">
          ⚠️ OFFLINE KIOSK MODE ACTIVE — Using local static cache for common questions. Network verification is paused.
        </div>
      )}

      {/* Main Content Body */}
      <main className="flex-1">
        {activeTab === 'chat' && (
          <ChatInterface
            selectedLanguage={selectedLanguage}
            onViewTicket={handleViewTicket}
            isOffline={isOffline}
          />
        )}

        {activeTab === 'officer' && (
          <OfficerDashboard
            initialSelectedTicketId={selectedTicketId}
          />
        )}

        {activeTab === 'documents' && (
          <DocumentManager />
        )}
      </main>
    </div>
  );
}
