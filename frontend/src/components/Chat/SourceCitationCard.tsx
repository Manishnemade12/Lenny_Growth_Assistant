import React from 'react';
import type { SourceCitation } from '../../types/chat';

export const SourceCitationCard: React.FC<{ citations: SourceCitation[] }> = ({ citations }) => {
  if (!citations || citations.length === 0) return null;

  return (
    <div className="citations-container">
      <div className="citations-header">📎 Grounded Sources ({citations.length})</div>
      {citations.map((c, i) => (
        <div key={i} className="citation-card">
          <div className="citation-source">
            {c.episode_title || c.source_file} {c.speaker ? `— ${c.speaker}` : ''}
          </div>
          <div className="citation-excerpt">"{c.excerpt}"</div>
        </div>
      ))}
    </div>
  );
};
