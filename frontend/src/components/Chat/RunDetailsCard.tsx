import React, { useState } from 'react';
import type { ChatMessage } from '../../types/chat';

export const RunDetailsCard: React.FC<{ message: ChatMessage }> = ({ message }) => {
  const [isOpen, setIsOpen] = useState(false);

  const wordCount = message.content ? message.content.trim().split(/\s+/).length : 0;
  const citationsCount = message.source_citations ? message.source_citations.length : 0;

  // Determine skill name based on content structure
  let skillName = 'QASkill (Grounded RAG)';
  if (message.content.includes('# ') || message.content.includes('## ') || message.content.length > 800) {
    skillName = 'Ship30Skill (Atomic Essay)';
  }
  if (message.content.includes('<html') || message.content.includes('```html')) {
    skillName = 'ArtifactSkill (Interactive Canvas)';
  }

  return (
    <div className="run-details-wrapper">
      <button
        className={`run-details-toggle ${isOpen ? 'expanded' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
      >
        <span className="details-icon">⚡</span>
        <span className="details-label">Run Details & Assistant Activity</span>
        <span className="details-chevron">{isOpen ? '▲' : '▼'}</span>
      </button>

      {isOpen && (
        <div className="run-details-panel">
          <div className="detail-row">
            <span className="detail-key">🤖 Provider & Model:</span>
            <span className="detail-val">{message.model_used || 'ollama/llama3.2'}</span>
          </div>
          <div className="detail-row">
            <span className="detail-key">🧠 Routed Skill:</span>
            <span className="detail-val">{skillName}</span>
          </div>
          <div className="detail-row">
            <span className="detail-key">🔍 RAG Retrieval:</span>
            <span className="detail-val">{citationsCount} transcript chunks retrieved</span>
          </div>
          <div className="detail-row">
            <span className="detail-key">📊 Token Output:</span>
            <span className="detail-val">~{wordCount} words ({Math.round(wordCount * 1.3)} tokens)</span>
          </div>
          <div className="detail-row">
            <span className="detail-key">🕒 Timestamp:</span>
            <span className="detail-val">{new Date(message.created_at).toLocaleTimeString()}</span>
          </div>
        </div>
      )}
    </div>
  );
};
