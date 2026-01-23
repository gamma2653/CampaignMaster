/**
 * TanStack Query hooks for AI features.
 */

import { useQuery, useMutation } from '@tanstack/react-query';
import {
  requestCompletion,
  testConnection,
  listProviders,
  listModels,
} from './api';
import type {
  CompletionRequest,
  CompletionResponse,
  TestConnectionRequest,
  TestConnectionResponse,
} from './types';

/**
 * Hook for AI text completion.
 * Returns a mutation function that can be called to request completion.
 */
export function useCompletion() {
  return useMutation<CompletionResponse, Error, CompletionRequest>({
    mutationFn: requestCompletion,
  });
}

/**
 * Hook for testing AI provider connection.
 */
export function useTestConnection() {
  return useMutation<TestConnectionResponse, Error, TestConnectionRequest>({
    mutationFn: testConnection,
  });
}

/**
 * Hook for fetching available AI providers.
 */
export function useProviders() {
  return useQuery({
    queryKey: ['ai', 'providers'],
    queryFn: listProviders,
    staleTime: 1000 * 60 * 60, // 1 hour - providers don't change often
  });
}

/**
 * Hook for fetching available models for a provider.
 */
export function useModels(providerType: string | undefined) {
  return useQuery({
    queryKey: ['ai', 'models', providerType],
    queryFn: () => listModels(providerType!),
    enabled: !!providerType,
    staleTime: 1000 * 60 * 60, // 1 hour
  });
}
