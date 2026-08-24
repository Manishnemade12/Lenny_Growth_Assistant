import React, { useEffect, useRef } from 'react';
import { useAppStore } from '../../stores/appStore';
import { sendChatMessageStream } from '../../services/sse';
import { InputBar } from './InputBar';
import { MessageBubble } from './MessageBubble';
import './chat.css';

export const ChatWindow: React.FC = () => {
  const {
    activeSessionId,
    messages,
    isStreaming,
    addMessage,
    updateLastMessageContent,
    setLastMessageCitations,
    setStreaming,
    createNewSession,
  } = useAppStore();

  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (text: string) => {
    let sessionId = activeSessionId;
    if (!sessionId) {
      sessionId = await createNewSession();
    }

    const userMsg = {
      id: Date.now().toString(),
      role: 'user' as const,
      content: text,
      created_at: new Date().toISOString(),
    };
    addMessage(userMsg);

    const assistantMsg = {
      id: (Date.now() + 1).toString(),
      role: 'assistant' as const,
      content: '',
      created_at: new Date().toISOString(),
    };
    addMessage(assistantMsg);
    setStreaming(true);

    await sendChatMessageStream(sessionId, text, {
      onDelta: (delta) => updateLastMessageContent(delta),
      onCitations: (citations) => setLastMessageCitations(citations),
      onEnd: () => setStreaming(false),
      onError: (err) => {
        updateLastMessageContent(`\n[Error: ${err}]`);
        setStreaming(false);
      },
    });
  };

  return (
    <div className="chat-window">
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="welcome-screen">
            <h2>Welcome to Lenny Growth Assistant</h2>
            <p>Ask product management questions or request a Ship 30 for 30 essay grounded in Lenny's transcripts.</p>
          </div>
        ) : (
          messages.map((m, idx) => <MessageBubble key={m.id || idx} message={m} />)
        )}
        <div ref={scrollRef} />
      </div>

      <InputBar onSend={handleSend} disabled={isStreaming} />
    </div>
  );
};
