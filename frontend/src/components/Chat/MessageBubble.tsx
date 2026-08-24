import React from 'react';
import type { ChatMessage } from '../../types/chat';
import { SourceCitationCard } from './SourceCitationCard';

export const MessageBubble: React.FC<{ message: ChatMessage }> = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div className={`message-row ${isUser ? 'user' : 'assistant'}`}>
      <div className="message-bubble">
        <div className="message-header">{isUser ? 'You' : 'Lenny Assistant'}</div>
        <div className="message-content">{message.content}</div>
        {message.source_citations && <SourceCitationCard citations={message.source_citations} />}
      </div>
    </div>
  );
};
