import React, { useState } from 'react';
import { useAppStore } from '../../stores/appStore';
import './sidebar.css';

export const Sidebar: React.FC = () => {
  const {
    sessions,
    activeSessionId,
    selectSession,
    createNewSession,
    removeSession,
    providerConfig,
    changeProvider,
  } = useAppStore();

  const [searchQuery, setSearchQuery] = useState('');
  const [isDarkMode, setIsDarkMode] = useState(false);

  const toggleTheme = () => {
    const nextTheme = !isDarkMode;
    setIsDarkMode(nextTheme);
    document.documentElement.setAttribute('data-theme', nextTheme ? 'dark' : 'light');
  };

  const filteredSessions = sessions.filter((s) =>
    s.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const activeProvider = providerConfig?.active_provider || 'ollama';

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="header-top">
          <h2>🚀 Lenny Assistant</h2>
          <button
            className="theme-toggle-btn"
            onClick={toggleTheme}
            title={isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          >
            {isDarkMode ? '☀️' : '🌙'}
          </button>
        </div>
        <button className="new-chat-btn" onClick={createNewSession}>
          + New Chat
        </button>
        <input
          type="text"
          className="search-input"
          placeholder="Filter conversations..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      <div className="session-list">
        {filteredSessions.length === 0 ? (
          <div className="empty-sessions">No conversations found</div>
        ) : (
          filteredSessions.map((s) => (
            <div
              key={s.id}
              className={`session-item ${activeSessionId === s.id ? 'active' : ''}`}
              onClick={() => selectSession(s.id)}
            >
              <span className="session-title">{s.title}</span>
              <button
                className="delete-btn"
                title="Delete chat"
                onClick={(e) => {
                  e.stopPropagation();
                  removeSession(s.id);
                }}
              >
                ×
              </button>
            </div>
          ))
        )}
      </div>

      <div className="sidebar-footer">
        <div className="provider-select">
          <div className="provider-label">
            <span>LLM Provider</span>
            <span className="status-indicator online" title="Connected">
              🟢 {activeProvider}
            </span>
          </div>
          <select
            value={activeProvider}
            onChange={(e) => changeProvider(e.target.value)}
          >
            <option value="ollama">Ollama (Local Default)</option>
            <option value="anthropic">Anthropic Claude 3.5</option>
            <option value="openai">OpenAI GPT-4o</option>
          </select>
        </div>
      </div>
    </aside>
  );
};
