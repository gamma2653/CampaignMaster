import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import Navbar from '../features/shared/components/nav';

// Mock image imports
vi.mock('../../../../../assets/images/icons/book2.png', () => ({
  default: 'book-icon.png',
}));
vi.mock('../../../../../assets/images/Me.jpg', () => ({
  default: 'profile.jpg',
}));

// Mock TanStack Router
const mockNavigate = vi.fn();
const mockInvalidate = vi.fn();

vi.mock('@tanstack/react-router', () => ({
  Link: ({
    children,
    to,
    className,
  }: {
    children: React.ReactNode;
    to: string;
    className?: string;
  }) => (
    <a href={to} className={className} data-testid="nav-link">
      {children}
    </a>
  ),
  useNavigate: () => mockNavigate,
  useRouter: () => ({ invalidate: mockInvalidate }),
}));

// Mock query hooks
const mockMutate = vi.fn();
const mockUseCreateCampaignPlan = vi.fn();

vi.mock('../query', () => ({
  useCreateCampaignPlan: () => mockUseCreateCampaignPlan(),
}));

// Mock auth hooks
const mockLogoutMutate = vi.fn();
vi.mock('../auth', () => ({
  useLogout: () => ({
    mutate: mockLogoutMutate,
    isPending: false,
  }),
  useCurrentUser: () => ({
    data: null,
    isLoading: false,
  }),
  useAuthenticatedImage: () => null,
  clearAuthToken: vi.fn(),
}));

// Mock AI context
vi.mock('../features/ai/AIContext', () => ({
  useAI: () => ({
    enabled: true,
    setEnabled: vi.fn(),
    defaultAgent: null,
    agents: [],
    isLoading: false,
    refreshAgents: vi.fn(),
  }),
}));

function renderNavbar() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <Navbar />
    </QueryClientProvider>,
  );
}

describe('Navbar', () => {
  beforeEach(() => {
    mockUseCreateCampaignPlan.mockReturnValue({
      mutate: mockMutate,
      isPending: false,
    });
    vi.clearAllMocks();
  });

  it('should render the navbar', () => {
    renderNavbar();
    expect(screen.getByRole('navigation')).toBeInTheDocument();
  });

  it('should render the logo link to home', () => {
    renderNavbar();
    const logoLink = screen.getAllByTestId('nav-link')[0];
    expect(logoLink).toHaveAttribute('href', '/');
  });

  it('should render My Campaign Plans link', () => {
    renderNavbar();
    expect(screen.getByText('My Campaign Plans')).toBeInTheDocument();
  });

  it('should render New Campaign button', () => {
    renderNavbar();
    expect(
      screen.getByRole('button', { name: 'New Campaign' }),
    ).toBeInTheDocument();
  });

  it('should render notifications button', () => {
    renderNavbar();
    expect(
      screen.getByRole('button', { name: 'View notifications' }),
    ).toBeInTheDocument();
  });

  it('should render user menu button', () => {
    renderNavbar();
    expect(
      screen.getByRole('button', { name: 'Open user menu' }),
    ).toBeInTheDocument();
  });

  it('should call create mutation when New Campaign is clicked', () => {
    renderNavbar();

    fireEvent.click(screen.getByRole('button', { name: 'New Campaign' }));

    expect(mockMutate).toHaveBeenCalledWith(
      {
        title: 'New Campaign',
        version: '0.0.1',
        setting: '',
        summary: '',
        storyline: [],
        storypoints: [],
        characters: [],
        locations: [],
        items: [],
        rules: [],
        objectives: [],
      },
      expect.objectContaining({
        onSuccess: expect.any(Function),
        onError: expect.any(Function),
      }),
    );
  });

  it('should show Creating... when mutation is pending', () => {
    mockUseCreateCampaignPlan.mockReturnValue({
      mutate: mockMutate,
      isPending: true,
    });

    renderNavbar();
    expect(
      screen.getByRole('button', { name: 'Creating...' }),
    ).toBeInTheDocument();
  });

  it('should disable button when mutation is pending', () => {
    mockUseCreateCampaignPlan.mockReturnValue({
      mutate: mockMutate,
      isPending: true,
    });

    renderNavbar();
    expect(screen.getByRole('button', { name: 'Creating...' })).toBeDisabled();
  });

  it('should navigate to new campaign on success', () => {
    renderNavbar();

    fireEvent.click(screen.getByRole('button', { name: 'New Campaign' }));

    // Get the onSuccess callback that was passed to mutate
    const mutateCallArgs = mockMutate.mock.calls[0];
    const callbacks = mutateCallArgs[1];

    // Simulate successful creation
    callbacks.onSuccess({ obj_id: { prefix: 'CampPlan', numeric: 123 } });

    expect(mockNavigate).toHaveBeenCalledWith({ to: '/campaign/plan/123' });
  });

  it('should show alert and invalidate on error', () => {
    const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {});

    renderNavbar();

    fireEvent.click(screen.getByRole('button', { name: 'New Campaign' }));

    // Get the onError callback that was passed to mutate
    const mutateCallArgs = mockMutate.mock.calls[0];
    const callbacks = mutateCallArgs[1];

    // Simulate error
    callbacks.onError(new Error('Failed to create'));

    expect(alertSpy).toHaveBeenCalledWith(
      'Failed to create campaign: Failed to create',
    );
    expect(mockInvalidate).toHaveBeenCalled();

    alertSpy.mockRestore();
  });

  it('should render mobile menu button', () => {
    renderNavbar();
    expect(
      screen.getByRole('button', { name: 'Open main menu' }),
    ).toBeInTheDocument();
  });
});
