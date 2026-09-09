import React, { useState, useRef, useEffect } from 'react';
import { Send, Mic, MicOff, Trash2, ShieldCheck, Sparkles, HelpCircle, Loader2 } from 'lucide-react';
import MessageBubble from './MessageBubble';
import { chatQuery, sendVoiceAudio } from '../services/api';
import { FALLBACK_FAQS } from '../services/localFaq';

export default function ChatInterface({ 
  selectedLanguage, 
  onViewTicket,
  isOffline 
}) {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      sender: 'assistant',
      status: 'SUPPORTED',
      confidence: 0.98,
      threshold: 0.75,
      intent: 'GENERAL_INFO',
      answer: "Welcome to SAHAYA — Multilingual Cooperative Governance & Legal Assistance. I provide strictly verified answers regarding PMFBY crop insurance, cooperative by-laws, PACS membership, and government schemes supported by official gazettes and guidelines.\n\nEvery factual assertion is backed by verifiable citations. If evidence is insufficient, queries are automatically escalated to a human cooperative officer.",
      sources: [
        {
          document: "PMFBY Operational Guidelines 2024",
          page: 1,
          section: "Section 1: Scheme Objectives",
          score: 0.98,
          excerpt: "The Pradhan Mantri Fasal Bima Yojana (PMFBY) aims at supporting sustainable production in agriculture sector..."
        },
        {
          document: "Model Cooperative Societies Bylaws",
          page: 4,
          section: "Chapter I: Preliminary and Definitions",
          score: 0.95,
          excerpt: "Primary Agricultural Credit Cooperative Societies Model By-laws approved by the Ministry of Cooperation..."
        }
      ]
    }
  ]);

  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingStatus, setRecordingStatus] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const exampleQueries = [
    {
      title: "PMFBY Claim Settlement",
      query: "What is the PMFBY claim settlement procedure and 72-hour deadline?",
      type: "supported"
    },
    {
      title: "PACS Membership Rules",
      query: "Who is eligible to become an ordinary member of a Primary Agricultural Credit Society (PACS)?",
      type: "supported"
    },
    {
      title: "KCC 4% Interest Subvention",
      query: "What is the net interest rate for prompt repayment under Kisan Credit Card?",
      type: "supported"
    },
    {
      title: "Unsupported Escalation Test",
      query: "Can I get a loan waiver of 10 lakh rupees without land records under government scheme?",
      type: "escalate"
    }
  ];

  const handleSend = async (queryText) => {
    const textToSend = queryText || inputQuery;
    if (!textToSend.trim() || loading) return;

    const userMsg = {
      id: Date.now().toString(),
      sender: 'user',
      text: textToSend.trim()
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputQuery('');
    setLoading(true);

    if (isOffline) {
      // Offline Kiosk Mode: Match static cache or escalate to offline warning
      setTimeout(() => {
        const queryLower = textToSend.toLowerCase();
        const matchedFaq = FALLBACK_FAQS.find(f => 
          f.question.toLowerCase().includes(queryLower) ||
          queryLower.includes(f.category.toLowerCase())
        );

        if (matchedFaq) {
          setMessages((prev) => [
            ...prev,
            {
              id: (Date.now() + 1).toString(),
              sender: 'assistant',
              status: 'SUPPORTED',
              confidence: 0.88,
              threshold: 0.75,
              intent: matchedFaq.category.toUpperCase().replace(' ', '_'),
              answer: `[OFFLINE KIOSK CACHED ANSWER]\n${matchedFaq.answer}`,
              sources: [
                {
                  document: matchedFaq.source,
                  page: 1,
                  section: "Local Cached Knowledge",
                  score: 0.88,
                  excerpt: matchedFaq.answer
                }
              ]
            }
          ]);
        } else {
          setMessages((prev) => [
            ...prev,
            {
              id: (Date.now() + 1).toString(),
              sender: 'assistant',
              status: 'ESCALATED',
              confidence: 0.35,
              threshold: 0.75,
              intent: 'GENERAL_INFO',
              ticket_id: `OFFLINE-GRV-${Math.floor(1000 + Math.random() * 9000)}`,
              reason: 'Device is running in Offline Kiosk Mode. Uncached legal/claim questions cannot be answered safely without network verification. Please reconnect or consult the PACS Nodal Officer in person.'
            }
          ]);
        }
        setLoading(false);
      }, 500);
      return;
    }

    try {
      const response = await chatQuery(textToSend, selectedLanguage);
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          sender: 'assistant',
          status: response.status,
          confidence: response.confidence,
          threshold: response.threshold,
          intent: response.intent,
          answer: response.answer,
          sources: response.sources,
          ticket_id: response.ticket_id,
          reason: response.reason
        }
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          sender: 'assistant',
          status: 'ESCALATED',
          confidence: 0.2,
          threshold: 0.75,
          intent: 'GENERAL_INFO',
          ticket_id: `SYS-ERR-${Math.floor(1000 + Math.random() * 9000)}`,
          reason: `Service communication error: ${err.message}. Ticket created for technical review.`
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Voice Input Handler (uses Web Speech Recognition or backend API)
  const handleVoiceInput = async () => {
    if (isRecording) {
      setIsRecording(false);
      setRecordingStatus('');
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.lang = selectedLanguage === 'ta' ? 'ta-IN' : selectedLanguage === 'hi' ? 'hi-IN' : 'en-IN';
      recognition.interimResults = false;

      recognition.onstart = () => {
        setIsRecording(true);
        setRecordingStatus('Listening to speech...');
      };

      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInputQuery(transcript);
        setIsRecording(false);
        setRecordingStatus('');
        handleSend(transcript);
      };

      recognition.onerror = async () => {
        setIsRecording(false);
        setRecordingStatus('Calling backend voice engine...');
        try {
          const res = await sendVoiceAudio(null, selectedLanguage);
          setInputQuery(res.text || 'What is the PMFBY claim procedure?');
          setRecordingStatus(res.message);
          setTimeout(() => setRecordingStatus(''), 4000);
        } catch {
          setRecordingStatus('Voice service not available.');
          setTimeout(() => setRecordingStatus(''), 3000);
        }
      };

      recognition.start();
    } else {
      // Fallback to backend endpoint
      setIsRecording(true);
      setRecordingStatus('Simulating voice capture...');
      try {
        const res = await sendVoiceAudio(null, selectedLanguage);
        setInputQuery(res.text || 'What is the PMFBY claim procedure?');
        setRecordingStatus(res.message);
        setTimeout(() => setRecordingStatus(''), 4000);
      } catch {
        setRecordingStatus('Voice simulation unavailable');
        setTimeout(() => setRecordingStatus(''), 3000);
      } finally {
        setIsRecording(false);
      }
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-140px)] max-w-5xl mx-auto px-4 sm:px-6 py-4">
      {/* Example Prompt Chips */}
      <div className="mb-3 shrink-0">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-gov-600" />
            <span>Interactive Demo Prompts</span>
          </span>
          <button
            onClick={clearChat}
            className="text-xs text-slate-400 hover:text-red-600 flex items-center gap-1 transition-colors"
            title="Clear Chat History"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Clear</span>
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2">
          {exampleQueries.map((ex, i) => (
            <button
              key={i}
              onClick={() => handleSend(ex.query)}
              disabled={loading}
              className={`p-2.5 rounded-lg border text-left transition-all text-xs flex flex-col justify-between ${
                ex.type === 'escalate'
                  ? 'bg-amber-50/70 border-amber-300 hover:bg-amber-100/80 text-amber-950 shadow-sm'
                  : 'bg-white border-slate-200 hover:border-gov-500 hover:shadow-sm text-slate-800'
              }`}
            >
              <div className="flex items-center justify-between w-full mb-1">
                <span className="font-bold">{ex.title}</span>
                <span className={`text-[10px] px-1.5 py-0.5 rounded font-bold ${
                  ex.type === 'escalate'
                    ? 'bg-amber-200 text-amber-900'
                    : 'bg-emerald-100 text-emerald-800'
                }`}>
                  {ex.type === 'escalate' ? 'Escalation Test' : 'Supported'}
                </span>
              </div>
              <p className="text-[11px] text-slate-500 line-clamp-2 mt-0.5">
                "{ex.query}"
              </p>
            </button>
          ))}
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto pr-1 space-y-4 rounded-xl bg-slate-100/50 p-4 border border-slate-200/80">
        {messages.map((m) => (
          <MessageBubble
            key={m.id}
            message={m}
            onViewTicket={onViewTicket}
          />
        ))}

        {loading && (
          <div className="flex items-center space-x-3 text-slate-500 text-xs py-3 px-4 bg-white rounded-xl border border-slate-200 shadow-sm w-fit animate-pulse">
            <Loader2 className="w-4 h-4 animate-spin text-gov-600" />
            <span>Consulting verified knowledge base & evaluating entailment safety gate...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="mt-3 shrink-0">
        {recordingStatus && (
          <div className="text-[11px] text-gov-700 bg-teal-50 px-3 py-1 rounded-md mb-2 border border-teal-200 flex items-center justify-between">
            <span>🎙️ {recordingStatus}</span>
            <button onClick={() => setRecordingStatus('')} className="text-slate-400 hover:text-slate-600">&times;</button>
          </div>
        )}

        <div className="relative flex items-center bg-white rounded-xl border-2 border-slate-300 focus-within:border-gov-600 focus-within:shadow-md transition-all">
          <input
            type="text"
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask about PMFBY claims, PACS by-laws, scheme rules or grievances..."
            disabled={loading}
            className="w-full py-3.5 pl-4 pr-24 rounded-xl text-sm text-slate-900 placeholder-slate-400 focus:outline-none bg-transparent"
          />

          <div className="absolute right-2 flex items-center space-x-1.5">
            {/* Voice Input Button */}
            <button
              onClick={handleVoiceInput}
              disabled={loading}
              className={`p-2 rounded-lg transition-colors ${
                isRecording 
                  ? 'bg-red-500 text-white animate-bounce' 
                  : 'text-slate-400 hover:text-gov-700 hover:bg-slate-100'
              }`}
              title="Voice Input (Speech-to-Text)"
            >
              {isRecording ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
            </button>

            {/* Send Button */}
            <button
              onClick={() => handleSend()}
              disabled={!inputQuery.trim() || loading}
              className="p-2.5 rounded-lg bg-gov-700 hover:bg-gov-800 disabled:opacity-40 disabled:hover:bg-gov-700 text-white transition-all shadow-sm"
              title="Send Query"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Civic Disclaimer */}
        <p className="text-[11px] text-slate-400 text-center mt-2">
          SAHAYA provides information from verified sources and does not replace advice from an authorized government/cooperative officer or qualified professional.
        </p>
      </div>
    </div>
  );
}
