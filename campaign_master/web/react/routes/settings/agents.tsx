/**
 * Agent Settings Page - Manage AI agent configurations.
 *
 * Two-column layout:
 * - Left: Agent list with add/remove buttons
 * - Right: Configuration form for selected agent
 */

import { useState, useEffect } from 'react';
import { createFileRoute } from '@tanstack/react-router';
import {
  Field,
  Label,
  Input,
  Textarea,
  Select,
  Checkbox,
  Button,
} from '@headlessui/react';
import {
  useAgentConfig,
  useCreateAgentConfig,
  useUpdateAgentConfig,
  useDeleteAgentConfig,
} from '../../query';
import {
  useProviders,
  useModels,
  useTestConnection,
} from '../../features/ai/hooks';
import type { AgentConfig } from '../../features/ai/types';
import { PREFIXES } from '../../schemas';

export const Route = createFileRoute('/settings/agents')({
  component: AgentSettingsPage,
});

function AgentSettingsPage() {
  const { data: agents, isLoading: agentsLoading, refetch } = useAgentConfig();
  const { data: providers } = useProviders();
  const createMutation = useCreateAgentConfig();
  const updateMutation = useUpdateAgentConfig();
  const deleteMutation = useDeleteAgentConfig();
  const testConnectionMutation = useTestConnection();

  const [selectedAgentId, setSelectedAgentId] = useState<number | null>(null);
  const [formData, setFormData] = useState<Partial<AgentConfig> | null>(null);
  const [showApiKey, setShowApiKey] = useState(false);
  const [testStatus, setTestStatus] = useState<{
    success: boolean;
    message: string;
  } | null>(null);

  const agentList = (agents || []) as AgentConfig[];
  const selectedAgent =
    agentList.find((a) => a.obj_id.numeric === selectedAgentId) || null;

  // Get models for selected provider
  const { data: models } = useModels(formData?.provider_type);

  // Update form when selection changes
  useEffect(() => {
    if (selectedAgent) {
      setFormData({ ...selectedAgent });
      setTestStatus(null);
    } else {
      setFormData(null);
    }
  }, [selectedAgent]);

  const handleCreateAgent = () => {
    createMutation.mutate(
      {
        name: 'New Agent',
        provider_type: 'anthropic',
        api_key: '',
        base_url: '',
        model: '',
        max_tokens: 500,
        temperature: 0.7,
        is_default: agentList.length === 0, // First agent is default
        is_enabled: true,
        system_prompt: '',
      },
      {
        onSuccess: (newAgent) => {
          refetch();
          setSelectedAgentId((newAgent as AgentConfig).obj_id.numeric);
        },
      },
    );
  };

  const handleDeleteAgent = () => {
    if (
      selectedAgentId &&
      confirm('Are you sure you want to delete this agent?')
    ) {
      deleteMutation.mutate(
        { prefix: PREFIXES.AGENT_CONFIG, numeric: selectedAgentId },
        {
          onSuccess: () => {
            refetch();
            setSelectedAgentId(null);
          },
        },
      );
    }
  };

  const handleSave = () => {
    if (!formData || !selectedAgent) return;

    updateMutation.mutate(
      {
        obj_id: selectedAgent.obj_id,
        name: formData.name || '',
        provider_type: formData.provider_type || '',
        api_key: formData.api_key || '',
        base_url: formData.base_url || '',
        model: formData.model || '',
        max_tokens: formData.max_tokens || 500,
        temperature: formData.temperature || 0.7,
        is_default: formData.is_default || false,
        is_enabled: formData.is_enabled ?? true,
        system_prompt: formData.system_prompt || '',
      },
      {
        onSuccess: () => {
          refetch();
        },
      },
    );
  };

  const handleTestConnection = () => {
    if (!formData?.provider_type || !formData?.model) {
      setTestStatus({
        success: false,
        message: 'Provider and model are required',
      });
      return;
    }

    setTestStatus(null);
    testConnectionMutation.mutate(
      {
        provider_type: formData.provider_type,
        api_key: formData.api_key || '',
        base_url: formData.base_url || '',
        model: formData.model,
      },
      {
        onSuccess: (result) => {
          setTestStatus(result);
        },
        onError: (error) => {
          setTestStatus({ success: false, message: error.message });
        },
      },
    );
  };

  const updateField = <K extends keyof AgentConfig>(
    field: K,
    value: AgentConfig[K],
  ) => {
    setFormData((prev) => (prev ? { ...prev, [field]: value } : null));
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <h1 className="text-2xl font-bold mb-6">AI Agent Settings</h1>

      <div className="flex gap-6">
        {/* Left Column: Agent List */}
        <div className="w-64 flex-shrink-0">
          <div className="bg-gray-800 rounded-lg p-4">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold">Agents</h2>
              <Button
                onClick={handleCreateAgent}
                disabled={createMutation.isPending}
                className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm"
              >
                + Add
              </Button>
            </div>

            {agentsLoading ? (
              <p className="text-gray-400">Loading...</p>
            ) : agentList.length === 0 ? (
              <p className="text-gray-400 text-sm">No agents configured</p>
            ) : (
              <ul className="space-y-2">
                {agentList.map((agent) => (
                  <li key={agent.obj_id.numeric}>
                    <button
                      onClick={() => setSelectedAgentId(agent.obj_id.numeric)}
                      className={`w-full text-left px-3 py-2 rounded ${
                        selectedAgentId === agent.obj_id.numeric
                          ? 'bg-blue-600'
                          : 'hover:bg-gray-700'
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <span
                          className={`w-2 h-2 rounded-full ${
                            agent.is_enabled ? 'bg-green-500' : 'bg-gray-500'
                          }`}
                        />
                        <span className="truncate">
                          {agent.name || 'Unnamed'}
                        </span>
                        {agent.is_default && (
                          <span className="text-xs bg-yellow-600 px-1 rounded">
                            Default
                          </span>
                        )}
                      </div>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        {/* Right Column: Configuration Form */}
        <div className="flex-1">
          {formData ? (
            <div className="bg-gray-800 rounded-lg p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-semibold">Configure Agent</h2>
                <div className="flex gap-2">
                  <Button
                    onClick={handleSave}
                    disabled={updateMutation.isPending}
                    className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded"
                  >
                    {updateMutation.isPending ? 'Saving...' : 'Save'}
                  </Button>
                  <Button
                    onClick={handleDeleteAgent}
                    disabled={deleteMutation.isPending}
                    className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded"
                  >
                    Delete
                  </Button>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-6">
                {/* Name */}
                <Field>
                  <Label className="block text-sm font-medium mb-1">Name</Label>
                  <Input
                    type="text"
                    value={formData.name || ''}
                    onChange={(e) => updateField('name', e.target.value)}
                    className="w-full px-3 py-2 bg-gray-700 rounded border border-gray-600 focus:border-blue-500"
                  />
                </Field>

                {/* Provider */}
                <Field>
                  <Label className="block text-sm font-medium mb-1">
                    Provider
                  </Label>
                  <Select
                    value={formData.provider_type || ''}
                    onChange={(e) => {
                      updateField('provider_type', e.target.value);
                      updateField('model', ''); // Reset model when provider changes
                    }}
                    className="w-full px-3 py-2 bg-gray-700 rounded border border-gray-600"
                  >
                    <option value="">Select provider...</option>
                    {providers?.map((p) => (
                      <option key={p.type} value={p.type}>
                        {p.name}
                      </option>
                    ))}
                  </Select>
                </Field>

                {/* Model */}
                <Field>
                  <Label className="block text-sm font-medium mb-1">
                    Model
                  </Label>
                  <Input
                    type="text"
                    value={formData.model || ''}
                    onChange={(e) => updateField('model', e.target.value)}
                    list="model-options"
                    className="w-full px-3 py-2 bg-gray-700 rounded border border-gray-600 focus:border-blue-500"
                    placeholder="Enter or select model..."
                  />
                  <datalist id="model-options">
                    {models?.map((m) => (
                      <option key={m.id} value={m.id}>
                        {m.name}
                      </option>
                    ))}
                  </datalist>
                </Field>

                {/* API Key */}
                <Field>
                  <Label className="block text-sm font-medium mb-1">
                    API Key
                    <span className="text-gray-400 text-xs ml-2">
                      (use $ENV_VAR for environment variable)
                    </span>
                  </Label>
                  <div className="flex gap-2">
                    <Input
                      type={showApiKey ? 'text' : 'password'}
                      value={formData.api_key || ''}
                      onChange={(e) => updateField('api_key', e.target.value)}
                      className="flex-1 px-3 py-2 bg-gray-700 rounded border border-gray-600 focus:border-blue-500"
                    />
                    <Button
                      type="button"
                      onClick={() => setShowApiKey(!showApiKey)}
                      className="px-3 py-2 bg-gray-600 hover:bg-gray-500 rounded"
                    >
                      {showApiKey ? 'Hide' : 'Show'}
                    </Button>
                  </div>
                </Field>

                {/* Base URL */}
                <Field>
                  <Label className="block text-sm font-medium mb-1">
                    Base URL (optional)
                  </Label>
                  <Input
                    type="text"
                    value={formData.base_url || ''}
                    onChange={(e) => updateField('base_url', e.target.value)}
                    className="w-full px-3 py-2 bg-gray-700 rounded border border-gray-600 focus:border-blue-500"
                    placeholder="Leave empty for default"
                  />
                </Field>

                {/* Temperature */}
                <Field>
                  <Label className="block text-sm font-medium mb-1">
                    Temperature: {formData.temperature?.toFixed(1) || '0.7'}
                  </Label>
                  <Input
                    type="range"
                    min="0"
                    max="2"
                    step="0.1"
                    value={formData.temperature || 0.7}
                    onChange={(e) =>
                      updateField('temperature', parseFloat(e.target.value))
                    }
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-400">
                    <span>Precise (0)</span>
                    <span>Creative (2)</span>
                  </div>
                </Field>

                {/* Max Tokens */}
                <Field>
                  <Label className="block text-sm font-medium mb-1">
                    Max Tokens: {formData.max_tokens || 500}
                  </Label>
                  <Input
                    type="range"
                    min="50"
                    max="8000"
                    step="50"
                    value={formData.max_tokens || 500}
                    onChange={(e) =>
                      updateField('max_tokens', parseInt(e.target.value))
                    }
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-400">
                    <span>50</span>
                    <span>8000</span>
                  </div>
                </Field>
              </div>

              {/* System Prompt */}
              <Field className="mt-6">
                <Label className="block text-sm font-medium mb-1">
                  System Prompt (optional)
                </Label>
                <Textarea
                  value={formData.system_prompt || ''}
                  onChange={(e) => updateField('system_prompt', e.target.value)}
                  rows={4}
                  className="w-full px-3 py-2 bg-gray-700 rounded border border-gray-600 focus:border-blue-500"
                  placeholder="Custom system prompt for this agent..."
                />
              </Field>

              {/* Checkboxes */}
              <div className="flex gap-6 mt-6">
                <Field className="flex items-center gap-2">
                  <Checkbox
                    checked={formData.is_default || false}
                    onChange={(checked) => updateField('is_default', checked)}
                    className="w-4 h-4"
                  />
                  <Label>Is Default Agent</Label>
                </Field>

                <Field className="flex items-center gap-2">
                  <Checkbox
                    checked={formData.is_enabled ?? true}
                    onChange={(checked) => updateField('is_enabled', checked)}
                    className="w-4 h-4"
                  />
                  <Label>Enabled</Label>
                </Field>
              </div>

              {/* Test Connection */}
              <div className="mt-6 pt-6 border-t border-gray-700">
                <div className="flex items-center gap-4">
                  <Button
                    onClick={handleTestConnection}
                    disabled={testConnectionMutation.isPending}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded"
                  >
                    {testConnectionMutation.isPending
                      ? 'Testing...'
                      : 'Test Connection'}
                  </Button>

                  {testStatus && (
                    <div
                      className={`flex-1 p-3 rounded ${
                        testStatus.success
                          ? 'bg-green-900/50 text-green-300'
                          : 'bg-red-900/50 text-red-300'
                      }`}
                    >
                      {testStatus.message}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-gray-800 rounded-lg p-6 text-center text-gray-400">
              <p>Select an agent from the list or create a new one.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
