import React, { useState } from 'react';
import type { SourceCitation } from '../../types/chat';

export const SourceCitationCard: React.FC<{ citations: SourceCitation[] }> = ({ citations }) => {
  const [isOpen, setIsOpen] = useState(false);

  if (!citations || citations.length === 0) return null;

  return (
    <div className="citations-wrapper">
      <button
        className={`citations-toggle-btn ${isOpen ? 'expanded' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
      >
        <span className="toggle-icon">📚</span>
        <span className="toggle-label">Grounded Podcast Sources</span>
        <span className="citations-count-badge">{citations.length} Sources</span>
        <span className="chevron-icon">{isOpen ? '▲' : '▼'}</span>
      </button>

      {isOpen && (
        <div className="citations-grid">
          {citations.map((c, i) => (
            <div key={i} className="citation-card-premium">
              <div className="citation-card-header">
                <span className="guest-badge">🎙️ {c.speaker || 'Podcast Guest'}</span>
                {c.similarity_score > 0 && (
                  <span className="score-badge">
                    {Math.round(c.similarity_score * 100)}% match
                  </span>
                )}
              </div>
              <div className="episode-title">
                {c.episode_title?.replace('.md', '').replace(/-/g, ' ') || c.source_file}
              </div>
              <div className="citation-quote">"{c.excerpt}"</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
