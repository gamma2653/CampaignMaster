/**
 * React context for global AI state management.
 *
 * The enabled state is session-only (React state), matching the GUI's approach
 * where the AICompletionService has a runtime _enabled flag.
 *
 * Agent configurations are fetched from the database via the existing
 * AgentConfig CRUD endpoints.
 */

import {
  createContext,
  useContext,
  useState,
  useCallback,
  type ReactNode,
} from 'react';
import type { AgentConfig } from './types';
import { useAgentConfig } from '../../query';

interface AIContextValue {
  /** Whether AI completions are enabled globally (session-only) */
  enabled: boolean;
  /** Toggle AI completions on/off */
  setEnabled: (enabled: boolean) => void;
  /** The default agent configuration (used for completions) */
  defaultAgent: AgentConfig | null;
  /** All available agent configurations */
  agents: AgentConfig[];
  /** Whether agents are currently loading */
  isLoading: boolean;
  /** Refresh the agent list */
  refreshAgents: () => void;
}

const AIContext = createContext<AIContextValue | null>(null);

interface AIProviderProps {
  children: ReactNode;
}

export function AIProvider({ children }: AIProviderProps) {
  // Session-only enabled state (not persisted, defaults to true)
  // This matches the GUI's AICompletionService._enabled behavior
  const [enabled, setEnabled] = useState(true);

  // Fetch agent configurations from the database
  const { data: agentsData, isLoading, refetch } = useAgentConfig();

  // Type cast since useAgentConfig returns the array
  const agents = (agentsData || []) as AgentConfig[];

  // Find the default agent (same logic as GUI's AICompletionService.load_default_agent)
  // Priority: is_default && is_enabled > first is_enabled > null
  const defaultAgent =
    agents.find((a) => a.is_default && a.is_enabled) ||
    agents.find((a) => a.is_enabled) ||
    null;

  const handleSetEnabled = useCallback((value: boolean) => {
    setEnabled(value);
  }, []);

  const refreshAgents = useCallback(() => {
    refetch();
  }, [refetch]);

  const value: AIContextValue = {
    enabled,
    setEnabled: handleSetEnabled,
    defaultAgent,
    agents,
    isLoading,
    refreshAgents,
  };

  return <AIContext.Provider value={value}>{children}</AIContext.Provider>;
}

export function useAI(): AIContextValue {
  const context = useContext(AIContext);
  if (!context) {
    throw new Error('useAI must be used within an AIProvider');
  }
  return context;
}

/**
 * Hook to check if AI completions are available.
 * Returns true if AI is enabled and a default agent is configured.
 */
export function useAIAvailable(): boolean {
  const { enabled, defaultAgent } = useAI();
  return enabled && defaultAgent !== null;
}
