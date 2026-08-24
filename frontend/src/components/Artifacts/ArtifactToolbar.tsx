import React, { useState } from 'react';
import type { Artifact } from '../../types/chat';

interface ArtifactToolbarProps {
  artifact: Artifact;
  isRawView: boolean;
  onToggleRawView: () => void;
  onClose: () => void;
}

export const ArtifactToolbar: React.FC<ArtifactToolbarProps> = ({
  artifact,
  isRawView,
  onToggleRawView,
  onClose,
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(artifact.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const extension = artifact.type === 'html' ? 'html' : 'md';
    const blob = new Blob([artifact.content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${artifact.title.toLowerCase().replace(/\s+/g, '_')}.${extension}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="artifact-toolbar">
      <button className="toolbar-btn" onClick={onToggleRawView}>
        {isRawView ? '👁️ Rendered' : '📝 Raw Source'}
      </button>
      <button className="toolbar-btn" onClick={handleCopy}>
        {copied ? '✓ Copied' : '📋 Copy'}
      </button>
      <button className="toolbar-btn" onClick={handleDownload}>
        💾 Download
      </button>
      <button className="toolbar-btn close" onClick={onClose}>
        ×
      </button>
    </div>
  );
};
