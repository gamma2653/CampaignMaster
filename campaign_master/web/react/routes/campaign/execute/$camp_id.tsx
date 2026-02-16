import { createFileRoute, useNavigate } from '@tanstack/react-router';
import { useState, useEffect } from 'react';
import {
  useCampaignExecutionByID,
  useUpdateCampaignExecution,
  useDeleteCampaignExecution,
  useCampaignPlan,
  useRefineNotes,
  useExtractEntityNotes,
  useAgentConfig,
} from '../../../query';
import { PREFIXES, PREFIX_TO_NAME } from '../../../schemas';
import type {
  CampaignExecution,
  ExecutionEntry,
  CampaignPlan,
  AgentConfig,
  AnyID,
} from '../../../schemas';

export const Route = createFileRoute('/campaign/execute/$camp_id')({
  component: RouteComponent,
});

const STATUS_OPTIONS = [
  { value: 'not_encountered', label: 'Not Encountered' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'completed', label: 'Completed' },
  { value: 'skipped', label: 'Skipped' },
];

function RouteComponent() {
  const { camp_id } = Route.useParams();
  const navigate = useNavigate();
  const numericId = parseInt(camp_id, 10);

  const {
    data: execution,
    isLoading,
    error,
  } = useCampaignExecutionByID({
    prefix: PREFIXES.EXECUTION,
    numeric: numericId,
  });
  const { data: plans } = useCampaignPlan();
  const { data: agentConfigs } = useAgentConfig();
  const updateMutation = useUpdateCampaignExecution();
  const deleteMutation = useDeleteCampaignExecution();
  const refineNotesMutation = useRefineNotes();
  const extractEntityMutation = useExtractEntityNotes();

  const [title, setTitle] = useState('');
  const [sessionDate, setSessionDate] = useState('');
  const [campaignPlanId, setCampaignPlanId] = useState<AnyID>({
    prefix: PREFIXES.CAMPAIGN_PLAN,
    numeric: 0,
  });
  const [rawSessionNotes, setRawSessionNotes] = useState('');
  const [refinedSessionNotes, setRefinedSessionNotes] = useState('');
  const [refinementMode, setRefinementMode] = useState<
    'narrative' | 'structured'
  >('narrative');
  const [entries, setEntries] = useState<ExecutionEntry[]>([]);

  const ex = execution as CampaignExecution | undefined;

  useEffect(() => {
    if (ex) {
      setTitle(ex.title);
      setSessionDate(ex.session_date);
      setCampaignPlanId(ex.campaign_plan_id);
      setRawSessionNotes(ex.raw_session_notes);
      setRefinedSessionNotes(ex.refined_session_notes);
      setRefinementMode(ex.refinement_mode);
      setEntries(ex.entries);
    }
  }, [ex]);

  const getDefaultAgent = (): AgentConfig | undefined => {
    const configs = (agentConfigs ?? []) as AgentConfig[];
    return configs.find((c) => c.is_default && c.is_enabled) ?? configs[0];
  };

  const handleSave = () => {
    if (!ex) return;
    updateMutation.mutate({
      obj_id: ex.obj_id,
      campaign_plan_id: campaignPlanId,
      title,
      session_date: sessionDate,
      raw_session_notes: rawSessionNotes,
      refined_session_notes: refinedSessionNotes,
      refinement_mode: refinementMode,
      entries,
    });
  };

  const handleDelete = () => {
    if (!ex) return;
    if (confirm('Delete this execution?')) {
      deleteMutation.mutate(ex.obj_id, {
        onSuccess: () => navigate({ to: '/campaign/execute' }),
      });
    }
  };

  const handleRefineNotes = () => {
    const agent = getDefaultAgent();
    if (!agent) {
      alert('No AI agent configured. Configure one in Agent settings.');
      return;
    }
    refineNotesMutation.mutate(
      {
        raw_notes: rawSessionNotes,
        mode: refinementMode,
        provider_type: agent.provider_type,
        api_key: agent.api_key,
        model: agent.model,
        base_url: agent.base_url,
      },
      {
        onSuccess: (data) => {
          if (data.error_message) {
            alert(`Refinement error: ${data.error_message}`);
          } else {
            setRefinedSessionNotes(data.refined_text);
          }
        },
      },
    );
  };

  const handlePopulateFromPlan = () => {
    const plansList = (plans ?? []) as CampaignPlan[];
    const selectedPlan = plansList.find(
      (p) =>
        p.obj_id.prefix === campaignPlanId.prefix &&
        p.obj_id.numeric === campaignPlanId.numeric,
    );
    if (!selectedPlan) {
      alert('Select a campaign plan first.');
      return;
    }

    const newEntries: ExecutionEntry[] = [];
    const addEntries = (items: { obj_id: AnyID }[], typeName: string) => {
      for (const item of items) {
        const exists = entries.some(
          (e) =>
            e.entity_id.prefix === item.obj_id.prefix &&
            e.entity_id.numeric === item.obj_id.numeric,
        );
        if (!exists) {
          newEntries.push({
            entity_id: item.obj_id,
            entity_type: typeName,
            status: 'not_encountered',
            raw_notes: '',
            refined_notes: '',
          });
        }
      }
    };

    addEntries(selectedPlan.characters, 'Character');
    addEntries(selectedPlan.locations, 'Location');
    addEntries(selectedPlan.items, 'Item');
    addEntries(selectedPlan.storypoints, 'Point');
    addEntries(selectedPlan.objectives, 'Objective');
    addEntries(selectedPlan.rules, 'Rule');

    setEntries([...entries, ...newEntries]);
  };

  const handleAutoExtractNotes = async () => {
    const agent = getDefaultAgent();
    if (!agent) {
      alert('No AI agent configured.');
      return;
    }

    for (let i = 0; i < entries.length; i++) {
      const entry = entries[i];
      const entityName = `${entry.entity_id.prefix}-${entry.entity_id.numeric}`;
      extractEntityMutation.mutate(
        {
          raw_session_notes: rawSessionNotes,
          entity_name: entityName,
          entity_type: entry.entity_type,
          provider_type: agent.provider_type,
          api_key: agent.api_key,
          model: agent.model,
          base_url: agent.base_url,
        },
        {
          onSuccess: (data) => {
            if (!data.error_message && data.extracted_notes) {
              setEntries((prev) => {
                const updated = [...prev];
                updated[i] = {
                  ...updated[i],
                  refined_notes: data.extracted_notes,
                };
                return updated;
              });
            }
          },
        },
      );
    }
  };

  const updateEntry = (
    index: number,
    field: keyof ExecutionEntry,
    value: string,
  ) => {
    setEntries((prev) => {
      const updated = [...prev];
      updated[index] = { ...updated[index], [field]: value };
      return updated;
    });
  };

  const removeEntry = (index: number) => {
    setEntries((prev) => prev.filter((_, i) => i !== index));
  };

  if (isLoading) return <div className="p-8">Loading execution...</div>;
  if (error)
    return <div className="p-8 text-red-400">Error: {error.message}</div>;
  if (!ex) return <div className="p-8">Execution not found.</div>;

  const plansList = (plans ?? []) as CampaignPlan[];

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">
          Execution: {ex.obj_id.prefix}-{ex.obj_id.numeric}
        </h1>
        <div className="space-x-2">
          <button
            type="button"
            onClick={handleSave}
            disabled={updateMutation.isPending}
            className="bg-blue-700 hover:bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
          >
            {updateMutation.isPending ? 'Saving...' : 'Save'}
          </button>
          <button
            type="button"
            onClick={handleDelete}
            className="bg-red-700 hover:bg-red-600 text-white px-4 py-2 rounded"
          >
            Delete
          </button>
        </div>
      </div>

      {updateMutation.isSuccess && (
        <div className="text-green-400 text-sm">Saved successfully.</div>
      )}

      {/* Basic fields */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm text-gray-400 mb-1">Title</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full bg-gray-800 border border-gray-600 rounded px-3 py-2"
          />
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-1">
            Session Date
          </label>
          <input
            type="date"
            value={sessionDate}
            onChange={(e) => setSessionDate(e.target.value)}
            className="w-full bg-gray-800 border border-gray-600 rounded px-3 py-2"
          />
        </div>
      </div>

      {/* Campaign Plan selector */}
      <div>
        <label className="block text-sm text-gray-400 mb-1">
          Linked Campaign Plan
        </label>
        <select
          value={`${campaignPlanId.prefix}-${campaignPlanId.numeric}`}
          onChange={(e) => {
            const [prefix, numStr] = e.target.value.split('-');
            setCampaignPlanId({ prefix, numeric: parseInt(numStr, 10) });
          }}
          className="w-full bg-gray-800 border border-gray-600 rounded px-3 py-2"
        >
          <option value={`${PREFIXES.CAMPAIGN_PLAN}-0`}>-- None --</option>
          {plansList.map((p) => (
            <option
              key={`${p.obj_id.prefix}-${p.obj_id.numeric}`}
              value={`${p.obj_id.prefix}-${p.obj_id.numeric}`}
            >
              {p.title || 'Untitled'} ({p.obj_id.prefix}-{p.obj_id.numeric})
            </option>
          ))}
        </select>
      </div>

      {/* Session Notes Panel */}
      <div className="border border-gray-600 rounded p-4 space-y-3">
        <h2 className="text-lg font-semibold">Session Notes</h2>
        <div>
          <label className="block text-sm text-gray-400 mb-1">Raw Notes</label>
          <textarea
            value={rawSessionNotes}
            onChange={(e) => setRawSessionNotes(e.target.value)}
            rows={8}
            className="w-full bg-gray-800 border border-gray-600 rounded px-3 py-2 font-mono text-sm"
          />
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <label className="text-sm text-gray-400">Mode:</label>
            <select
              value={refinementMode}
              onChange={(e) =>
                setRefinementMode(e.target.value as 'narrative' | 'structured')
              }
              className="bg-gray-800 border border-gray-600 rounded px-2 py-1 text-sm"
            >
              <option value="narrative">Narrative</option>
              <option value="structured">Structured</option>
            </select>
          </div>
          <button
            type="button"
            onClick={handleRefineNotes}
            disabled={refineNotesMutation.isPending || !rawSessionNotes}
            className="bg-purple-700 hover:bg-purple-600 text-white px-3 py-1 rounded text-sm disabled:opacity-50"
          >
            {refineNotesMutation.isPending ? 'Refining...' : 'Refine with AI'}
          </button>
        </div>
        {refinedSessionNotes && (
          <div>
            <label className="block text-sm text-gray-400 mb-1">
              Refined Notes
            </label>
            <div className="bg-gray-900 border border-gray-600 rounded px-3 py-2 whitespace-pre-wrap text-sm">
              {refinedSessionNotes}
            </div>
          </div>
        )}
      </div>

      {/* Entity Status Grid */}
      <div className="border border-gray-600 rounded p-4 space-y-3">
        <div className="flex justify-between items-center">
          <h2 className="text-lg font-semibold">Entity Tracking</h2>
          <div className="space-x-2">
            <button
              type="button"
              onClick={handlePopulateFromPlan}
              disabled={campaignPlanId.numeric === 0}
              className="bg-gray-700 hover:bg-gray-600 text-white px-3 py-1 rounded text-sm disabled:opacity-50"
            >
              Populate from Plan
            </button>
            <button
              type="button"
              onClick={handleAutoExtractNotes}
              disabled={
                extractEntityMutation.isPending ||
                !rawSessionNotes ||
                entries.length === 0
              }
              className="bg-purple-700 hover:bg-purple-600 text-white px-3 py-1 rounded text-sm disabled:opacity-50"
            >
              {extractEntityMutation.isPending
                ? 'Extracting...'
                : 'Auto-extract Entity Notes'}
            </button>
          </div>
        </div>

        {entries.length === 0 ? (
          <p className="text-gray-400 text-sm">
            No entities tracked. Link a campaign plan and click "Populate from
            Plan".
          </p>
        ) : (
          <div className="space-y-4">
            {entries.map((entry, idx) => (
              <div
                key={`${entry.entity_id.prefix}-${entry.entity_id.numeric}-${idx}`}
                className="border border-gray-700 rounded p-3 space-y-2"
              >
                <div className="flex items-center gap-3">
                  <span className="bg-gray-700 text-xs px-2 py-1 rounded">
                    {entry.entity_type ||
                      PREFIX_TO_NAME[
                        entry.entity_id.prefix as keyof typeof PREFIX_TO_NAME
                      ] ||
                      entry.entity_id.prefix}
                  </span>
                  <span className="font-mono text-sm">
                    {entry.entity_id.prefix}-{entry.entity_id.numeric}
                  </span>
                  <select
                    value={entry.status}
                    onChange={(e) => updateEntry(idx, 'status', e.target.value)}
                    className="bg-gray-800 border border-gray-600 rounded px-2 py-1 text-sm ml-auto"
                  >
                    {STATUS_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                  <button
                    type="button"
                    onClick={() => removeEntry(idx)}
                    className="text-red-400 hover:text-red-300 text-sm"
                  >
                    Remove
                  </button>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block text-xs text-gray-400 mb-1">
                      Raw Notes
                    </label>
                    <textarea
                      value={entry.raw_notes}
                      onChange={(e) =>
                        updateEntry(idx, 'raw_notes', e.target.value)
                      }
                      rows={2}
                      className="w-full bg-gray-800 border border-gray-600 rounded px-2 py-1 text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-400 mb-1">
                      Refined Notes
                    </label>
                    <div className="bg-gray-900 border border-gray-600 rounded px-2 py-1 text-sm min-h-[3.5rem] whitespace-pre-wrap">
                      {entry.refined_notes || (
                        <span className="text-gray-500 italic">
                          No refined notes
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
