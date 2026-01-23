/**
 * TypeScript interfaces for AI completion features.
 */

export interface CompletionRequest {
  prompt: string;
  context: CompletionContext;
  max_tokens?: number;
  temperature?: number;
  system_prompt?: string;
  provider_type: string;
  api_key: string;
  base_url?: string;
  model: string;
}

export interface CompletionContext {
  field_name: string;
  entity_type: string;
  current_text: string;
  entity_data?: Record<string, unknown>;
}

export interface CompletionResponse {
  text: string;
  finish_reason: 'stop' | 'length' | 'error';
  usage?: {
    input_tokens: number;
    output_tokens: number;
  };
  error_message: string;
}

export interface TestConnectionRequest {
  provider_type: string;
  api_key: string;
  base_url?: string;
  model: string;
}

export interface TestConnectionResponse {
  success: boolean;
  message: string;
}

export interface ProviderInfo {
  name: string;
  type: string;
}

export interface ModelInfo {
  id: string;
  name: string;
}

export interface AgentConfig {
  obj_id: {
    prefix: string;
    numeric: number;
  };
  name: string;
  provider_type: string;
  api_key: string;
  base_url: string;
  model: string;
  max_tokens: number;
  temperature: number;
  is_default: boolean;
  is_enabled: boolean;
  system_prompt: string;
}
