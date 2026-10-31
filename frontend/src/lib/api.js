const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export async function request(path, options = {}) {
  const url = `${API_BASE}${path}`;
  try {
    const response = await fetch(url, options);
    if (!response.ok) {
      let errDetail = 'Request failed';
      try {
        const errJson = await response.json();
        errDetail = errJson.detail || errJson.message || errDetail;
      } catch {
        errDetail = await response.text();
      }
      throw new Error(errDetail || `HTTP Error ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`API error at ${path}:`, error);
    throw error;
  }
}

// Auth
export function login(username, password) {
  return request('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
}

export function register(data) {
  return request('/api/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
}

export function getDemoUsers() {
  return request('/api/auth/demo-users');
}

// Speech Analysis
export function analyzeSpeech(audioFile, targetWord, childId = null) {
  const formData = new FormData();
  formData.append('audio', audioFile);
  formData.append('target_word', targetWord);
  if (childId) {
    formData.append('child_id', childId);
  }

  return request('/api/speech/analyze', {
    method: 'POST',
    body: formData
  });
}

// Visual Guidance
export function getVisualPhoneme(phoneme) {
  return request(`/api/visual/phoneme/${encodeURIComponent(phoneme)}`);
}

export function getAllPhonemes() {
  return request('/api/visual/all');
}

// Explainable AI
export function getXaiExplanation(expected, detected, confidence = 0.85) {
  return request('/api/xai/explain', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ expected, detected, confidence })
  });
}

// Therapy Plans
export function getTherapyPlan(childId) {
  return request(`/api/therapy/plan/${childId}`);
}

export function advanceTherapyPhase(planId) {
  return request(`/api/therapy/advance-phase/${planId}`, {
    method: 'POST'
  });
}

// Progress Analytics
export function getChildProgress(childId) {
  return request(`/api/progress/${childId}`);
}

// Therapist Dashboard
export function getTherapistPatients() {
  return request('/api/therapist/patients');
}

export function getTherapistPatientDetail(childId) {
  return request(`/api/therapist/patient/${childId}`);
}

export function saveTherapistNote(data) {
  return request('/api/therapist/notes', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
}

// Chat Assistant
export function sendChatMessage(message) {
  return request('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message })
  });
}
