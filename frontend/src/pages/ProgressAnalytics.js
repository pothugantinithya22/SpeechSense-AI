import React, { useState, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import { getChildProgress } from '../lib/api';
import './ProgressAnalytics.css';

export default function ProgressAnalytics() {
  const { user } = useApp();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const childId = user?.child_id || 1;

  useEffect(() => {
    async function load() {
      try {
        const res = await getChildProgress(childId);
        setData(res);
      } catch (err) {
        console.error('Progress load error:', err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [childId]);

  if (loading) {
    return <div className="progress-loading">Loading clinical analytics...</div>;
  }

  const sessions = data?.all_sessions || [];
  const mastery = data?.phoneme_mastery || {};
  const errors = data?.error_distribution || { substitution: 0, omission: 0, insertion: 0 };
  const totalErrors = errors.substitution + errors.omission + errors.insertion || 1;

  return (
    <div className="progress-container">
      <div className="progress-header">
        <div>
          <h2>📈 Longitudinal Progress & Analytics</h2>
          <p className="subtext">
            Patient: <strong>{data?.child_name || user?.full_name}</strong> • Age {data?.age} • {data?.diagnosis}
          </p>
        </div>
      </div>

      {/* KPI Overview Cards */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <span className="kpi-icon">🎯</span>
          <div className="kpi-body">
            <span className="kpi-lbl">Overall Accuracy</span>
            <strong className="kpi-val">{data?.average_accuracy}%</strong>
          </div>
        </div>
        <div className="kpi-card">
          <span className="kpi-icon">📉</span>
          <div className="kpi-body">
            <span className="kpi-lbl">Phoneme Error Rate (PER)</span>
            <strong className="kpi-val">{data?.average_per}%</strong>
          </div>
        </div>
        <div className="kpi-card">
          <span className="kpi-icon">🔥</span>
          <div className="kpi-body">
            <span className="kpi-lbl">Practice Streak</span>
            <strong className="kpi-val">{data?.streak_days} Days</strong>
          </div>
        </div>
        <div className="kpi-card">
          <span className="kpi-icon">⭐</span>
          <div className="kpi-body">
            <span className="kpi-lbl">Stars Earned</span>
            <strong className="kpi-val">{data?.stars}</strong>
          </div>
        </div>
      </div>

      {/* Main Analytics Grid */}
      <div className="analytics-grid">
        {/* Longitudinal Accuracy Chart (Visual Bars) */}
        <div className="analytics-card">
          <h3>📈 Session Accuracy Trajectory</h3>
          <p className="card-desc">Chronological progression of pronunciation accuracy</p>
          <div className="chart-bars-wrap">
            {sessions.map((s, idx) => (
              <div key={s.id} className="bar-column">
                <span className="bar-val">{Math.round(s.accuracy)}%</span>
                <div className="bar-outer">
                  <div
                    className={`bar-inner ${s.accuracy >= 80 ? 'green' : s.accuracy >= 65 ? 'amber' : 'red'}`}
                    style={{ height: `${s.accuracy}%` }}
                  />
                </div>
                <span className="bar-lbl">{s.target_word}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Error Types Breakdown */}
        <div className="analytics-card">
          <h3>🧩 Error Type Distribution</h3>
          <p className="card-desc">Classification of detected articulation errors</p>

          <div className="error-distribution-bars">
            <div className="dist-row">
              <div className="dist-meta">
                <span>Substitutions (e.g. /r/ ➔ /w/)</span>
                <strong>{errors.substitution} ({Math.round((errors.substitution / totalErrors) * 100)}%)</strong>
              </div>
              <div className="dist-track">
                <div className="dist-fill sub" style={{ width: `${(errors.substitution / totalErrors) * 100}%` }} />
              </div>
            </div>

            <div className="dist-row">
              <div className="dist-meta">
                <span>Omissions (Deleted sounds)</span>
                <strong>{errors.omission} ({Math.round((errors.omission / totalErrors) * 100)}%)</strong>
              </div>
              <div className="dist-track">
                <div className="dist-fill omi" style={{ width: `${(errors.omission / totalErrors) * 100}%` }} />
              </div>
            </div>

            <div className="dist-row">
              <div className="dist-meta">
                <span>Insertions (Extra sounds)</span>
                <strong>{errors.insertion} ({Math.round((errors.insertion / totalErrors) * 100)}%)</strong>
              </div>
              <div className="dist-track">
                <div className="dist-fill ins" style={{ width: `${(errors.insertion / totalErrors) * 100}%` }} />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Phoneme Mastery Grid */}
      <div className="analytics-card phoneme-mastery-card">
        <h3>🎯 Phoneme Inventory Mastery Levels</h3>
        <p className="card-desc">Mastery percentages across evaluated CMU phonemes</p>

        <div className="phoneme-pills-grid">
          {Object.entries(mastery).map(([ph, score]) => (
            <div key={ph} className="mastery-box">
              <span className="m-phoneme">/{ph}/</span>
              <span className={`m-score ${score >= 80 ? 'high' : score >= 60 ? 'mid' : 'low'}`}>
                {score}%
              </span>
              <div className="m-track">
                <div className="m-fill" style={{ width: `${score}%` }} />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
