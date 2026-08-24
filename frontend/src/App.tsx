import React, { useEffect } from 'react';
import { Sidebar } from './components/Sidebar/Sidebar';
import { ChatWindow } from './components/Chat/ChatWindow';
import { ArtifactViewer } from './components/Artifacts/ArtifactViewer';
import { useAppStore } from './stores/appStore';
import './styles/globals.css';

export const App: React.FC = () => {
  const { loadSessions, loadProviderConfig } = useAppStore();

  useEffect(() => {
    loadSessions();
    loadProviderConfig();
  }, []);

  return (
    <div style={{ display: 'flex', width: '100vw', height: '100vh' }}>
      <Sidebar />
      <ChatWindow />
      <ArtifactViewer />
    </div>
  );
};

export default App;
