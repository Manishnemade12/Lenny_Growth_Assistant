import React, { useMemo } from 'react';
import DOMPurify from 'dompurify';

interface ArtifactSandboxProps {
  htmlContent: string;
}

export const ArtifactSandbox: React.FC<ArtifactSandboxProps> = ({ htmlContent }) => {
  const sanitizedHtml = useMemo(() => {
    return DOMPurify.sanitize(htmlContent, {
      ALLOWED_TAGS: ['div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'b', 'i', 'strong', 'em', 'style', 'table', 'tr', 'td', 'th', 'thead', 'tbody'],
      ALLOWED_ATTR: ['style', 'class', 'id'],
    });
  }, [htmlContent]);

  return (
    <iframe
      title="Artifact Viewer"
      sandbox="allow-same-origin"
      srcDoc={sanitizedHtml}
      style={{
        width: '100%',
        height: '100%',
        border: 'none',
        backgroundColor: '#ffffff',
      }}
    />
  );
};
