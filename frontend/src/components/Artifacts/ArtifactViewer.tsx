import React from 'react';
import { useAppStore } from '../../stores/appStore';
import { ArtifactSandbox } from './ArtifactSandbox';
import './artifacts.css';

export const ArtifactViewer: React.FC = () => {
  const { activeArtifact, setArtifact } = useAppStore();

  if (!activeArtifact) return null;

  return (
    <aside className="artifact-viewer">
      <div className="artifact-header">
        <h3>{activeArtifact.title}</h3>
        <button className="close-btn" onClick={() => setArtifact(null)}>
          ×
        </button>
      </div>

      <div className="artifact-body">
        {activeArtifact.type === 'html' ? (
          <ArtifactSandbox htmlContent={activeArtifact.content} />
        ) : (
          <pre className="markdown-content">{activeArtifact.content}</pre>
        )}
      </div>
    </aside>
  );
};
