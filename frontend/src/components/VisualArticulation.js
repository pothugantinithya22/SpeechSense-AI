import React, { useState, useEffect } from 'react';
import { getVisualPhoneme } from '../lib/api';
import './VisualArticulation.css';

const DEFAULT_PHONEMES = ['R', 'S', 'TH', 'K', 'L', 'F', 'B', 'M', 'CH', 'SH'];

export default function VisualArticulation({ initialPhoneme = 'R', compact = false }) {
  const [activePhoneme, setActivePhoneme] = useState(initialPhoneme.replace(/[/]/g, '').toUpperCase());
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [viewMode, setViewMode] = useState('sagittal'); // 'sagittal' or 'front'

  useEffect(() => {
    let clean = initialPhoneme.replace(/[/]/g, '').toUpperCase();
    if (clean) setActivePhoneme(clean);
  }, [initialPhoneme]);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        const res = await getVisualPhoneme(activePhoneme);
        setData(res);
      } catch (err) {
        console.error('Failed to load visual data:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [activePhoneme]);

  function speakSound() {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const utt = new SpeechSynthesisUtterance(data?.symbol || activePhoneme);
    utt.rate = 0.8;
    window.speechSynthesis.speak(utt);
  }

  const svg = data?.svg_params || {
    tongue_tip_x: 140,
    tongue_tip_y: 130,
    tongue_body_x: 110,
    tongue_body_y: 145,
    lips_open: 20,
    lip_rounding: 10,
    velum_closed: true,
    vocal_folds_vibrating: true,
    highlight_region: 'oral_cavity'
  };

  return (
    <div className={`visual-articulation-box ${compact ? 'compact' : ''}`}>
      <div className="va-header">
        <div>
          <h3 className="va-title">
            <span className="va-icon">🗣️</span> Visual Articulation & Vocal Tract Guide
          </h3>
          <p className="va-subtitle">
            Target Sound: <strong className="va-target-badge">{data?.symbol || `/${activePhoneme}/`}</strong> — {data?.manner}
          </p>
        </div>

        <div className="va-controls">
          <button
            type="button"
            className={`va-tab-btn ${viewMode === 'sagittal' ? 'active' : ''}`}
            onClick={() => setViewMode('sagittal')}
          >
            Vocal Tract (Side)
          </button>
          <button
            type="button"
            className={`va-tab-btn ${viewMode === 'front' ? 'active' : ''}`}
            onClick={() => setViewMode('front')}
          >
            Lips & Teeth (Front)
          </button>
          <button type="button" className="va-sound-btn" onClick={speakSound} title="Listen to Sound">
            🔊 Play
          </button>
        </div>
      </div>

      {/* Phoneme Quick Selector */}
      {!compact && (
        <div className="va-phoneme-strip">
          <span className="strip-label">Select Phoneme:</span>
          {DEFAULT_PHONEMES.map(ph => (
            <button
              key={ph}
              type="button"
              className={`ph-pill-btn ${activePhoneme === ph ? 'selected' : ''}`}
              onClick={() => setActivePhoneme(ph)}
            >
              /{ph.toLowerCase()}/
            </button>
          ))}
        </div>
      )}

      {/* Main Articulation Diagram Viewport */}
      <div className="va-canvas-container">
        {viewMode === 'sagittal' ? (
          <svg viewBox="0 0 300 240" className="va-svg" aria-label="Sagittal Vocal Tract Diagram">
            <defs>
              <linearGradient id="tongueGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#ff7b89" />
                <stop offset="100%" stopColor="#e63946" />
              </linearGradient>
              <linearGradient id="palateGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#457b9d" />
                <stop offset="100%" stopColor="#1d3557" />
              </linearGradient>
              <filter id="glow">
                <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                <feMerge>
                  <feMergeNode in="coloredBlur"/>
                  <feMergeNode in="SourceGraphic"/>
                </feMerge>
              </filter>
            </defs>

            {/* Head Silhouette Background */}
            <path
              d="M 50,210 C 40,160 40,90 70,50 C 100,20 180,20 220,55 C 240,75 245,100 245,120 L 230,122 C 220,125 210,130 205,140 C 200,150 205,170 215,185 C 220,195 210,215 190,215 L 60,215 Z"
              fill="#f8f9fa"
              stroke="#cbd5e1"
              strokeWidth="2"
            />

            {/* Pharynx & Trachea */}
            <path d="M 90,215 L 90,160 C 90,130 110,95 150,90" fill="none" stroke="#94a3b8" strokeWidth="4" />
            <path d="M 65,215 L 65,160 C 65,110 90,60 140,55" fill="none" stroke="#94a3b8" strokeWidth="3" />

            {/* Hard Palate & Alveolar Ridge */}
            <path
              d="M 120,80 Q 155,75 175,95 L 180,105"
              fill="none"
              stroke="url(#palateGrad)"
              strokeWidth="6"
              strokeLinecap="round"
            />
            <text x="135" y="70" className="svg-label">Palate</text>
            <text x="175" y="90" className="svg-label">Alveolar</text>

            {/* Velum (Soft Palate) - Closed or lowered */}
            {svg.velum_closed ? (
              <path d="M 120,80 Q 105,85 100,100" fill="none" stroke="#e63946" strokeWidth="5" strokeLinecap="round" />
            ) : (
              <path d="M 120,80 Q 110,105 105,125" fill="none" stroke="#3b82f6" strokeWidth="5" strokeLinecap="round" strokeDasharray="3,3" />
            )}
            <text x="95" y="75" className="svg-label">{svg.velum_closed ? 'Velum (Shut)' : 'Velum (Open ⬇)'}</text>

            {/* Upper & Lower Incisors (Teeth) */}
            <rect x="180" y="105" width="8" height="12" rx="2" fill="#ffffff" stroke="#475569" strokeWidth="1.5" />
            <rect x="178" y="132" width="8" height="12" rx="2" fill="#ffffff" stroke="#475569" strokeWidth="1.5" />

            {/* Upper & Lower Lips with variable opening */}
            <path
              d={`M 188,102 Q ${200 + (svg.lip_rounding || 0) * 0.2},105 198,${115 - (svg.lips_open || 15) * 0.2}`}
              fill="none"
              stroke="#ef4444"
              strokeWidth="6"
              strokeLinecap="round"
            />
            <path
              d={`M 186,145 Q ${198 + (svg.lip_rounding || 0) * 0.2},140 196,${130 + (svg.lips_open || 15) * 0.2}`}
              fill="none"
              stroke="#ef4444"
              strokeWidth="6"
              strokeLinecap="round"
            />

            {/* Tongue Body and Tip using dynamic physiological coordinates */}
            <path
              d={`M 80,185 C 85,150 ${svg.tongue_body_x},${svg.tongue_body_y} ${svg.tongue_tip_x},${svg.tongue_tip_y} C ${svg.tongue_tip_x - 10},${svg.tongue_tip_y + 25} 100,195 80,185 Z`}
              fill="url(#tongueGrad)"
              stroke="#b91c1c"
              strokeWidth="2.5"
            />
            <circle cx={svg.tongue_tip_x} cy={svg.tongue_tip_y} r="5" fill="#ffd166" stroke="#d97706" strokeWidth="2" filter="url(#glow)" />
            <text x={svg.tongue_tip_x - 30} y={svg.tongue_tip_y - 8} className="svg-pointer-label">Tongue Tip</text>

            {/* Vocal Cords Vibration */}
            <g transform="translate(80, 195)">
              <line x1="-10" y1="0" x2="10" y2="0" stroke="#f59e0b" strokeWidth="4" />
              {svg.vocal_folds_vibrating && (
                <path d="M -8,-5 Q 0,-10 8,-5 Q 0,0 -8,-5" fill="none" stroke="#e11d48" strokeWidth="2" />
              )}
              <text x="-25" y="15" className="svg-label">{svg.vocal_folds_vibrating ? '⚡ Voiced' : '○ Voiceless'}</text>
            </g>

            {/* Airflow Arrow */}
            <path
              d="M 100,165 Q 140,120 195,122"
              fill="none"
              stroke="#0ea5e9"
              strokeWidth="2.5"
              strokeDasharray="4,4"
              markerEnd="url(#arrow)"
            />
          </svg>
        ) : (
          /* Front Lips and Teeth View */
          <svg viewBox="0 0 260 180" className="va-svg" aria-label="Frontal Mouth Diagram">
            {/* Outer Lips */}
            <ellipse
              cx="130"
              cy="90"
              rx={65 + (svg.lip_rounding ? -15 : 10)}
              ry={35 + (svg.lips_open ? 8 : 0)}
              fill="#f87171"
              stroke="#b91c1c"
              strokeWidth="4"
            />
            {/* Oral Opening */}
            <ellipse
              cx="130"
              cy="90"
              rx={40 + (svg.lip_rounding ? -20 : 5)}
              ry={12 + (svg.lips_open ? 10 : -4)}
              fill="#450a0a"
            />
            {/* Upper Teeth */}
            <rect x="105" y="80" width="12" height="12" rx="2" fill="#fff" stroke="#94a3b8" />
            <rect x="120" y="80" width="12" height="12" rx="2" fill="#fff" stroke="#94a3b8" />
            <rect x="135" y="80" width="12" height="12" rx="2" fill="#fff" stroke="#94a3b8" />
            <rect x="150" y="80" width="12" height="12" rx="2" fill="#fff" stroke="#94a3b8" />

            {/* Tongue Visibility from Front */}
            {svg.tongue_tip_y < 125 && (
              <path
                d="M 115,96 Q 130,88 145,96 Q 130,104 115,96"
                fill="#e63946"
                stroke="#991b1b"
                strokeWidth="1.5"
              />
            )}
          </svg>
        )}
      </div>

      {/* Articulatory Guidance Cards */}
      <div className="va-guidance-grid">
        <div className="va-card child-card">
          <h4>🌟 Child-Friendly Sound Secret</h4>
          <p className="cue-text">{data?.child_cue || 'Practice making this sound slowly and clearly.'}</p>
        </div>

        <div className="va-card clinical-card">
          <h4>🩺 Clinical Articulation Points</h4>
          <ul className="va-details-list">
            <li><strong>Place:</strong> {data?.place}</li>
            <li><strong>Manner:</strong> {data?.manner}</li>
            <li><strong>Voicing:</strong> {data?.voicing}</li>
            <li><strong>Tongue Position:</strong> {data?.tongue_placement}</li>
            <li><strong>Lip Shape:</strong> {data?.lip_shape}</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
