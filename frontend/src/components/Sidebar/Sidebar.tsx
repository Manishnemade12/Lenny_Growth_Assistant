import React from 'react';
import { useAppStore } from '../../stores/appStore';
import './sidebar.css';

export const Sidebar: React.FC = () => {
  const { sessions, activeSessionId, selectSession, createNewSession, removeSession, providerConfig, changeProvider } =
    useAppStore();

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h2>Lenny Assistant</h2>
        <button className="new-chat-btn" onClick={createNewSession}>
          + New Chat
        </button>
      </div>

      <div className="session-list">
        {sessions.map((s) => (
          <div
            key={s.id}
            className={`session-item ${activeSessionId === s.id ? 'active' : ''}`}
            onClick={() => selectSession(s.id)}
          >
            <span className="session-title">{s.title}</span>
            <button
              className="delete-btn"
              onClick={(e) => {
                e.stopPropagation();
                removeSession(s.id);
              }}
            >
              ×
            </button>
          </div>
        ))}
      </div>

      <div className="sidebar-footer">
        <div className="provider-select">
          <label>Model Provider:</label>
          <select
            value={providerConfig?.active_provider || 'ollama'}
            onChange={(e) => changeProvider(e.target.value)}
          >
            <option value="ollama">Ollama (Local)</option>
            <option value="anthropic">Anthropic Claude</option>
          </select>
        </div>
      </div>
    </aside>
  );
};
