import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { getChildProgress, getTherapyPlan } from '../lib/api';
import './ChildDashboard.css';

const DAILY_QUESTS = [
  { word: 'rabbit', target: '/r/', icon: '🐰', points: 5, hint: 'Remember to smile and pull tongue back!' },
  { word: 'sun', target: '/s/', icon: '☀️', points: 5, hint: 'Hiss like a snake through closed teeth fence!' },
  { word: 'star', target: '/s/ + /r/', icon: '⭐', points: 8, hint: 'Start with /s/ and glide into /r/!' },
  { word: 'chair', target: '/ch/', icon: '🪑', points: 5, hint: 'Start with a tap, then sneeze out the sound!' },
  { word: 'fish', target: '/f/', icon: '🐟', points: 5, hint: 'Bite lower lip gently and blow air!' }
];

export default function ChildDashboard() {
  const navigate = useNavigate();
  const { user, setActiveTargetWord } = useApp();

  const [progress, setProgress] = useState(null);
  const [therapyPlan, setTherapyPlan] = useState(null);
  const [loading, setLoading] = useState(true);

  const childId = user?.child_id || 1;

  useEffect(() => {
    async function loadDashboard() {
      try {
        const [progRes, planRes] = await Promise.all([
          getChildProgress(childId).catch(() => null),
          getTherapyPlan(childId).catch(() => null)
        ]);
        setProgress(progRes);
        setTherapyPlan(planRes);
      } finally {
        setLoading(false);
      }
    }
    loadDashboard();
  }, [childId]);

  function startPractice(word) {
    setActiveTargetWord(word);
    navigate('/analyze');
  }

  const stars = progress?.stars || user?.stars || 45;
  const streak = progress?.streak_days || user?.streak_days || 5;

  return (
    <div className="child-dashboard-container">
      {/* Hero Header */}
      <div className="child-hero-card">
        <div className="child-avatar-wrap">
          <span className="big-avatar">🦊</span>
        </div>
        <div className="child-hero-info">
          <h2>Hi, {user?.full_name || 'Leo'}! 👋</h2>
          <p className="hero-subtext">Ready for speech adventures today? Let's unlock new stars!</p>
          <div className="stats-badges">
            <span className="stat-pill star-pill">⭐ {stars} Total Stars</span>
            <span className="stat-pill streak-pill">🔥 {streak} Day Practice Streak</span>
            <span className="stat-pill level-pill">🏆 Level 3 Sound Master</span>
          </div>
        </div>
        <div className="hero-quick-action">
          <button
            type="button"
            className="big-practice-btn"
            onClick={() => startPractice('rabbit')}
          >
            🎙️ Quick Practice (Rabbit)
          </button>
        </div>
      </div>

      <div className="child-grid">
        {/* Left Column: Daily Quests */}
        <div className="dashboard-section-card">
          <div className="section-head">
            <h3>🎯 Today's Sound Missions</h3>
            <span className="section-tag">Daily Practice</span>
          </div>
          <p className="section-desc">Pick a word, record your voice, and earn stars!</p>

          <div className="quests-list">
            {DAILY_QUESTS.map(q => (
              <div key={q.word} className="quest-item">
                <span className="quest-icon">{q.icon}</span>
                <div className="quest-details">
                  <div className="quest-word-row">
                    <strong className="quest-word">{q.word.toUpperCase()}</strong>
                    <span className="quest-target-tag">{q.target}</span>
                  </div>
                  <p className="quest-hint">{q.hint}</p>
                </div>
                <div className="quest-action">
                  <span className="quest-points">+{q.points} ⭐</span>
                  <button
                    type="button"
                    className="quest-start-btn"
                    onClick={() => startPractice(q.word)}
                  >
                    Start 🎙️
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Column: Personalized Therapy Plan & Badges */}
        <div className="right-col-stack">
          {/* Active Therapy Plan Status */}
          <div className="dashboard-section-card plan-widget">
            <div className="section-head">
              <h3>📋 Active Therapy Plan</h3>
              <button
                type="button"
                className="view-plan-link"
                onClick={() => navigate('/therapy-plan')}
              >
                View Full Plan ➔
              </button>
            </div>
            {therapyPlan ? (
              <div className="plan-summary-box">
                <h4>{therapyPlan.title}</h4>
                <p className="plan-desc">{therapyPlan.description}</p>
                <div className="progress-bar-wrap">
                  <div className="progress-bar-labels">
                    <span>Phase {therapyPlan.current_phase} of {therapyPlan.total_phases}</span>
                    <span>{Math.round((therapyPlan.current_phase / therapyPlan.total_phases) * 100)}%</span>
                  </div>
                  <div className="bar-track">
                    <div
                      className="bar-fill"
                      style={{ width: `${(therapyPlan.current_phase / therapyPlan.total_phases) * 100}%` }}
                    />
                  </div>
                </div>
                <button
                  type="button"
                  className="open-drills-btn"
                  onClick={() => navigate('/feedback')}
                >
                  Go to Phase {therapyPlan.current_phase} Drills ➔
                </button>
              </div>
            ) : (
              <p>Loading your customized curriculum...</p>
            )}
          </div>

          {/* Gamified Achievements / Badges */}
          <div className="dashboard-section-card">
            <div className="section-head">
              <h3>🏅 Trophy Room & Badges</h3>
            </div>
            <div className="badges-grid">
              <div className="badge-card unlocked">
                <span className="badge-emoji">🌟</span>
                <span className="badge-name">First Word</span>
                <span className="badge-status">Unlocked</span>
              </div>
              <div className="badge-card unlocked">
                <span className="badge-emoji">🦁</span>
                <span className="badge-name">R-Sound Hero</span>
                <span className="badge-status">Unlocked</span>
              </div>
              <div className="badge-card unlocked">
                <span className="badge-emoji">🔥</span>
                <span className="badge-name">5-Day Streak</span>
                <span className="badge-status">Unlocked</span>
              </div>
              <div className="badge-card locked">
                <span className="badge-emoji">👑</span>
                <span className="badge-name">Master Speaker</span>
                <span className="badge-status">100 Stars Req.</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
