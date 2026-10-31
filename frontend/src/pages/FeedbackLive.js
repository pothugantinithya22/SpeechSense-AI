import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import VisualArticulation from '../components/VisualArticulation';
import './Feedback.css';

function say(text) {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.75;
    utterance.lang = 'en-US';
    window.speechSynthesis.speak(utterance);
  }
}

export default function FeedbackLive() {
  const navigate = useNavigate();
  const { analysisResult } = useApp();

  const [activePhonemeFocus, setActivePhonemeFocus] = useState('R');

  if (!analysisResult) {
    return (
      <div className="page-wrapper">
        <div className="page-header">
          <div className="page-label">Step 2</div>
          <h1 className="page-title">🎯 Corrective Feedback & Exercises</h1>
        </div>
        <div className="card" style={{ textAlign: 'center', padding: '56px 24px' }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '14px' }}>🎙️</div>
          <p style={{ fontSize: '1rem', color: 'var(--muted)', marginBottom: '20px' }}>
            Run an analysis first to generate personalized feedback and practice drills.
          </p>
          <button type="button" className="btn-teal" onClick={() => navigate('/analyze')}>
            Go to Analyze Speech
          </button>
        </div>
      </div>
    );
  }

  const errors = analysisResult.phoneme_errors || [];
  const feedbackItems = analysisResult.feedback || [];
  const substitutions = errors.filter(error => error.type === 'substitution').length;
  const omissions = errors.filter(error => error.type === 'omission').length;
  const insertions = errors.filter(error => error.type === 'insertion').length;
  const correctPhonemes = (analysisResult.all_phonemes || []).filter(item => item.err === 'Correct');
  const targetWords = analysisResult.target_word
    ? analysisResult.target_word.trim().split(/\s+/).filter(Boolean)
    : [];

  const practiceItems = feedbackItems.length > 0
    ? feedbackItems.map((item, index) => ({
        n: index + 1,
        title: `${item.phoneme_label} ${item.issue}`,
        desc: item.tip,
        rawPhone: item.phoneme
      }))
    : (analysisResult.recommendations || []).map((item, index) => ({
        n: index + 1,
        title: `Practice step ${index + 1}`,
        desc: item,
        rawPhone: 'R'
      }));

  const errorPhonemes = Array.from(new Set(feedbackItems.map(item => item.phoneme_label)));

  const ttsItems = [
    { word: analysisResult.target_word, ipa: 'Full target' },
    ...targetWords.map((word, index) => ({ word, ipa: `Word ${index + 1}` })),
    { word: `${analysisResult.target_word}. ${analysisResult.target_word}.`, ipa: 'Slow repetition' },
  ];

  const summaryCopy = errors.length === 0
    ? `All expected phonemes in "${analysisResult.target_word}" were matched correctly. No substitutions, omissions, or insertions were detected in this attempt!`
    : `For "${analysisResult.target_word}", the model detected ${substitutions} substitution(s), ${omissions} omission(s), and ${insertions} insertion(s).`;

  const strengthsCopy = correctPhonemes.length > 0
    ? `Stable acoustic matches were detected for ${correctPhonemes.map(item => item.ph).join(', ')}. Keep those articulatory placements consistent while practicing the targeted sound.`
    : 'This attempt benefits from a slower, more deliberate repetition with clear articulatory contact.';

  return (
    <div className="page-wrapper">
      <div className="page-header">
        <div className="page-label">Step 2: Remediation</div>
        <h1 className="page-title">🎯 Corrective Feedback & Motor Drills</h1>
        <p className="page-desc">
          Evidence-based drills and articulatory biofeedback for <strong>{analysisResult.target_word}</strong>.
        </p>
      </div>

      <div className="fb-layout">
        {/* Left Column */}
        <div className="fb-left">
          <div className="fb-block fb-info">
            <div className="fb-head">
              <div className="fb-icon" style={{ background: 'var(--teal)' }}>AI</div>
              <div className="fb-title">Diagnostic Error Summary</div>
            </div>
            <p>{summaryCopy}</p>
          </div>

          <div className="fb-block fb-ok">
            <div className="fb-head">
              <div className="fb-icon" style={{ background: 'var(--green)' }}>OK</div>
              <div className="fb-title">Strengths Observed</div>
            </div>
            <p>{strengthsCopy}</p>
          </div>

          {/* Embedded Visual Articulation Box */}
          <VisualArticulation initialPhoneme={activePhonemeFocus} compact={true} />

          <div className="card">
            <div className="card-head">
              <div className="card-title">Targeted Remediation Drills</div>
            </div>
            <div className="card-body">
              <ul className="ex-list">
                {practiceItems.map(item => (
                  <li key={item.n} className="ex-item" onClick={() => item.rawPhone && setActivePhonemeFocus(item.rawPhone)}>
                    <div className="ex-num">{item.n}</div>
                    <div style={{ flex: 1 }}>
                      <div className="ex-title">{item.title}</div>
                      <div className="ex-desc">{item.desc}</div>
                    </div>
                    <button type="button" className="tts-play" onClick={() => say(item.desc)}>
                      🔊 Listen
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        {/* Right Column */}
        <div className="fb-right">
          <div className="card">
            <div className="card-head">
              <div className="card-title">🔊 Listen and Repeat Audio</div>
            </div>
            <div className="card-body">
              <p className="tts-hint">Tap play to hear model acoustic pronunciation, then rehearse out loud.</p>
              <div className="tts-list">
                {ttsItems.map(({ word, ipa }, index) => (
                  <div key={`${ipa}-${word}-${index}`} className="tts-item">
                    <div>
                      <span className="tts-word">{word}</span>
                      <span className="tts-ipa">{ipa}</span>
                    </div>
                    <button type="button" className="tts-play" onClick={() => say(word)}>
                      Play
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Session Metrics Snapshot */}
          <div className="card acc-snapshot">
            <div className="card-head">
              <div className="card-title">Session Performance Snapshot</div>
            </div>
            <div className="card-body">
              <div className="snap-row">
                <span className="snap-label">Session Accuracy</span>
                <span className="snap-val" style={{ color: 'var(--teal)' }}>
                  {analysisResult.accuracy !== null ? `${analysisResult.accuracy}%` : 'N/A'}
                </span>
              </div>
              <div className="snap-row">
                <span className="snap-label">Phoneme Error Rate</span>
                <span className="snap-val" style={{ color: 'var(--red)' }}>
                  {analysisResult.per !== null ? `${analysisResult.per}%` : 'N/A'}
                </span>
              </div>
              <div className="snap-row">
                <span className="snap-label">Errors Detected</span>
                <span className="snap-val" style={{ color: 'var(--amber)' }}>{errors.length}</span>
              </div>
              <div className="snap-row">
                <span className="snap-label">Substitutions</span>
                <span className="snap-val">{substitutions}</span>
              </div>
              <div className="snap-row">
                <span className="snap-label">Omissions</span>
                <span className="snap-val">{omissions}</span>
              </div>
              <div className="snap-row" style={{ borderBottom: 'none' }}>
                <span className="snap-label">Detected Phonemes</span>
                <span className="snap-val">{(analysisResult.detected_phonemes || []).length}</span>
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <button
              type="button"
              className="btn-teal"
              style={{ width: '100%', justifyContent: 'center', padding: '12px' }}
              onClick={() => navigate('/report')}
            >
              Generate Printable Clinical Report ➔
            </button>
            <button
              type="button"
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '8px',
                border: '1px solid #cbd5e1',
                background: '#ffffff',
                fontWeight: 700,
                color: '#475569',
                cursor: 'pointer'
              }}
              onClick={() => navigate('/child-dashboard')}
            >
              Back to Child Hub
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
