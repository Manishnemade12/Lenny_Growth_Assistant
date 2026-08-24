import type { SourceCitation } from '../types/chat';

export interface SSECallbacks {
  onDelta: (text: string) => void;
  onCitations: (citations: SourceCitation[]) => void;
  onEnd: () => void;
  onError: (error: string) => void;
}

export async function sendChatMessageStream(
  sessionId: string,
  message: string,
  callbacks: SSECallbacks
) {
  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, message, stream: true }),
    });

    if (!response.ok || !response.body) {
      throw new Error(`HTTP Error: ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const events = buffer.split('\n\n');
      buffer = events.pop() || '';

      for (const eventBlock of events) {
        if (!eventBlock.trim()) continue;
        const lines = eventBlock.split('\n');
        let eventType = '';
        let dataStr = '';

        for (const line of lines) {
          if (line.startsWith('event: ')) eventType = line.slice(7).trim();
          if (line.startsWith('data: ')) dataStr = line.slice(6).trim();
        }

        if (dataStr) {
          try {
            const data = JSON.parse(dataStr);
            if (eventType === 'content_delta') {
              callbacks.onDelta(data.delta);
            } else if (eventType === 'source_citations') {
              callbacks.onCitations(data.citations);
            } else if (eventType === 'message_end') {
              callbacks.onEnd();
            } else if (eventType === 'error') {
              callbacks.onError(data.error);
            }
          } catch (e) {
            console.error('Failed to parse SSE data', e);
          }
        }
      }
    }
    callbacks.onEnd();
  } catch (err: any) {
    callbacks.onError(err.message || 'Stream connection failed');
  }
}
