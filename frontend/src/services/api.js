const envBase = import.meta.env.VITE_API_BASE_URL;
let API_BASE = '/api';
if (envBase) {
  const trimmed = envBase.replace(/\/+$/, '');
  API_BASE = trimmed.endsWith('/api') ? trimmed : `${trimmed}/api`;
}

export async function chatQuery(query, language = 'en', userId = 'citizen-demo') {
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, language, user_id: userId })
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Server returned ${res.status}`);
  }
  return res.json();
}

export async function getStats() {
  const res = await fetch(`${API_BASE}/stats`);
  if (!res.ok) throw new Error('Failed to fetch dashboard stats');
  return res.json();
}

export async function getDocuments() {
  const res = await fetch(`${API_BASE}/documents`);
  if (!res.ok) throw new Error('Failed to fetch documents');
  return res.json();
}

export async function triggerIngestion() {
  const res = await fetch(`${API_BASE}/documents/ingest`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to trigger ingestion');
  return res.json();
}

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/documents/upload`, {
    method: 'POST',
    body: formData
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'File upload failed');
  }
  return res.json();
}

export async function getTickets(filters = {}) {
  const params = new URLSearchParams();
  if (filters.status && filters.status !== 'ALL') params.append('status', filters.status);
  if (filters.intent && filters.intent !== 'ALL') params.append('intent', filters.intent);
  if (filters.language && filters.language !== 'ALL') params.append('language', filters.language);
  if (filters.search) params.append('search', filters.search);

  const res = await fetch(`${API_BASE}/tickets?${params.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch tickets');
  return res.json();
}

export async function getTicket(ticketId) {
  const res = await fetch(`${API_BASE}/tickets/${ticketId}`);
  if (!res.ok) throw new Error(`Failed to fetch ticket ${ticketId}`);
  return res.json();
}

export async function updateTicket(ticketId, updateData) {
  const res = await fetch(`${API_BASE}/tickets/${ticketId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(updateData)
  });
  if (!res.ok) throw new Error('Failed to update ticket');
  return res.json();
}

export async function sendVoiceAudio(blob, language = 'en') {
  const formData = new FormData();
  if (blob) {
    formData.append('file', blob, 'audio_query.wav');
  }
  formData.append('language', language);
  const res = await fetch(`${API_BASE}/voice`, {
    method: 'POST',
    body: formData
  });
  if (!res.ok) throw new Error('Voice service failed');
  return res.json();
}

export async function getOfflineFaqs() {
  const res = await fetch(`${API_BASE}/faq`);
  if (!res.ok) throw new Error('Failed to load FAQ cache');
  return res.json();
}
