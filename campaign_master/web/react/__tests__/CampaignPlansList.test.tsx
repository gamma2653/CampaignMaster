import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { CampaignPlansList } from '../features/planning/components/CampaignPlansList';
import type { CampaignPlan } from '../schemas';

// Mock TanStack Router
vi.mock('@tanstack/react-router', () => ({
  Link: ({ children, to, className }: { children: React.ReactNode; to: string; className?: string }) => (
    <a href={to} className={className}>
      {children}
    </a>
  ),
}));

// Mock query hooks
const mockUseCampaignPlan = vi.fn();
const mockUseDeleteCampaignPlan = vi.fn();

vi.mock('../query', () => ({
  useCampaignPlan: () => mockUseCampaignPlan(),
  useDeleteCampaignPlan: () => mockUseDeleteCampaignPlan(),
}));

const mockCampaigns: CampaignPlan[] = [
  {
    obj_id: { prefix: 'CampPlan', numeric: 1 },
    title: 'Campaign One',
    version: '1.0.0',
    setting: 'Fantasy',
    summary: 'First campaign',
    storyline: [],
    storypoints: [],
    characters: [],
    locations: [],
    items: [],
    rules: [],
    objectives: [],
  },
  {
    obj_id: { prefix: 'CampPlan', numeric: 2 },
    title: 'Campaign Two',
    version: '2.0.0',
    setting: 'Sci-Fi',
    summary: 'Second campaign',
    storyline: [],
    storypoints: [],
    characters: [],
    locations: [],
    items: [],
    rules: [],
    objectives: [],
  },
];

describe('CampaignPlansList', () => {
  let mockMutate: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    mockMutate = vi.fn();
    mockUseDeleteCampaignPlan.mockReturnValue({
      mutate: mockMutate,
      isPending: false,
    });
    vi.clearAllMocks();
  });

  it('should display loading state', () => {
    mockUseCampaignPlan.mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
    });

    render(<CampaignPlansList />);
    expect(screen.getByText('Loading campaigns...')).toBeInTheDocument();
  });

  it('should display error state', () => {
    mockUseCampaignPlan.mockReturnValue({
      data: undefined,
      isLoading: false,
      error: new Error('Network error'),
    });

    render(<CampaignPlansList />);
    expect(screen.getByText('Error loading campaigns: Network error')).toBeInTheDocument();
  });

  it('should display empty state when no campaigns', () => {
    mockUseCampaignPlan.mockReturnValue({
      data: [],
      isLoading: false,
      error: null,
    });

    render(<CampaignPlansList />);
    expect(screen.getByText(/You don't have any campaigns yet/)).toBeInTheDocument();
  });

  it('should display empty state when data is undefined', () => {
    mockUseCampaignPlan.mockReturnValue({
      data: undefined,
      isLoading: false,
      error: null,
    });

    render(<CampaignPlansList />);
    expect(screen.getByText(/You don't have any campaigns yet/)).toBeInTheDocument();
  });

  it('should render campaign cards when data is available', () => {
    mockUseCampaignPlan.mockReturnValue({
      data: mockCampaigns,
      isLoading: false,
      error: null,
    });

    render(<CampaignPlansList />);
    expect(screen.getByText('Campaign One')).toBeInTheDocument();
    expect(screen.getByText('Campaign Two')).toBeInTheDocument();
  });

  it('should render page title', () => {
    mockUseCampaignPlan.mockReturnValue({
      data: mockCampaigns,
      isLoading: false,
      error: null,
    });

    render(<CampaignPlansList />);
    expect(screen.getByRole('heading', { name: 'My Campaign Plans' })).toBeInTheDocument();
  });

  it('should call delete mutation when campaign is deleted', () => {
    mockUseCampaignPlan.mockReturnValue({
      data: mockCampaigns,
      isLoading: false,
      error: null,
    });

    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true);

    render(<CampaignPlansList />);

    // Click the first delete button
    const deleteButtons = screen.getAllByRole('button', { name: 'Delete' });
    fireEvent.click(deleteButtons[0]);

    expect(mockMutate).toHaveBeenCalledWith({ prefix: 'CampPlan', numeric: 1 });

    confirmSpy.mockRestore();
  });

  it('should show deleting indicator when mutation is pending', () => {
    mockUseCampaignPlan.mockReturnValue({
      data: mockCampaigns,
      isLoading: false,
      error: null,
    });
    mockUseDeleteCampaignPlan.mockReturnValue({
      mutate: mockMutate,
      isPending: true,
    });

    render(<CampaignPlansList />);
    expect(screen.getByText('Deleting campaign...')).toBeInTheDocument();
  });

  it('should not show deleting indicator when mutation is not pending', () => {
    mockUseCampaignPlan.mockReturnValue({
      data: mockCampaigns,
      isLoading: false,
      error: null,
    });
    mockUseDeleteCampaignPlan.mockReturnValue({
      mutate: mockMutate,
      isPending: false,
    });

    render(<CampaignPlansList />);
    expect(screen.queryByText('Deleting campaign...')).not.toBeInTheDocument();
  });
});
