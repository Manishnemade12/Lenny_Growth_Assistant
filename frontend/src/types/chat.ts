export interface SourceCitation {
  source_file: string;
  episode_title?: string;
  speaker?: string;
  excerpt: string;
  similarity_score: number;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  source_citations?: SourceCitation[];
  model_used?: string;
  metadata?: Record<string, any>;
  created_at: string;
}

export interface ChatSession {
  id: string;
  title: string;
  message_count: number;
  created_at: string;
  updated_at: string;
}

export interface ProviderInfo {
  name: string;
  status: string;
  models: string[];
}

export interface ProviderConfig {
  active_provider: string;
  active_model: string;
  available_providers: ProviderInfo[];
}

export interface Artifact {
  id: string;
  type: 'markdown' | 'html';
  title: string;
  content: string;
  created_at: string;
}
