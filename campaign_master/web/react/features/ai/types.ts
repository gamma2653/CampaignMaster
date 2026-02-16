/**
 * TypeScript interfaces for AI completion features.
 */

import type {
  Arc,
  Point,
  Character,
  Location,
  Item,
  Rule,
  Objective,
} from '../../../schemas';

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

/**
 * Campaign context containing all sub-objects for AI completion.
 * This provides the AI with full campaign context to generate
 * more relevant and consistent completions.
 */
export interface CampaignContext {
  title?: string;
  version?: string;
  setting?: string;
  summary?: string;
  storyline?: Arc[];
  storypoints?: Point[];
  characters?: Character[];
  locations?: Location[];
  items?: Item[];
  rules?: Rule[];
  objectives?: Objective[];
}

export interface EntityContext {
  obj_id: { prefix: string; numeric: number };
  field: string;
  current_value: string;
}

export interface CompletionContext {
  campaign: CampaignContext;
  entity: EntityContext;
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
