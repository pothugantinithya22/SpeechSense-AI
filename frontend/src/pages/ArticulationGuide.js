import React, { useState } from 'react';
import VisualArticulation from '../components/VisualArticulation';
import './ArticulationGuide.css';

const PHONEME_CATEGORIES = {
  'Liquids & Glides': ['R', 'L', 'W', 'Y'],
  'Sibilants & Fricatives': ['S', 'Z', 'SH', 'ZH', 'TH', 'DH', 'F', 'V', 'HH'],
  'Stops & Plosives': ['P', 'B', 'T', 'D', 'K', 'G'],
  'Affricates': ['CH', 'JH'],
  'Nasals': ['M', 'N', 'NG'],
  'Vowels': ['AA', 'AE', 'AH', 'AO', 'AW', 'AY', 'EH', 'ER', 'EY', 'IH', 'IY', 'OW', 'OY', 'UH', 'UW']
};

export default function ArticulationGuide() {
  const [activePhoneme, setActivePhoneme] = useState('R');

  return (
    <div className="articulation-studio-container">
      <div className="studio-header">
        <h2>🗣️ Visual Articulation & Speech Studio</h2>
        <p className="subtext">
          Interactive sagittal cross-section anatomical visualizer and oral-motor cue library for clinical speech sound remediation.
        </p>
      </div>

      {/* Main Interactive Visualizer */}
      <VisualArticulation initialPhoneme={activePhoneme} />

      {/* Category Explorer */}
      <div className="studio-categories-card">
        <h3>📚 Explore CMU Phoneme Articulation Inventory</h3>
        <p className="category-desc">Click any sound to update the anatomical diagram and review mouth placement cues.</p>

        {Object.entries(PHONEME_CATEGORIES).map(([catName, phones]) => (
          <div key={catName} className="category-row">
            <span className="cat-title">{catName}:</span>
            <div className="cat-pills">
              {phones.map(p => (
                <button
                  key={p}
                  type="button"
                  className={`studio-pill ${activePhoneme === p ? 'active' : ''}`}
                  onClick={() => setActivePhoneme(p)}
                >
                  /{p.toLowerCase()}/
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
