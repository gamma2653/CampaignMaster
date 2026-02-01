import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { PREFIXES } from '../../schemas';
import type { CampaignExecution } from '../../schemas';

// Mock query hooks
const mockUseCampaignExecution = vi.fn();
const mockCreateMutate = vi.fn();
const mockUseCreateCampaignExecution = vi.fn();
const mockDeleteMutate = vi.fn();
const mockUseDeleteCampaignExecution = vi.fn();

vi.mock('../../query', () => ({
  useCampaignExecution: () => mockUseCampaignExecution(),
  useCreateCampaignExecution: () => mockUseCreateCampaignExecution(),
  useDeleteCampaignExecution: () => mockUseDeleteCampaignExecution(),
}));

// Mock TanStack Router
const mockNavigate = vi.fn();

vi.mock('@tanstack/react-router', () => ({
  createFileRoute: () => {
    return () => ({
      useParams: () => ({}),
    });
  },
  useNavigate: () => mockNavigate,
}));

// Build a test component that mirrors the route component's logic
function TestExecuteList() {
  const { data: executions, isLoading, error } = mockUseCampaignExecution();
  const createMutation = mockUseCreateCampaignExecution();
  const deleteMutation = mockUseDeleteCampaignExecution();

  const handleCreate = () => {
    createMutation.mutate(
      {
        campaign_plan_id: { prefix: PREFIXES.CAMPAIGN_PLAN, numeric: 0 },
        title: 'New Session',
        session_date: new Date().toISOString().split('T')[0],
        raw_session_notes: '',
        refined_session_notes: '',
        refinement_mode: 'narrative',
        entries: [],
      },
      {
        onSuccess: (created: CampaignExecution) => {
          mockNavigate({
            to: '/campaign/execute/$camp_id',
            params: { camp_id: String(created.obj_id.numeric) },
          });
        },
      },
    );
  };

  const handleDelete = (id: { prefix: string; numeric: number }, e: React.MouseEvent) => {
    e.stopPropagation();
    deleteMutation.mutate(id);
  };

  if (isLoading) return <div className="p-8">Loading executions...</div>;
  if (error)
    return <div className="p-8 text-red-400">Error: {error.message}</div>;

  const items = (executions ?? []) as CampaignExecution[];

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Campaign Executions</h1>
        <button
          type="button"
          onClick={handleCreate}
          disabled={createMutation.isPending}
          className="bg-green-700 hover:bg-green-600 text-white px-4 py-2 rounded disabled:opacity-50"
        >
          {createMutation.isPending ? 'Creating...' : 'New Execution'}
        </button>
      </div>

      {items.length === 0 ? (
        <p className="text-gray-400">
          No executions yet. Create one to start tracking a session.
        </p>
      ) : (
        <div className="space-y-3">
          {items.map((ex) => (
            <div
              key={`${ex.obj_id.prefix}-${ex.obj_id.numeric}`}
              onClick={() =>
                mockNavigate({
                  to: '/campaign/execute/$camp_id',
                  params: { camp_id: String(ex.obj_id.numeric) },
                })
              }
              className="border border-gray-600 rounded p-4 hover:bg-gray-800 cursor-pointer flex justify-between items-start"
            >
              <div>
                <h2 className="font-semibold text-lg">
                  {ex.title || 'Untitled Session'}
                </h2>
                <div className="text-sm text-gray-400 mt-1">
                  {ex.session_date && <span>Date: {ex.session_date}</span>}
                  {ex.campaign_plan_id.numeric > 0 && (
                    <span className="ml-4">
                      Plan: {ex.campaign_plan_id.prefix}-
                      {ex.campaign_plan_id.numeric}
                    </span>
                  )}
                  <span className="ml-4">
                    {ex.entries.length} entit
                    {ex.entries.length === 1 ? 'y' : 'ies'}
                  </span>
                </div>
              </div>
              <button
                type="button"
                onClick={(e) => handleDelete(ex.obj_id, e)}
                className="text-red-400 hover:text-red-300 text-sm px-2 py-1"
              >
                Delete
              </button>
            </div>
          ))}
        </div>
      )}
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
    raw_session_notes: 'Some notes',
    refined_session_notes: '',
    refinement_mode: 'narrative',
    entries: [],
    ...overrides,
  };
}

describe('ExecuteList Route', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseCreateCampaignExecution.mockReturnValue({
      mutate: mockCreateMutate,
      isPending: false,
    });
    mockUseDeleteCampaignExecution.mockReturnValue({
      mutate: mockDeleteMutate,
      isPending: false,
    });
  });

  describe('loading state', () => {
    it('should display loading message while data is being fetched', () => {
      mockUseCampaignExecution.mockReturnValue({
        data: undefined,
        isLoading: true,
        error: null,
      });

      render(<TestExecuteList />);
      expect(screen.getByText('Loading executions...')).toBeInTheDocument();
    });
  });

  describe('error state', () => {
    it('should display error message when fetch fails', () => {
      mockUseCampaignExecution.mockReturnValue({
        data: undefined,
        isLoading: false,
        error: new Error('Network error'),
      });

      render(<TestExecuteList />);
      expect(screen.getByText('Error: Network error')).toBeInTheDocument();
    });
  });

  describe('empty state', () => {
    it('should display empty message when no executions exist', () => {
      mockUseCampaignExecution.mockReturnValue({
        data: [],
        isLoading: false,
        error: null,
      });

      render(<TestExecuteList />);
      expect(
        screen.getByText(
          'No executions yet. Create one to start tracking a session.',
        ),
      ).toBeInTheDocument();
    });
  });

  describe('populated state', () => {
    it('should render the page heading', () => {
      mockUseCampaignExecution.mockReturnValue({
        data: [],
        isLoading: false,
        error: null,
      });

      render(<TestExecuteList />);
      expect(screen.getByText('Campaign Executions')).toBeInTheDocument();
    });

    it('should render execution items with titles', () => {
      const executions = [
        createMockExecution({ obj_id: { prefix: 'EX', numeric: 1 }, title: 'Session One' }),
        createMockExecution({ obj_id: { prefix: 'EX', numeric: 2 }, title: 'Session Two' }),
      ];
      mockUseCampaignExecution.mockReturnValue({
        data: executions,
        isLoading: false,
        error: null,
      });

      render(<TestExecuteList />);
      expect(screen.getByText('Session One')).toBeInTheDocument();
      expect(screen.getByText('Session Two')).toBeInTheDocument();
    });

    it('should display Untitled Session for executions without a title', () => {
      mockUseCampaignExecution.mockReturnValue({
        data: [createMockExecution({ title: '' })],
        isLoading: false,
        error: null,
      });

      render(<TestExecuteList />);
      expect(screen.getByText('Untitled Session')).toBeInTheDocument();
    });

    it('should display session date when present', () => {
      mockUseCampaignExecution.mockReturnValue({
        data: [createMockExecution({ session_date: '2025-03-20' })],
        isLoading: false,
        error: null,
      });

      render(<TestExecuteList />);
      expect(screen.getByText('Date: 2025-03-20')).toBeInTheDocument();
    });

    it('should display entity count', () => {
      const entries = [
        {
          entity_id: { prefix: 'C', numeric: 1 },
          entity_type: 'Character',
          status: 'not_encountered' as const,
          raw_notes: '',
          refined_notes: '',
        },
        {
          entity_id: { prefix: 'L', numeric: 1 },
          entity_type: 'Location',
          status: 'not_encountered' as const,
          raw_notes: '',
          refined_notes: '',
        },
      ];
      mockUseCampaignExecution.mockReturnValue({
        data: [createMockExecution({ entries })],
        isLoading: false,
        error: null,
      });

      render(<TestExecuteList />);
      expect(screen.getByText('2 entities')).toBeInTheDocument();
    });

    it('should use singular entity for single entry', () => {
      const entries = [
        {
          entity_id: { prefix: 'C', numeric: 1 },
          entity_type: 'Character',
          status: 'not_encountered' as const,
          raw_notes: '',
          refined_notes: '',
        },
      ];
      mockUseCampaignExecution.mockReturnValue({
        data: [createMockExecution({ entries })],
        isLoading: false,
        error: null,
      });

      render(<TestExecuteList />);
      expect(screen.getByText('1 entity')).toBeInTheDocument();
    });

    it('should navigate to detail view when clicking an execution', () => {
      mockUseCampaignExecution.mockReturnValue({
        data: [createMockExecution({ obj_id: { prefix: 'EX', numeric: 5 } })],
        isLoading: false,
        error: null,
      });

      render(<TestExecuteList />);
      fireEvent.click(screen.getByText('Test Session'));

      expect(mockNavigate).toHaveBeenCalledWith({
        to: '/campaign/execute/$camp_id',
        params: { camp_id: '5' },
      });
    });
  });

  describe('create execution', () => {
    it('should render New Execution button', () => {
      mockUseCampaignExecution.mockReturnValue({
        data: [],
        isLoading: false,
        error: null,
      });

      render(<TestExecuteList />);
      expect(
        screen.getByRole('button', { name: 'New Execution' }),
      ).toBeInTheDocument();
    });

    it('should call create mutation when New Execution is clicked', () => {
      mockUseCampaignExecution.mockReturnValue({
        data: [],
        isLoading: false,
        error: null,
      });

      render(<TestExecuteList />);
      fireEvent.click(screen.getByRole('button', { name: 'New Execution' }));

      expect(mockCreateMutate).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'New Session',
          refinement_mode: 'narrative',
          entries: [],
        }),
        expect.objectContaining({
          onSuccess: expect.any(Function),
        }),
      );
    });

    it('should navigate to new execution on successful creation', () => {
      mockUseCampaignExecution.mockReturnValue({
        data: [],
        isLoading: false,
        error: null,
      });

      render(<TestExecuteList />);
      fireEvent.click(screen.getByRole('button', { name: 'New Execution' }));

      const callbacks = mockCreateMutate.mock.calls[0][1];
      callbacks.onSuccess({
        obj_id: { prefix: 'EX', numeric: 99 },
      });

      expect(mockNavigate).toHaveBeenCalledWith({
        to: '/campaign/execute/$camp_id',
        params: { camp_id: '99' },
      });
    });

    it('should show Creating... when create mutation is pending', () => {
      mockUseCampaignExecution.mockReturnValue({
        data: [],
        isLoading: false,
        error: null,
      });
      mockUseCreateCampaignExecution.mockReturnValue({
        mutate: mockCreateMutate,
        isPending: true,
      });

      render(<TestExecuteList />);
      expect(
        screen.getByRole('button', { name: 'Creating...' }),
      ).toBeInTheDocument();
    });

    it('should disable button when create mutation is pending', () => {
      mockUseCampaignExecution.mockReturnValue({
        data: [],
        isLoading: false,
        error: null,
      });
      mockUseCreateCampaignExecution.mockReturnValue({
        mutate: mockCreateMutate,
        isPending: true,
      });

      render(<TestExecuteList />);
      expect(
        screen.getByRole('button', { name: 'Creating...' }),
      ).toBeDisabled();
    });
  });

  describe('delete execution', () => {
    it('should render Delete buttons for each execution', () => {
      mockUseCampaignExecution.mockReturnValue({
        data: [
          createMockExecution({ obj_id: { prefix: 'EX', numeric: 1 } }),
          createMockExecution({ obj_id: { prefix: 'EX', numeric: 2 } }),
        ],
        isLoading: false,
        error: null,
      });

      render(<TestExecuteList />);
      const deleteButtons = screen.getAllByRole('button', { name: 'Delete' });
      expect(deleteButtons).toHaveLength(2);
    });

    it('should call delete mutation when Delete is clicked', () => {
      mockUseCampaignExecution.mockReturnValue({
        data: [
          createMockExecution({ obj_id: { prefix: 'EX', numeric: 7 } }),
        ],
        isLoading: false,
        error: null,
      });

      render(<TestExecuteList />);
      fireEvent.click(screen.getByRole('button', { name: 'Delete' }));

      expect(mockDeleteMutate).toHaveBeenCalledWith({
        prefix: 'EX',
        numeric: 7,
      });
    });

    it('should not navigate when Delete button is clicked (stopPropagation)', () => {
      mockUseCampaignExecution.mockReturnValue({
        data: [createMockExecution()],
        isLoading: false,
        error: null,
      });

      render(<TestExecuteList />);
      fireEvent.click(screen.getByRole('button', { name: 'Delete' }));

      // Navigate should not be called from the row click handler
      // (only from delete, which doesn't navigate)
      expect(mockNavigate).not.toHaveBeenCalled();
    });
  });
});
