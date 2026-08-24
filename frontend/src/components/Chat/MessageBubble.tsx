import React, { useMemo, useState } from 'react';
import type { ChatMessage } from '../../types/chat';
import { SourceCitationCard } from './SourceCitationCard';
import { useAppStore } from '../../stores/appStore';
import { marked } from 'marked';
import DOMPurify from 'dompurify';

export const MessageBubble: React.FC<{ message: ChatMessage }> = ({ message }) => {
  const isUser = message.role === 'user';
  const { setArtifact } = useAppStore();
  const [copied, setCopied] = useState(false);

  const renderedHtml = useMemo(() => {
    if (isUser || !message.content) return null;
    const rawHtml = marked.parse(message.content) as string;
    return DOMPurify.sanitize(rawHtml);
  }, [message.content, isUser]);

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleCreateArtifact = () => {
    const isHtml = message.content.includes('<div') || message.content.includes('<html');
    setArtifact({
      id: Date.now().toString(),
      type: isHtml ? 'html' : 'markdown',
      title: message.content.slice(0, 30).trim() || 'Conversation Artifact',
      content: message.content,
      created_at: new Date().toISOString(),
    });
  };

  return (
    <div className={`message-row ${isUser ? 'user' : 'assistant'}`}>
      <div className="message-bubble-premium">
        <div className="message-header-premium">
          <div className="avatar-title">
            <span className="role-avatar">{isUser ? '👤' : '🚀'}</span>
            <span className="role-name">{isUser ? 'You' : 'Lenny Assistant'}</span>
          </div>
          {message.model_used && (
            <span className="model-badge-premium">{message.model_used}</span>
          )}
        </div>

        {isUser ? (
          <div className="message-content-user">{message.content}</div>
        ) : message.content ? (
          <div
            className="message-content-assistant markdown-rendered"
            dangerouslySetInnerHTML={{ __html: renderedHtml || '' }}
          />
        ) : (
          <div className="typing-indicator">
            <span className="dot"></span>
            <span className="dot"></span>
            <span className="dot"></span>
          </div>
        )}

        {message.source_citations && message.source_citations.length > 0 && (
          <SourceCitationCard citations={message.source_citations} />
        )}

        {!isUser && message.content && (
          <div className="message-actions-bar">
            <button className="action-pill" onClick={handleCopy}>
              {copied ? '✓ Copied' : '📋 Copy'}
            </button>
            <button className="action-pill" onClick={handleCreateArtifact}>
              📄 View Artifact
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
