import { create } from 'zustand';
import type { Artifact, ChatMessage, ChatSession, ProviderConfig } from '../types/chat';
import * as api from '../services/api';

interface AppState {
  sessions: ChatSession[];
  activeSessionId: string | null;
  messages: ChatMessage[];
  activeArtifact: Artifact | null;
  providerConfig: ProviderConfig | null;
  isLoading: boolean;
  isStreaming: boolean;

  loadSessions: () => Promise<void>;
  selectSession: (id: string) => Promise<void>;
  createNewSession: () => Promise<string>;
  removeSession: (id: string) => Promise<void>;
  loadProviderConfig: () => Promise<void>;
  changeProvider: (provider: string) => Promise<void>;
  addMessage: (msg: ChatMessage) => void;
  updateLastMessageContent: (delta: string) => void;
  setLastMessageCitations: (citations: any[]) => void;
  setStreaming: (streaming: boolean) => void;
  setArtifact: (artifact: Artifact | null) => void;
}

export const useAppStore = create<AppState>((set) => ({
  sessions: [],
  activeSessionId: null,
  messages: [],
  activeArtifact: null,
  providerConfig: null,
  isLoading: false,
  isStreaming: false,

  loadSessions: async () => {
    try {
      const sessions = await api.fetchSessions();
      set({ sessions });
    } catch (e) {
      console.error('Failed to load sessions', e);
    }
  },

  selectSession: async (id: string) => {
    set({ activeSessionId: id, isLoading: true });
    try {
      const detail = await api.fetchSessionDetail(id);
      set({ messages: detail.messages, isLoading: false });
    } catch (e) {
      console.error('Failed to load session detail', e);
      set({ isLoading: false });
    }
  },

  createNewSession: async () => {
    const session = await api.createSession();
    set((state) => ({
      sessions: [session, ...state.sessions],
      activeSessionId: session.id,
      messages: [],
    }));
    return session.id;
  },

  removeSession: async (id: string) => {
    await api.deleteSession(id);
    set((state) => {
      const remaining = state.sessions.filter((s) => s.id !== id);
      const activeId = state.activeSessionId === id ? (remaining[0]?.id || null) : state.activeSessionId;
      return { sessions: remaining, activeSessionId: activeId };
    });
  },

  loadProviderConfig: async () => {
    try {
      const config = await api.fetchProviderConfig();
      set({ providerConfig: config });
    } catch (e) {
      console.error('Failed to load provider config', e);
    }
  },

  changeProvider: async (provider: string) => {
    const updated = await api.switchProvider(provider);
    set((state) => ({
      providerConfig: state.providerConfig
        ? { ...state.providerConfig, active_provider: updated.active_provider, active_model: updated.active_model }
        : null,
    }));
  },

  addMessage: (msg) => set((state) => ({ messages: [...state.messages, msg] })),

  updateLastMessageContent: (delta) =>
    set((state) => {
      const msgs = [...state.messages];
      if (msgs.length === 0) return state;
      const last = { ...msgs[msgs.length - 1] };
      last.content += delta;
      msgs[msgs.length - 1] = last;
      return { messages: msgs };
    }),

  setLastMessageCitations: (citations) =>
    set((state) => {
      const msgs = [...state.messages];
      if (msgs.length === 0) return state;
      const last = { ...msgs[msgs.length - 1] };
      last.source_citations = citations;
      msgs[msgs.length - 1] = last;
      return { messages: msgs };
    }),

  setStreaming: (streaming) => set({ isStreaming: streaming }),
  setArtifact: (artifact) => set({ activeArtifact: artifact }),
}));
