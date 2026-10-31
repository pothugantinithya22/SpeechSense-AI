import React, { useState } from 'react';
import './XaiFeedbackCard.css';

export default function XaiFeedbackCard({ xai, onSelectPhoneme }) {
  const [expanded, setExpanded] = useState(false);

  if (!xai) return null;

  const contrast = xai.articulatory_contrast || {};

  return (
    <div className="xai-feedback-card">
      <div className="xai-top-row">
        <div className="xai-badge-group">
          <span className="xai-tag">Explainable AI (XAI)</span>
          <span className="xai-contrast-badge">
            {xai.expected_phoneme} → {xai.detected_phoneme}
          </span>
        </div>
        <div className="xai-confidence">
          <span className="conf-label">Acoustic Certainty:</span>
          <span className="conf-value">{xai.confidence_score}%</span>
        </div>
      </div>

      <h4 className="xai-classification">{xai.error_classification}</h4>
      <p className="xai-reasoning">
        <strong>Acoustic Analysis:</strong> {xai.why_flagged}
      </p>

      <div className="xai-contrast-table">
        <div className="contrast-col">
          <span className="col-label">Expected Target ({xai.expected_phoneme})</span>
          <span className="col-val">{contrast.expected_place || 'Standard'}</span>
        </div>
        <div className="contrast-arrow">➔</div>
        <div className="contrast-col">
          <span className="col-label">Acoustically Detected ({xai.detected_phoneme})</span>
          <span className="col-val highlighted">{contrast.detected_place || 'Substituted'}</span>
        </div>
      </div>

      {contrast.key_discrepancy && (
        <div className="xai-discrepancy">
          <strong>Key Physical Discrepancy:</strong> {contrast.key_discrepancy}
        </div>
      )}

      {expanded && (
        <div className="xai-expanded-details">
          {contrast.tongue_guidance && (
            <div className="xai-cue-row">
              <span className="cue-icon">👅</span>
              <div>
                <strong>Tongue Placement Cue:</strong> {contrast.tongue_guidance}
              </div>
            </div>
          )}
          {contrast.lip_guidance && (
            <div className="xai-cue-row">
              <span className="cue-icon">👄</span>
              <div>
                <strong>Lip Posture Cue:</strong> {contrast.lip_guidance}
              </div>
            </div>
          )}
          <div className="xai-clinical-evidence">
            <small>Diagnostic Evidence: {xai.clinical_evidence}</small>
          </div>
        </div>
      )}

      <div className="xai-footer">
        <button
          type="button"
          className="xai-toggle-btn"
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? '▲ Hide Anatomical Cues' : '▼ View Anatomical Motor Cues'}
        </button>

        {onSelectPhoneme && (
          <button
            type="button"
            className="xai-view-model-btn"
            onClick={() => onSelectPhoneme(xai.expected_phoneme.replace(/[/]/g, ''))}
          >
            Show Mouth Model 🔍
          </button>
        )}
      </div>
    </div>
  );
}
