import React, { useRef, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { analyzeSpeech } from '../lib/api';
import { ensureWavFile } from '../lib/audioUtils';
import VisualArticulation from '../components/VisualArticulation';
import XaiFeedbackCard from '../components/XaiFeedbackCard';
import './Analyze.css';

const SUGGESTED_WORDS = [
  { word: 'rabbit', tag: '/r/' },
  { word: 'sun', tag: '/s/' },
  { word: 'chair', tag: '/ch/' },
  { word: 'fish', tag: '/f/' },
  { word: 'dog', tag: '/d/' },
  { word: 'star', tag: '/s/ + /r/' }
];

function formatPhonemeSequence(phones) {
  if (!phones || phones.length === 0) return 'Unavailable';
  return phones.map(phone => `/${phone}/`).join(' ');
}

export default function AnalyzeLive() {
  const navigate = useNavigate();
  const { setAnalysisResult, user, addStars, activeTargetWord, setActiveTargetWord } = useApp();

  const [audioURL, setAudioURL] = useState(null);
  const [audioFile, setAudioFile] = useState(null);
  const [recording, setRecording] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [targetWord, setTargetWord] = useState(activeTargetWord || '');
  const [selectedFocusPhoneme, setSelectedFocusPhoneme] = useState('R');
  const [errorText, setErrorText] = useState('');
  const [status, setStatus] = useState({ text: 'Ready', cls: 'pill-grey' });

  const fileRef = useRef(null);
  const mediaRef = useRef(null);
  const chunksRef = useRef([]);
  const dropRef = useRef(null);

  useEffect(() => {
    if (activeTargetWord) {
      setTargetWord(activeTargetWord);
    }
  }, [activeTargetWord]);

  async function loadFile(file) {
    try {
      const nextFile = file instanceof File ? file : new File([file], 'recording.webm', { type: file.type || 'audio/webm' });
      const wavFile = await ensureWavFile(nextFile);
      setAudioFile(wavFile);
      setAudioURL(URL.createObjectURL(wavFile));
      setStatus({ text: 'Audio Loaded', cls: 'pill-ok' });
      setErrorText('');
    } catch (error) {
      console.error('Audio conversion failed:', error);
      setErrorText('Unable to process this audio file. Please upload a WAV/MP3/OGG file or record again.');
      setStatus({ text: 'Audio conversion failed', cls: 'pill-err' });
    }
  }

  function onFileChange(event) {
    if (event.target.files[0]) {
      loadFile(event.target.files[0]);
    }
  }

  function onDrop(event) {
    event.preventDefault();
    if (dropRef.current) dropRef.current.classList.remove('over');
    if (event.dataTransfer.files[0]) {
      loadFile(event.dataTransfer.files[0]);
    }
  }

  async function toggleRecord() {
    if (!recording) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        chunksRef.current = [];
        mediaRef.current = new MediaRecorder(stream);
        mediaRef.current.ondataavailable = event => {
          if (event.data.size > 0) {
            chunksRef.current.push(event.data);
          }
        };
        mediaRef.current.onstop = async () => {
          const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
          await loadFile(blob);
          stream.getTracks().forEach(track => track.stop());
        };
        mediaRef.current.start();
        setRecording(true);
      } catch {
        alert('Microphone access denied.');
      }
    } else {
      if (mediaRef.current) mediaRef.current.stop();
      setRecording(false);
    }
  }

  async function runAnalysis() {
    if (!audioFile) {
      setStatus({ text: 'Add Audio', cls: 'pill-err' });
      setErrorText('Please upload or record an audio sample before running analysis.');
      return;
    }

    if (!targetWord.trim()) {
      setStatus({ text: 'Target Needed', cls: 'pill-err' });
      setErrorText('Please enter the target word for pronunciation comparison.');
      return;
    }

    setLoading(true);
    setErrorText('');
    setStatus({ text: 'Analysing...', cls: 'pill-warn' });

    try {
      const childId = user?.child_id || 1;
      const data = await analyzeSpeech(audioFile, targetWord.trim(), childId);
      setResult(data);
      setAnalysisResult(data);
      addStars(data.accuracy >= 80 ? 5 : 3);
      setStatus({ text: 'Analysis Complete', cls: 'pill-ok' });

      // If phoneme error exists, set focus sound for visual guidance
      if (data.phoneme_errors && data.phoneme_errors.length > 0) {
        setSelectedFocusPhoneme(data.phoneme_errors[0].expected);
      } else if (data.expected_phonemes && data.expected_phonemes.length > 0) {
        setSelectedFocusPhoneme(data.expected_phonemes[0]);
      }
    } catch (error) {
      setStatus({ text: 'Failed', cls: 'pill-err' });
      setErrorText(error.message || 'Speech analysis request failed.');
    } finally {
      setLoading(false);
    }
  }

  function alignStatusTone(statusValue) {
    if (statusValue === 'correct') return { background: '#ecfdf5', color: '#047857' };
    if (statusValue === 'substitution') return { background: '#fef2f2', color: '#b91c1c' };
    if (statusValue === 'insertion') return { background: '#eff6ff', color: '#1d4ed8' };
    return { background: '#fef3c7', color: '#b45309' };
  }

  return (
    <div className="page-wrapper">
      <div className="page-header">
        <div className="page-label">AI Pronunciation Assessment</div>
        <h1 className="page-title">🎙️ Audio Recording & Speech Analysis</h1>
        <p className="page-desc">
          Evaluate speech audio against HuBERT acoustic features with CTC phoneme alignment and Explainable AI.
        </p>
      </div>

      <div className="two-col">
        {/* Left Card: Input & Recording */}
        <div className="card">
          <div className="card-head">
            <div className="card-title">
              <span>🎤 Input Voice Sample</span>
            </div>
            <span className={`pill ${status.cls}`}>{status.text}</span>
          </div>

          <div className="card-body">
            {/* Quick Word Suggestion Chips */}
            <div className="quick-suggestions-wrap">
              <span className="suggest-lbl">Target Vocabulary:</span>
              <div className="suggest-chips">
                {SUGGESTED_WORDS.map(s => (
                  <button
                    key={s.word}
                    type="button"
                    className={`suggest-chip ${targetWord.toLowerCase() === s.word ? 'selected' : ''}`}
                    onClick={() => {
                      setTargetWord(s.word);
                      setActiveTargetWord(s.word);
                    }}
                  >
                    {s.word} <small>({s.tag})</small>
                  </button>
                ))}
              </div>
            </div>

            <div className="target-word-wrap">
              <label className="form-label">Target Word or Phrase</label>
              <textarea
                className="form-input"
                rows={3}
                style={{ resize: 'vertical' }}
                placeholder="Type ANY word, name, sentence or paragraph - exactly what you will say"
                value={targetWord}
                onChange={event => setTargetWord(event.target.value)}
              />
            </div>

            {/* Audio Drop Zone */}
            <div
              className="drop-zone"
              ref={dropRef}
              onClick={() => fileRef.current?.click()}
              onDragOver={event => {
                event.preventDefault();
                dropRef.current?.classList.add('over');
              }}
              onDragLeave={() => dropRef.current?.classList.remove('over')}
              onDrop={onDrop}
            >
              <input type="file" accept="audio/*" ref={fileRef} onChange={onFileChange} style={{ display: 'none' }} />
              <div className="dz-icon-wrap">
                <span>📁</span>
              </div>
              <h3>Drop speech audio file here</h3>
              <p>or click to select from your device (WAV, MP3, WebM)</p>
              <div className="fmt-chips">
                {['WAV', 'MP3', 'OGG', 'WEBM'].map(format => (
                  <span key={format} className="fmt-chip">{format}</span>
                ))}
              </div>
            </div>

            {/* Microphone Button */}
            <button
              type="button"
              className={`rec-btn ${recording ? 'recording' : ''}`}
              onClick={toggleRecord}
            >
              <span className={`rec-emoji ${recording ? 'active' : ''}`} aria-hidden="true">
                {recording ? '🔴' : '🎙️'}
              </span>
              {recording ? 'Stop Recording Voice' : 'Record Microphone Audio'}
            </button>

            {audioURL && (
              <div className="audio-preview">
                <p className="audio-label">Loaded Audio Sample</p>
                <audio controls src={audioURL} style={{ width: '100%', height: '36px' }} />
              </div>
            )}

            {errorText && <div className="error-box">{errorText}</div>}

            <button type="button" className="run-btn" onClick={runAnalysis} disabled={loading}>
              {loading ? (
                <>
                  <span className="spinner" /> Analyzing Acoustic Features...
                </>
              ) : (
                <>
                  ⚡ Run HuBERT Pronunciation Analysis
                </>
              )}
            </button>
          </div>
        </div>

        {/* Right Column: Assessment Results */}
        <div className="results-col">
          <div className="card">
            <div className="card-head">
              <div className="card-title">
                <span>📊 Acoustic Assessment Results</span>
              </div>
            </div>

            <div className="card-body">
              {result ? (
                <div className="result-summary">
                  <div className="summary-line">
                    <span className="summary-grade">{result.summary?.grade}</span>
                    <span className="pill pill-info">{result.accuracy}% Accuracy</span>
                    <span className="pill pill-warn">{result.per}% PER</span>
                  </div>
                  <p className="summary-copy">{result.summary?.message}</p>

                  {result.warning && (
                    <div style={{background:'#fff4e5',border:'1px solid #f0b429',color:'#7a4b00',padding:'10px 12px',borderRadius:8,margin:'10px 0',fontSize:13}}>
                      ⚠️ {result.warning}
                    </div>
                  )}
                  {result.pipeline && (
                    <div style={{margin:'12px 0',padding:'12px',border:'1px solid #d9e2ec',borderRadius:10,background:'#f8fafc'}}>
                      <strong style={{fontSize:13}}>How this result was produced</strong>
                      <ol style={{margin:'8px 0 0',paddingLeft:18,fontSize:12.5,lineHeight:1.6}}>
                        {result.pipeline.map((st, i) => (
                          <li key={i}><strong>{st.stage}:</strong> {st.detail}</li>
                        ))}
                      </ol>
                      {result.similarity_score !== undefined && (
                        <p style={{margin:'8px 0 0',fontSize:12.5}}>Similarity score: <strong>{result.similarity_score}%</strong></p>
                      )}
                    </div>
                  )}
                  {result.personalized_plan?.weak_sounds?.length > 0 && (
                    <div style={{margin:'12px 0',padding:'12px',border:'1px solid #cfe8d5',borderRadius:10,background:'#f3fbf5',fontSize:12.5}}>
                      <strong>Personalized plan ({result.personalized_plan.difficulty}):</strong> {result.personalized_plan.plan_title}
                      <div style={{marginTop:6}}>Weak sounds: {result.personalized_plan.weak_sounds.map(w => `/${w.phoneme}/ (${w.error_rate}% errors)`).join(', ')}</div>
                    </div>
                  )}
                  {result.transcript && (
                    <p className="summary-copy">Heard: <strong>"{result.transcript}"</strong> (mode: {result.mode})</p>
                  )}

                  {/* Levenshtein Phoneme Alignment Ribbon */}
                  <div className="alignment-ribbon-card">
                    <span className="ribbon-title">Levenshtein Phoneme Alignment:</span>
                    <div className="align-cells-row">
                      {result.alignment?.map((item, idx) => (
                        <div key={idx} className="align-cell" style={alignStatusTone(item.status)}>
                          <span className="cell-expected">{item.expected}</span>
                          <span className="cell-arrow">⬇</span>
                          <span className="cell-detected">{item.detected}</span>
                          <span className="cell-status">{item.status}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Explainable AI Cards */}
                  {result.phoneme_errors && result.phoneme_errors.length > 0 && (
                    <div className="xai-results-block">
                      <h4 className="xai-block-heading">🧠 Explainable AI Diagnostic Findings:</h4>
                      {result.phoneme_errors.map((err, idx) => {
                        const xaiData = result.xai_diagnostics?.[err.expected] || {
                          expected_phoneme: err.phoneme,
                          detected_phoneme: err.produced,
                          error_classification: `${err.type?.toUpperCase()}: ${err.phoneme} -> ${err.produced}`,
                          why_flagged: err.xai_explanation || err.tip,
                          confidence_score: err.confidence || 85,
                          articulatory_contrast: {
                            expected_place: err.tip_title,
                            detected_place: 'Deviated Articulatory Target',
                            key_discrepancy: err.tip,
                            tongue_guidance: err.tip
                          }
                        };
                        return (
                          <XaiFeedbackCard
                            key={idx}
                            xai={xaiData}
                            onSelectPhoneme={(ph) => setSelectedFocusPhoneme(ph)}
                          />
                        );
                      })}
                    </div>
                  )}

                  {/* Action Nav Buttons */}
                  <div className="result-actions-row">
                    <button
                      type="button"
                      className="nav-action-btn feedback-btn"
                      onClick={() => navigate('/feedback')}
                    >
                      Go to Targeted Drills ➔
                    </button>
                    <button
                      type="button"
                      className="nav-action-btn report-btn"
                      onClick={() => navigate('/report')}
                    >
                      Generate Clinical Report ➔
                    </button>
                  </div>
                </div>
              ) : (
                <div className="placeholder-results">
                  <span className="placeholder-icon">🎙️</span>
                  <p>Upload or record your speech on the left, then click <strong>Run HuBERT Pronunciation Analysis</strong>.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Embedded Real-Time Visual Articulation Guide for Target Deficit */}
      <div className="embedded-visual-guide-wrap">
        <VisualArticulation initialPhoneme={selectedFocusPhoneme} compact={false} />
      </div>
    </div>
  );
}
