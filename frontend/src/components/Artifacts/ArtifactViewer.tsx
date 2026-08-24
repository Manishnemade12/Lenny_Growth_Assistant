import React, { useState } from 'react';
import { useAppStore } from '../../stores/appStore';
import { ArtifactSandbox } from './ArtifactSandbox';
import { ArtifactToolbar } from './ArtifactToolbar';
import './artifacts.css';

export const ArtifactViewer: React.FC = () => {
  const { activeArtifact, setArtifact } = useAppStore();
  const [isRawView, setIsRawView] = useState(false);

  if (!activeArtifact) return null;

  return (
    <aside className="artifact-viewer">
      <div className="artifact-header">
        <div className="artifact-title-wrapper">
          <span className="artifact-type-badge">{activeArtifact.type.toUpperCase()}</span>
          <h3>{activeArtifact.title}</h3>
        </div>
        <ArtifactToolbar
          artifact={activeArtifact}
          isRawView={isRawView}
          onToggleRawView={() => setIsRawView(!isRawView)}
          onClose={() => setArtifact(null)}
        />
      </div>

      <div className="artifact-body">
        {isRawView ? (
          <pre className="markdown-content">{activeArtifact.content}</pre>
        ) : activeArtifact.type === 'html' ? (
          <ArtifactSandbox htmlContent={activeArtifact.content} />
        ) : (
          <pre className="markdown-content">{activeArtifact.content}</pre>
        )}
      </div>
    </aside>
  );
};
