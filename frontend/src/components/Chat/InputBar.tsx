import React, { useState } from 'react';
import './chat.css';

interface InputBarProps {
  onSend: (message: string) => void;
  disabled: boolean;
}

export const InputBar: React.FC<InputBarProps> = ({ onSend, disabled }) => {
  const [text, setText] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (text.trim() && !disabled) {
      onSend(text.trim());
      setText('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form className="input-bar-container" onSubmit={handleSubmit}>
      <div className="input-bar-wrapper">
        <textarea
          className="chat-textarea"
          placeholder="Ask about PMF, growth loops, Ship 30 essay... (Press Enter to send)"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={1}
        />
        <button
          type="submit"
          className="send-button"
          disabled={disabled || !text.trim()}
          title={disabled ? 'Generating response...' : 'Send message'}
        >
          {disabled ? (
            <span className="spinner">⏳</span>
          ) : (
            <span className="send-arrow">➔</span>
          )}
        </button>
      </div>
    </form>
  );
};
