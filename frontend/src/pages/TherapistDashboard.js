import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import {
  getTherapistPatients,
  getTherapistPatientDetail,
  saveTherapistNote
} from '../lib/api';
import './TherapistDashboard.css';

export default function TherapistDashboard() {
  const navigate = useNavigate();
  const { setPatientInfo } = useApp();

  const [patients, setPatients] = useState([]);
  const [selectedChildId, setSelectedChildId] = useState(1);
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [noteText, setNoteText] = useState('');
  const [noteSaving, setNoteSaving] = useState(false);
  const [noteSavedMsg, setNoteSavedMsg] = useState('');

  useEffect(() => {
    async function loadPatients() {
      try {
        const pts = await getTherapistPatients();
        setPatients(pts);
        if (pts.length > 0) {
          setSelectedChildId(pts[0].child_id);
        }
      } catch (err) {
        console.error('Error fetching patients:', err);
      } finally {
        setLoading(false);
      }
    }
    loadPatients();
  }, []);

  useEffect(() => {
    if (!selectedChildId) return;
    async function loadDetail() {
      try {
        const res = await getTherapistPatientDetail(selectedChildId);
        setDetail(res);
        setPatientInfo({
          name: res.patient.full_name,
          age: res.patient.age,
          sessionType: 'Comprehensive Clinical Speech Assessment',
          therapist: 'Dr. Sarah Jenkins, CCC-SLP'
        });
      } catch (err) {
        console.error('Error fetching patient detail:', err);
      }
    }
    loadDetail();
  }, [selectedChildId, setPatientInfo]);

  async function handleAddNote(e) {
    e.preventDefault();
    if (!noteText.trim()) return;

    setNoteSaving(true);
    try {
      await saveTherapistNote({
        child_id: selectedChildId,
        note_text: noteText,
        clinical_recommendations: detail?.ai_recommendations?.recommendations?.join('; ') || ''
      });
      setNoteSavedMsg('Note saved to medical chart!');
      setNoteText('');
      // Reload patient detail
      const updated = await getTherapistPatientDetail(selectedChildId);
      setDetail(updated);
      setTimeout(() => setNoteSavedMsg(''), 3000);
    } catch (err) {
      console.error('Error saving note:', err);
    } finally {
      setNoteSaving(false);
    }
  }

  const patient = detail?.patient;
  const aiRec = detail?.ai_recommendations;

  return (
    <div className="therapist-container">
      {/* Header */}
      <div className="therapist-header">
        <div>
          <h2>🩺 Clinical SLP Portal</h2>
          <p className="subtext">Speech-Language Pathologist Patient Management & Diagnostic Analytics</p>
        </div>
        <div className="therapist-header-actions">
          <button
            type="button"
            className="action-btn report-export-btn"
            onClick={() => navigate('/report')}
          >
            📄 View & Export Clinical Report
          </button>
        </div>
      </div>

      {/* Patient Roster Strip */}
      <div className="roster-card">
        <h3>Assigned Patients Roster</h3>
        <div className="patient-cards-grid">
          {patients.map(p => (
            <div
              key={p.child_id}
              className={`patient-roster-pill ${selectedChildId === p.child_id ? 'active' : ''}`}
              onClick={() => setSelectedChildId(p.child_id)}
            >
              <span className="roster-avatar">
                {p.avatar === 'bear' ? '🐻' : '🦊'}
              </span>
              <div className="roster-info">
                <strong>{p.name}</strong>
                <span>Age {p.age} • {p.diagnosis}</span>
              </div>
              <div className="roster-stat">
                <span className="stat-acc">{p.average_accuracy}%</span>
                <span className="stat-lbl">{p.session_count} Sessions</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Main Detail Grid */}
      {detail && patient && (
        <div className="patient-detail-grid">
          {/* Left Column: AI Diagnostics & Sessions */}
          <div className="detail-col-main">
            {/* AI Clinical Recommendations Box */}
            <div className="clinical-card-box ai-recom-box">
              <div className="card-box-header">
                <h3>🤖 AI Clinical Diagnosis & Recommendations</h3>
                <span className="severity-badge">{aiRec?.severity_index || 'Active Monitoring'}</span>
              </div>
              <p className="ai-summary-text">{aiRec?.summary}</p>

              <div className="ai-spec-grid">
                <div className="spec-item">
                  <span className="spec-lbl">Suggested Therapy Frequency:</span>
                  <strong className="spec-val">{aiRec?.suggested_frequency}</strong>
                </div>
                <div className="spec-item">
                  <span className="spec-lbl">Home Practice Target:</span>
                  <strong className="spec-val">{aiRec?.home_practice_target}</strong>
                </div>
              </div>

              <div className="ai-recom-list">
                <h4>Evidence-Based Treatment Recommendations:</h4>
                <ul>
                  {aiRec?.recommendations?.map((r, i) => (
                    <li key={i}>{r}</li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Practice Sessions History Table */}
            <div className="clinical-card-box">
              <div className="card-box-header">
                <h3>📊 Recorded Practice Sessions History</h3>
                <span className="count-tag">{detail.sessions?.length || 0} Sessions Logged</span>
              </div>

              <div className="table-wrapper">
                <table className="clinical-sessions-table">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Target Word</th>
                      <th>Accuracy</th>
                      <th>Phoneme Error Rate (PER)</th>
                      <th>Errors</th>
                    </tr>
                  </thead>
                  <tbody>
                    {detail.sessions?.map(s => (
                      <tr key={s.id}>
                        <td className="date-cell">{s.created_at?.split(' ')[0]}</td>
                        <td><strong>{s.target_word?.toUpperCase()}</strong></td>
                        <td>
                          <span className={`acc-pill ${s.accuracy >= 80 ? 'good' : s.accuracy >= 60 ? 'mid' : 'low'}`}>
                            {s.accuracy}%
                          </span>
                        </td>
                        <td>{s.per}%</td>
                        <td>{s.error_count} phoneme(s)</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* Right Column: Phoneme Deficit Mastery & Clinical Notes */}
          <div className="detail-col-side">
            {/* Phoneme Mastery Analysis */}
            <div className="clinical-card-box">
              <div className="card-box-header">
                <h3>🎯 Phoneme Mastery Breakdown</h3>
              </div>
              <div className="phoneme-bars-stack">
                {Object.entries(detail.phoneme_stats || {}).map(([ph, score]) => (
                  <div key={ph} className="phone-stat-row">
                    <div className="phone-info">
                      <span className="phone-tag">/{ph}/</span>
                      <span className="phone-score">{score}%</span>
                    </div>
                    <div className="stat-track">
                      <div
                        className={`stat-bar ${score >= 80 ? 'bg-green' : score >= 60 ? 'bg-yellow' : 'bg-red'}`}
                        style={{ width: `${score}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Clinical Charting / Therapist Notes */}
            <div className="clinical-card-box notes-box">
              <div className="card-box-header">
                <h3>📝 Clinical Progress Notes</h3>
              </div>

              <form onSubmit={handleAddNote} className="add-note-form">
                <textarea
                  rows="3"
                  placeholder="Enter clinical observations, articulator motor notes, or instructions..."
                  value={noteText}
                  onChange={e => setNoteText(e.target.value)}
                  required
                />
                <button type="submit" className="save-note-btn" disabled={noteSaving}>
                  {noteSaving ? 'Saving...' : 'Save Note to Patient Chart'}
                </button>
              </form>

              {noteSavedMsg && <div className="note-saved-alert">{noteSavedMsg}</div>}

              <div className="notes-history-list">
                <h4>Previous Clinical Entries:</h4>
                {detail.notes?.length === 0 && <p className="no-notes">No notes entered yet.</p>}
                {detail.notes?.map(n => (
                  <div key={n.id} className="note-history-card">
                    <div className="note-meta">
                      <strong>{n.therapist_name}</strong>
                      <span>{n.created_at?.split(' ')[0]}</span>
                    </div>
                    <p className="note-content">{n.note_text}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
