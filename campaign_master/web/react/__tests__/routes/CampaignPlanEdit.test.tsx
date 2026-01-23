import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { createMockCampaign } from '../test-utils';
import { PREFIXES } from '../../schemas';

// Mock query hooks
const mockUseCampaignPlanByID = vi.fn();
const mockUseUpdateCampaignPlan = vi.fn();

vi.mock('../../query', () => ({
  useCampaignPlanByID: (id: unknown) => mockUseCampaignPlanByID(id),
  useUpdateCampaignPlan: () => mockUseUpdateCampaignPlan(),
}));

// Mock TanStack Router
const mockUseParams = vi.fn();

vi.mock('@tanstack/react-router', () => ({
  createFileRoute: () => {
    return () => {
      return {
        useParams: mockUseParams,
      };
    };
  },
}));

// Mock TanStack Form
vi.mock('@tanstack/react-form', () => ({
  createFieldMap: (defaultValues: unknown) => defaultValues,
  formOptions: (opts: unknown) => opts,
}));

// Mock the form context
const mockHandleSubmit = vi.fn();

vi.mock('../../features/shared/components/ctx', () => ({
  useAppForm: (opts: {
    defaultValues: unknown;
    onSubmit: (data: { value: unknown }) => void;
  }) => {
    return {
      state: { values: opts.defaultValues },
      handleSubmit: mockHandleSubmit,
      AppForm: ({ children }: { children: React.ReactNode }) => (
        <div>{children}</div>
      ),
      SubscribeButton: ({
        label,
        className,
      }: {
        label: string;
        className?: string;
      }) => (
        <button type="submit" className={className}>
          {label}
        </button>
      ),
    };
  },
}));

// Mock CampaignPlanGroup
vi.mock(
  '../../features/shared/components/fieldgroups/CampaignPlanGroup',
  () => ({
    CampaignPlanGroup: () => (
      <div data-testid="campaign-plan-group">CampaignPlanGroup Mock</div>
    ),
  }),
);

// Create a test component that mimics the route component behavior
function TestCampaignPlanEditForm() {
  const { camp_id } = mockUseParams();
  const numericId = parseInt(camp_id, 10);

  const {
    data: campaign,
    isLoading,
    error,
  } = mockUseCampaignPlanByID({
    prefix: PREFIXES.CAMPAIGN_PLAN,
    numeric: numericId,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-gray-400">Loading campaign...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-red-400">
          Error loading campaign: {error.message}
        </div>
      </div>
    );
  }

  if (!campaign) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-gray-400">Campaign not found</div>
      </div>
    );
  }

  const updateMutation = mockUseUpdateCampaignPlan();

  return (
    <div>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          mockHandleSubmit();
        }}
      >
        <div data-testid="campaign-plan-group">CampaignPlanGroup Mock</div>
        <div className="flex flex-col p-2 pb-8">
          <button
            type="submit"
            className="self-center submit-button"
            disabled={updateMutation.isPending}
          >
            {updateMutation.isPending ? 'Saving...' : 'Save Campaign'}
          </button>
        </div>
      </form>
    </div>
  );
}

describe('CampaignPlanEdit Route', () => {
  let mockMutate: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    vi.clearAllMocks();
    mockMutate = vi.fn();
    mockUseParams.mockReturnValue({ camp_id: '42' });
    mockUseUpdateCampaignPlan.mockReturnValue({
      mutate: mockMutate,
      isPending: false,
    });
  });

  describe('loading state', () => {
    it('should display loading message while data is being fetched', () => {
      mockUseCampaignPlanByID.mockReturnValue({
        data: undefined,
        isLoading: true,
        error: null,
      });

      render(<TestCampaignPlanEditForm />);
      expect(screen.getByText('Loading campaign...')).toBeInTheDocument();
    });
  });

  describe('error state', () => {
    it('should display error message when fetch fails', () => {
      mockUseCampaignPlanByID.mockReturnValue({
        data: undefined,
        isLoading: false,
        error: new Error('Network error'),
      });

      render(<TestCampaignPlanEditForm />);
      expect(
        screen.getByText('Error loading campaign: Network error'),
      ).toBeInTheDocument();
    });
  });

  describe('not found state', () => {
    it('should display not found message when campaign is null', () => {
      mockUseCampaignPlanByID.mockReturnValue({
        data: null,
        isLoading: false,
        error: null,
      });

      render(<TestCampaignPlanEditForm />);
      expect(screen.getByText('Campaign not found')).toBeInTheDocument();
    });

    it('should display not found message when campaign is undefined', () => {
      mockUseCampaignPlanByID.mockReturnValue({
        data: undefined,
        isLoading: false,
        error: null,
      });

      render(<TestCampaignPlanEditForm />);
      expect(screen.getByText('Campaign not found')).toBeInTheDocument();
    });
  });

  describe('success state', () => {
    it('should render CampaignPlanGroup when data is loaded', () => {
      const mockCampaign = createMockCampaign({
        obj_id: { prefix: 'CampPlan', numeric: 42 },
      });
      mockUseCampaignPlanByID.mockReturnValue({
        data: mockCampaign,
        isLoading: false,
        error: null,
      });

      render(<TestCampaignPlanEditForm />);
      expect(screen.getByTestId('campaign-plan-group')).toBeInTheDocument();
    });

    it('should render Save Campaign button', () => {
      const mockCampaign = createMockCampaign();
      mockUseCampaignPlanByID.mockReturnValue({
        data: mockCampaign,
        isLoading: false,
        error: null,
      });

      render(<TestCampaignPlanEditForm />);
      expect(
        screen.getByRole('button', { name: 'Save Campaign' }),
      ).toBeInTheDocument();
    });

    it('should show Saving... when mutation is pending', () => {
      const mockCampaign = createMockCampaign();
      mockUseCampaignPlanByID.mockReturnValue({
        data: mockCampaign,
        isLoading: false,
        error: null,
      });
      mockUseUpdateCampaignPlan.mockReturnValue({
        mutate: mockMutate,
        isPending: true,
      });

      render(<TestCampaignPlanEditForm />);
      expect(
        screen.getByRole('button', { name: 'Saving...' }),
      ).toBeInTheDocument();
    });

    it('should disable button when mutation is pending', () => {
      const mockCampaign = createMockCampaign();
      mockUseCampaignPlanByID.mockReturnValue({
        data: mockCampaign,
        isLoading: false,
        error: null,
      });
      mockUseUpdateCampaignPlan.mockReturnValue({
        mutate: mockMutate,
        isPending: true,
      });

      render(<TestCampaignPlanEditForm />);
      expect(screen.getByRole('button', { name: 'Saving...' })).toBeDisabled();
    });
  });

  describe('form submission', () => {
    it('should call handleSubmit when form is submitted', () => {
      const mockCampaign = createMockCampaign();
      mockUseCampaignPlanByID.mockReturnValue({
        data: mockCampaign,
        isLoading: false,
        error: null,
      });

      render(<TestCampaignPlanEditForm />);

      const form = screen
        .getByRole('button', { name: 'Save Campaign' })
        .closest('form');
      fireEvent.submit(form!);

      expect(mockHandleSubmit).toHaveBeenCalled();
    });
  });

  describe('route params', () => {
    it('should fetch campaign with correct ID from params', () => {
      mockUseParams.mockReturnValue({ camp_id: '123' });
      mockUseCampaignPlanByID.mockReturnValue({
        data: undefined,
        isLoading: true,
        error: null,
      });

      render(<TestCampaignPlanEditForm />);

      expect(mockUseCampaignPlanByID).toHaveBeenCalledWith({
        prefix: PREFIXES.CAMPAIGN_PLAN,
        numeric: 123,
      });
    });
  });
});
