/**
 * API functions for AI endpoints.
 */

import type {
  CompletionRequest,
  CompletionResponse,
  TestConnectionRequest,
  TestConnectionResponse,
  ProviderInfo,
  ModelInfo,
} from './types';

const AI_API_BASE = '/api/ai';

/**
 * Request AI text completion.
 */
export async function requestCompletion(
  request: CompletionRequest,
): Promise<CompletionResponse> {
  const response = await fetch(`${AI_API_BASE}/complete`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => ({ detail: 'Request failed' }));
    return {
      text: '',
      finish_reason: 'error',
      error_message: error.detail || 'Request failed',
    };
  }

  return response.json();
}

/**
 * Test connection to an AI provider.
 */
export async function testConnection(
  request: TestConnectionRequest,
): Promise<TestConnectionResponse> {
  const response = await fetch(`${AI_API_BASE}/test`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => ({ detail: 'Request failed' }));
    return {
      success: false,
      message: error.detail || 'Request failed',
    };
  }

  return response.json();
}

/**
 * List available AI providers.
 */
export async function listProviders(): Promise<ProviderInfo[]> {
  const response = await fetch(`${AI_API_BASE}/providers`);

  if (!response.ok) {
    throw new Error('Failed to fetch providers');
  }

  return response.json();
}

/**
 * List available models for a provider.
 */
export async function listModels(providerType: string): Promise<ModelInfo[]> {
  const response = await fetch(`${AI_API_BASE}/models/${providerType}`);

  if (!response.ok) {
    throw new Error('Failed to fetch models');
  }

  return response.json();
}
