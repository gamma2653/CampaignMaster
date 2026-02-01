import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, act } from '@testing-library/react';
import React from 'react';
import { PREFIXES } from '../../schemas';
import type {
  CampaignExecution,
  CampaignPlan,
  ExecutionEntry,
  AgentConfig,
} from '../../schemas';

// Mock query hooks
const mockUseCampaignExecutionByID = vi.fn();
const mockUseCampaignPlan = vi.fn();
const mockUseAgentConfig = vi.fn();
const mockUpdateMutate = vi.fn();
const mockUseUpdateCampaignExecution = vi.fn();
const mockDeleteMutate = vi.fn();
const mockUseDeleteCampaignExecution = vi.fn();
const mockRefineNotesMutate = vi.fn();
const mockUseRefineNotes = vi.fn();
const mockExtractMutate = vi.fn();
const mockUseExtractEntityNotes = vi.fn();

vi.mock('../../query', () => ({
  useCampaignExecutionByID: (id: unknown) => mockUseCampaignExecutionByID(id),
  useCampaignPlan: () => mockUseCampaignPlan(),
  useAgentConfig: () => mockUseAgentConfig(),
  useUpdateCampaignExecution: () => mockUseUpdateCampaignExecution(),
  useDeleteCampaignExecution: () => mockUseDeleteCampaignExecution(),
  useRefineNotes: () => mockUseRefineNotes(),
  useExtractEntityNotes: () => mockUseExtractEntityNotes(),
}));

// Mock TanStack Router
const mockNavigate = vi.fn();
const mockUseParams = vi.fn();

vi.mock('@tanstack/react-router', () => ({
  createFileRoute: () => {
    const route = () => ({
      useParams: mockUseParams,
    });
    route.useParams = mockUseParams;
    return route;
  },
  useNavigate: () => mockNavigate,
}));

const STATUS_OPTIONS = [
  { value: 'not_encountered', label: 'Not Encountered' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'completed', label: 'Completed' },
  { value: 'skipped', label: 'Skipped' },
];

// Test component that mirrors the route's logic
function TestExecuteDetail() {
  const { camp_id } = mockUseParams();
  const numericId = parseInt(camp_id, 10);

  const {
    data: execution,
    isLoading,
    error,
  } = mockUseCampaignExecutionByID({
    prefix: PREFIXES.EXECUTION,
    numeric: numericId,
  });
  const { data: plans } = mockUseCampaignPlan();
  const { data: agentConfigs } = mockUseAgentConfig();
  const updateMutation = mockUseUpdateCampaignExecution();
  const deleteMutation = mockUseDeleteCampaignExecution();
  const refineNotesMutation = mockUseRefineNotes();
  const extractEntityMutation = mockUseExtractEntityNotes();

  const [title, setTitle] = React.useState('');
  const [sessionDate, setSessionDate] = React.useState('');
  const [rawSessionNotes, setRawSessionNotes] = React.useState('');
  const [refinedSessionNotes, setRefinedSessionNotes] = React.useState('');
  const [refinementMode, setRefinementMode] = React.useState<
    'narrative' | 'structured'
  >('narrative');
  const [entries, setEntries] = React.useState<ExecutionEntry[]>([]);
  const [campaignPlanId, setCampaignPlanId] = React.useState({
    prefix: PREFIXES.CAMPAIGN_PLAN,
    numeric: 0,
  });

  const ex = execution as CampaignExecution | undefined;

  React.useEffect(() => {
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
    deleteMutation.mutate(ex.obj_id, {
      onSuccess: () => mockNavigate({ to: '/campaign/execute' }),
    });
  };

  const handleRefineNotes = () => {
    const configs = (agentConfigs ?? []) as AgentConfig[];
    const agent = configs.find((c) => c.is_default && c.is_enabled) ?? configs[0];
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
        onSuccess: (data: { error_message?: string; refined_text: string }) => {
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
    const addEntries = (items: { obj_id: { prefix: string; numeric: number } }[], typeName: string) => {
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
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">
          Execution: {ex.obj_id.prefix}-{ex.obj_id.numeric}
        </h1>
        <div className="space-x-2">
          <button
            type="button"
            onClick={handleSave}
            disabled={updateMutation.isPending}
          >
            {updateMutation.isPending ? 'Saving...' : 'Save'}
          </button>
          <button type="button" onClick={handleDelete}>
            Delete
          </button>
        </div>
      </div>

      {updateMutation.isSuccess && (
        <div className="text-green-400 text-sm">Saved successfully.</div>
      )}

      <div>
        <label>Title</label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          aria-label="Title"
        />
      </div>
      <div>
        <label>Session Date</label>
        <input
          type="date"
          value={sessionDate}
          onChange={(e) => setSessionDate(e.target.value)}
          aria-label="Session Date"
        />
      </div>

      <div>
        <label>Linked Campaign Plan</label>
        <select
          value={`${campaignPlanId.prefix}-${campaignPlanId.numeric}`}
          onChange={(e) => {
            const [prefix, numStr] = e.target.value.split('-');
            setCampaignPlanId({ prefix, numeric: parseInt(numStr, 10) });
          }}
          aria-label="Linked Campaign Plan"
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

      <div>
        <h2>Session Notes</h2>
        <label>Raw Notes</label>
        <textarea
          value={rawSessionNotes}
          onChange={(e) => setRawSessionNotes(e.target.value)}
          aria-label="Raw Notes"
        />
        <div>
          <label>Mode:</label>
          <select
            value={refinementMode}
            onChange={(e) =>
              setRefinementMode(e.target.value as 'narrative' | 'structured')
            }
            aria-label="Refinement Mode"
          >
            <option value="narrative">Narrative</option>
            <option value="structured">Structured</option>
          </select>
          <button
            type="button"
            onClick={handleRefineNotes}
            disabled={refineNotesMutation.isPending || !rawSessionNotes}
          >
            {refineNotesMutation.isPending ? 'Refining...' : 'Refine with AI'}
          </button>
        </div>
        {refinedSessionNotes && (
          <div data-testid="refined-notes">{refinedSessionNotes}</div>
        )}
      </div>

      <div>
        <h2>Entity Tracking</h2>
        <button
          type="button"
          onClick={handlePopulateFromPlan}
          disabled={campaignPlanId.numeric === 0}
        >
          Populate from Plan
        </button>
        <button
          type="button"
          onClick={() => {}}
          disabled={
            extractEntityMutation.isPending ||
            !rawSessionNotes ||
            entries.length === 0
          }
        >
          {extractEntityMutation.isPending
            ? 'Extracting...'
            : 'Auto-extract Entity Notes'}
        </button>

        {entries.length === 0 ? (
          <p>
            No entities tracked. Link a campaign plan and click "Populate from
            Plan".
          </p>
        ) : (
          <div>
            {entries.map((entry, idx) => (
              <div
                key={`${entry.entity_id.prefix}-${entry.entity_id.numeric}-${idx}`}
                data-testid={`entry-${idx}`}
              >
                <span data-testid={`entry-type-${idx}`}>
                  {entry.entity_type || entry.entity_id.prefix}
                </span>
                <span data-testid={`entry-id-${idx}`}>
                  {entry.entity_id.prefix}-{entry.entity_id.numeric}
                </span>
                <select
                  value={entry.status}
                  onChange={(e) => updateEntry(idx, 'status', e.target.value)}
                  aria-label={`Status for entry ${idx}`}
                >
                  {STATUS_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
                <button type="button" onClick={() => removeEntry(idx)}>
                  Remove
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function createMockExecution(
  overrides: Partial<CampaignExecution> = {},
): CampaignExecution {
  return {
    obj_id: { prefix: PREFIXES.EXECUTION, numeric: 1 },
    campaign_plan_id: { prefix: PREFIXES.CAMPAIGN_PLAN, numeric: 0 },
    title: 'Test Session',
    session_date: '2025-01-15',
    raw_session_notes: 'The party entered the dungeon.',
    refined_session_notes: '',
    refinement_mode: 'narrative',
    entries: [],
    ...overrides,
  };
}

function createMockPlan(
  overrides: Partial<CampaignPlan> = {},
): CampaignPlan {
  return {
    obj_id: { prefix: PREFIXES.CAMPAIGN_PLAN, numeric: 1 },
    title: 'Test Campaign',
    version: '1.0',
    setting: 'Fantasy',
    summary: 'A test campaign',
    storyline: [],
    storypoints: [],
    characters: [],
    locations: [],
    items: [],
    rules: [],
    objectives: [],
    ...overrides,
  };
}

function createMockAgent(overrides: Partial<AgentConfig> = {}): AgentConfig {
  return {
    obj_id: { prefix: PREFIXES.AGENT_CONFIG, numeric: 1 },
    name: 'Test Agent',
    provider_type: 'openai',
    api_key: 'test-key',
    base_url: 'https://api.openai.com',
    model: 'gpt-4',
    max_tokens: 1000,
    temperature: 0.7,
    is_default: true,
    is_enabled: true,
    system_prompt: 'You are a helpful assistant.',
    ...overrides,
  };
}

function setupDefaultMocks(execution?: CampaignExecution) {
  mockUseParams.mockReturnValue({ camp_id: '1' });
  mockUseCampaignExecutionByID.mockReturnValue({
    data: execution ?? createMockExecution(),
    isLoading: false,
    error: null,
  });
  mockUseCampaignPlan.mockReturnValue({ data: [] });
  mockUseAgentConfig.mockReturnValue({ data: [] });
  mockUseUpdateCampaignExecution.mockReturnValue({
    mutate: mockUpdateMutate,
    isPending: false,
    isSuccess: false,
  });
  mockUseDeleteCampaignExecution.mockReturnValue({
    mutate: mockDeleteMutate,
    isPending: false,
  });
  mockUseRefineNotes.mockReturnValue({
    mutate: mockRefineNotesMutate,
    isPending: false,
  });
  mockUseExtractEntityNotes.mockReturnValue({
    mutate: mockExtractMutate,
    isPending: false,
  });
}

describe('ExecuteDetail Route', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    setupDefaultMocks();
  });

  describe('loading state', () => {
    it('should display loading message while data is being fetched', () => {
      mockUseCampaignExecutionByID.mockReturnValue({
        data: undefined,
        isLoading: true,
        error: null,
      });

      render(<TestExecuteDetail />);
      expect(screen.getByText('Loading execution...')).toBeInTheDocument();
    });
  });

  describe('error state', () => {
    it('should display error message when fetch fails', () => {
      mockUseCampaignExecutionByID.mockReturnValue({
        data: undefined,
        isLoading: false,
        error: new Error('Server error'),
      });

      render(<TestExecuteDetail />);
      expect(screen.getByText('Error: Server error')).toBeInTheDocument();
    });
  });

  describe('not found state', () => {
    it('should display not found when execution is undefined', () => {
      mockUseCampaignExecutionByID.mockReturnValue({
        data: undefined,
        isLoading: false,
        error: null,
      });

      render(<TestExecuteDetail />);
      expect(screen.getByText('Execution not found.')).toBeInTheDocument();
    });
  });

  describe('route params', () => {
    it('should fetch execution with correct ID from params', () => {
      mockUseParams.mockReturnValue({ camp_id: '42' });
      mockUseCampaignExecutionByID.mockReturnValue({
        data: undefined,
        isLoading: true,
        error: null,
      });

      render(<TestExecuteDetail />);

      expect(mockUseCampaignExecutionByID).toHaveBeenCalledWith({
        prefix: PREFIXES.EXECUTION,
        numeric: 42,
      });
    });
  });

  describe('success state', () => {
    it('should render the execution heading', () => {
      render(<TestExecuteDetail />);
      expect(screen.getByText('Execution: EX-1')).toBeInTheDocument();
    });

    it('should render Save and Delete buttons', () => {
      render(<TestExecuteDetail />);
      expect(screen.getByRole('button', { name: 'Save' })).toBeInTheDocument();
      expect(
        screen.getByRole('button', { name: 'Delete' }),
      ).toBeInTheDocument();
    });

    it('should populate form fields from execution data', () => {
      const execution = createMockExecution({
        title: 'My Session',
        session_date: '2025-06-01',
      });
      setupDefaultMocks(execution);

      render(<TestExecuteDetail />);
      expect(screen.getByDisplayValue('My Session')).toBeInTheDocument();
      expect(screen.getByDisplayValue('2025-06-01')).toBeInTheDocument();
    });

    it('should render session notes section', () => {
      render(<TestExecuteDetail />);
      expect(screen.getByText('Session Notes')).toBeInTheDocument();
    });

    it('should render entity tracking section', () => {
      render(<TestExecuteDetail />);
      expect(screen.getByText('Entity Tracking')).toBeInTheDocument();
    });
  });

  describe('save', () => {
    it('should call update mutation when Save is clicked', () => {
      render(<TestExecuteDetail />);
      fireEvent.click(screen.getByRole('button', { name: 'Save' }));

      expect(mockUpdateMutate).toHaveBeenCalledWith(
        expect.objectContaining({
          obj_id: { prefix: PREFIXES.EXECUTION, numeric: 1 },
          title: 'Test Session',
        }),
      );
    });

    it('should show Saving... when update is pending', () => {
      mockUseUpdateCampaignExecution.mockReturnValue({
        mutate: mockUpdateMutate,
        isPending: true,
        isSuccess: false,
      });

      render(<TestExecuteDetail />);
      expect(
        screen.getByRole('button', { name: 'Saving...' }),
      ).toBeInTheDocument();
    });

    it('should disable Save button when update is pending', () => {
      mockUseUpdateCampaignExecution.mockReturnValue({
        mutate: mockUpdateMutate,
        isPending: true,
        isSuccess: false,
      });

      render(<TestExecuteDetail />);
      expect(
        screen.getByRole('button', { name: 'Saving...' }),
      ).toBeDisabled();
    });

    it('should show success message after save', () => {
      mockUseUpdateCampaignExecution.mockReturnValue({
        mutate: mockUpdateMutate,
        isPending: false,
        isSuccess: true,
      });

      render(<TestExecuteDetail />);
      expect(screen.getByText('Saved successfully.')).toBeInTheDocument();
    });
  });

  describe('delete', () => {
    it('should call delete mutation when Delete is clicked', () => {
      render(<TestExecuteDetail />);
      fireEvent.click(screen.getByRole('button', { name: 'Delete' }));

      expect(mockDeleteMutate).toHaveBeenCalledWith(
        { prefix: PREFIXES.EXECUTION, numeric: 1 },
        expect.objectContaining({
          onSuccess: expect.any(Function),
        }),
      );
    });

    it('should navigate to list after successful delete', () => {
      render(<TestExecuteDetail />);
      fireEvent.click(screen.getByRole('button', { name: 'Delete' }));

      const callbacks = mockDeleteMutate.mock.calls[0][1];
      callbacks.onSuccess();

      expect(mockNavigate).toHaveBeenCalledWith({
        to: '/campaign/execute',
      });
    });
  });

  describe('entity tracking', () => {
    it('should display empty message when no entries exist', () => {
      render(<TestExecuteDetail />);
      expect(
        screen.getByText(/No entities tracked/),
      ).toBeInTheDocument();
    });

    it('should render entries from execution data', () => {
      const entries: ExecutionEntry[] = [
        {
          entity_id: { prefix: 'C', numeric: 1 },
          entity_type: 'Character',
          status: 'not_encountered',
          raw_notes: '',
          refined_notes: '',
        },
        {
          entity_id: { prefix: 'L', numeric: 2 },
          entity_type: 'Location',
          status: 'in_progress',
          raw_notes: '',
          refined_notes: '',
        },
      ];
      setupDefaultMocks(createMockExecution({ entries }));

      render(<TestExecuteDetail />);
      expect(screen.getByTestId('entry-0')).toBeInTheDocument();
      expect(screen.getByTestId('entry-1')).toBeInTheDocument();
      expect(screen.getByText('Character')).toBeInTheDocument();
      expect(screen.getByText('Location')).toBeInTheDocument();
      expect(screen.getByText('C-1')).toBeInTheDocument();
      expect(screen.getByText('L-2')).toBeInTheDocument();
    });

    it('should remove an entry when Remove is clicked', () => {
      const entries: ExecutionEntry[] = [
        {
          entity_id: { prefix: 'C', numeric: 1 },
          entity_type: 'Character',
          status: 'not_encountered',
          raw_notes: '',
          refined_notes: '',
        },
        {
          entity_id: { prefix: 'L', numeric: 2 },
          entity_type: 'Location',
          status: 'not_encountered',
          raw_notes: '',
          refined_notes: '',
        },
      ];
      setupDefaultMocks(createMockExecution({ entries }));

      render(<TestExecuteDetail />);
      expect(screen.getAllByRole('button', { name: 'Remove' })).toHaveLength(2);

      // Remove the first entry
      fireEvent.click(screen.getAllByRole('button', { name: 'Remove' })[0]);

      // Only one entry should remain
      expect(screen.getAllByRole('button', { name: 'Remove' })).toHaveLength(1);
      expect(screen.getByText('Location')).toBeInTheDocument();
    });

    it('should disable Populate from Plan when no plan is selected', () => {
      render(<TestExecuteDetail />);
      expect(
        screen.getByRole('button', { name: 'Populate from Plan' }),
      ).toBeDisabled();
    });

    it('should populate entries from linked campaign plan', () => {
      const plan = createMockPlan({
        obj_id: { prefix: PREFIXES.CAMPAIGN_PLAN, numeric: 5 },
        characters: [
          {
            obj_id: { prefix: 'C', numeric: 10 },
            name: 'Hero',
            role: 'PC',
            backstory: '',
            attributes: {},
            skills: {},
            storylines: [],
            inventory: [],
          },
        ],
        locations: [
          {
            obj_id: { prefix: 'L', numeric: 20 },
            name: 'Town',
            description: '',
            neighboring_locations: [],
            coords: [0, 0],
          },
        ],
      });

      const execution = createMockExecution({
        campaign_plan_id: { prefix: PREFIXES.CAMPAIGN_PLAN, numeric: 5 },
      });

      setupDefaultMocks(execution);
      mockUseCampaignPlan.mockReturnValue({ data: [plan] });

      render(<TestExecuteDetail />);

      // The button should be enabled since a plan is selected
      const populateBtn = screen.getByRole('button', {
        name: 'Populate from Plan',
      });
      expect(populateBtn).not.toBeDisabled();

      fireEvent.click(populateBtn);

      // Entries should now be populated
      expect(screen.getByText('Character')).toBeInTheDocument();
      expect(screen.getByText('Location')).toBeInTheDocument();
      expect(screen.getByText('C-10')).toBeInTheDocument();
      expect(screen.getByText('L-20')).toBeInTheDocument();
    });
  });

  describe('AI refinement', () => {
    it('should disable Refine button when raw notes are empty', () => {
      setupDefaultMocks(createMockExecution({ raw_session_notes: '' }));

      render(<TestExecuteDetail />);
      expect(
        screen.getByRole('button', { name: 'Refine with AI' }),
      ).toBeDisabled();
    });

    it('should alert when no AI agent is configured', () => {
      const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {});
      mockUseAgentConfig.mockReturnValue({ data: [] });

      render(<TestExecuteDetail />);
      fireEvent.click(
        screen.getByRole('button', { name: 'Refine with AI' }),
      );

      expect(alertSpy).toHaveBeenCalledWith(
        'No AI agent configured. Configure one in Agent settings.',
      );
      alertSpy.mockRestore();
    });

    it('should call refine mutation when agent is configured', () => {
      const agent = createMockAgent();
      mockUseAgentConfig.mockReturnValue({ data: [agent] });

      render(<TestExecuteDetail />);
      fireEvent.click(
        screen.getByRole('button', { name: 'Refine with AI' }),
      );

      expect(mockRefineNotesMutate).toHaveBeenCalledWith(
        expect.objectContaining({
          raw_notes: 'The party entered the dungeon.',
          mode: 'narrative',
          provider_type: 'openai',
        }),
        expect.objectContaining({
          onSuccess: expect.any(Function),
        }),
      );
    });

    it('should show Refining... when refinement is pending', () => {
      mockUseRefineNotes.mockReturnValue({
        mutate: mockRefineNotesMutate,
        isPending: true,
      });

      render(<TestExecuteDetail />);
      expect(
        screen.getByRole('button', { name: 'Refining...' }),
      ).toBeInTheDocument();
    });

    it('should display refined notes after successful refinement', () => {
      const agent = createMockAgent();
      mockUseAgentConfig.mockReturnValue({ data: [agent] });

      render(<TestExecuteDetail />);
      fireEvent.click(
        screen.getByRole('button', { name: 'Refine with AI' }),
      );

      const callbacks = mockRefineNotesMutate.mock.calls[0][1];
      act(() => {
        callbacks.onSuccess({
          refined_text: 'A polished summary of the session.',
        });
      });

      expect(screen.getByTestId('refined-notes')).toHaveTextContent(
        'A polished summary of the session.',
      );
    });

    it('should alert on refinement error', () => {
      const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {});
      const agent = createMockAgent();
      mockUseAgentConfig.mockReturnValue({ data: [agent] });

      render(<TestExecuteDetail />);
      fireEvent.click(
        screen.getByRole('button', { name: 'Refine with AI' }),
      );

      const callbacks = mockRefineNotesMutate.mock.calls[0][1];
      callbacks.onSuccess({
        error_message: 'API quota exceeded',
        refined_text: '',
      });

      expect(alertSpy).toHaveBeenCalledWith(
        'Refinement error: API quota exceeded',
      );
      alertSpy.mockRestore();
    });

    it('should disable Auto-extract when no raw notes or no entries', () => {
      setupDefaultMocks(createMockExecution({ raw_session_notes: '' }));

      render(<TestExecuteDetail />);
      expect(
        screen.getByRole('button', { name: 'Auto-extract Entity Notes' }),
      ).toBeDisabled();
    });
  });

  describe('refinement mode', () => {
    it('should default to narrative mode', () => {
      render(<TestExecuteDetail />);
      const modeSelect = screen.getByLabelText('Refinement Mode') as HTMLSelectElement;
      expect(modeSelect.value).toBe('narrative');
    });

    it('should allow switching to structured mode', () => {
      render(<TestExecuteDetail />);
      const modeSelect = screen.getByLabelText('Refinement Mode');
      fireEvent.change(modeSelect, { target: { value: 'structured' } });
      expect((modeSelect as HTMLSelectElement).value).toBe('structured');
    });
  });
});
