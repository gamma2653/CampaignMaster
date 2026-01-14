import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { CampaignCard } from '../features/planning/components/CampaignCard';
import type { CampaignPlan, CampaignID } from '../schemas';

// Mock TanStack Router
vi.mock('@tanstack/react-router', () => ({
  Link: ({ children, to, params, className }: { children: React.ReactNode; to: string; params?: Record<string, string>; className?: string }) => (
    <a href={to.replace('$camp_id', params?.camp_id || '')} className={className} data-testid="edit-link">
      {children}
    </a>
  ),
}));

const mockCampaign: CampaignPlan = {
  obj_id: { prefix: 'CampPlan', numeric: 42 },
  title: 'Test Campaign',
  version: '1.0.0',
  setting: 'Fantasy',
  summary: 'This is a test campaign for unit testing purposes.',
  storyline: [],
  storypoints: [
    { obj_id: { prefix: 'P', numeric: 1 }, name: 'Point 1', description: 'Desc', objective: null },
    { obj_id: { prefix: 'P', numeric: 2 }, name: 'Point 2', description: 'Desc', objective: null },
  ],
  characters: [
    { obj_id: { prefix: 'C', numeric: 1 }, name: 'Hero', role: 'PC', backstory: '', attributes: {}, skills: {}, storylines: [], inventory: [] },
  ],
  locations: [
    { obj_id: { prefix: 'L', numeric: 1 }, name: 'Village', description: 'A village', neighboring_locations: [] },
    { obj_id: { prefix: 'L', numeric: 2 }, name: 'Forest', description: 'A forest', neighboring_locations: [] },
  ],
  items: [],
  rules: [
    { obj_id: { prefix: 'R', numeric: 1 }, description: 'Rule 1', effect: '', components: [] },
  ],
  objectives: [],
};

describe('CampaignCard', () => {
  let mockOnDelete: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    mockOnDelete = vi.fn();
    vi.clearAllMocks();
  });

  it('should render campaign title', () => {
    render(<CampaignCard campaign={mockCampaign} onDelete={mockOnDelete} />);
    expect(screen.getByText('Test Campaign')).toBeInTheDocument();
  });

  it('should render campaign version', () => {
    render(<CampaignCard campaign={mockCampaign} onDelete={mockOnDelete} />);
    expect(screen.getByText('v1.0.0')).toBeInTheDocument();
  });

  it('should render campaign summary', () => {
    render(<CampaignCard campaign={mockCampaign} onDelete={mockOnDelete} />);
    expect(screen.getByText('This is a test campaign for unit testing purposes.')).toBeInTheDocument();
  });

  it('should truncate long summaries', () => {
    const longSummaryCampaign = {
      ...mockCampaign,
      summary: 'A'.repeat(150),
    };
    render(<CampaignCard campaign={longSummaryCampaign} onDelete={mockOnDelete} />);
    const truncated = screen.getByText(/^A+\.\.\.$/);
    expect(truncated.textContent?.length).toBeLessThan(150);
  });

  it('should display entity counts', () => {
    render(<CampaignCard campaign={mockCampaign} onDelete={mockOnDelete} />);
    expect(screen.getByText('Characters: 1')).toBeInTheDocument();
    expect(screen.getByText('Locations: 2')).toBeInTheDocument();
    expect(screen.getByText('Items: 0')).toBeInTheDocument();
    expect(screen.getByText('Rules: 1')).toBeInTheDocument();
    expect(screen.getByText('Objectives: 0')).toBeInTheDocument();
    expect(screen.getByText('Arcs: 0')).toBeInTheDocument();
    expect(screen.getByText('Points: 2')).toBeInTheDocument();
  });

  it('should render Edit link with correct URL', () => {
    render(<CampaignCard campaign={mockCampaign} onDelete={mockOnDelete} />);
    const editLink = screen.getByTestId('edit-link');
    expect(editLink).toHaveAttribute('href', '/campaign/plan/42');
    expect(editLink).toHaveTextContent('Edit');
  });

  it('should render Delete button', () => {
    render(<CampaignCard campaign={mockCampaign} onDelete={mockOnDelete} />);
    expect(screen.getByRole('button', { name: 'Delete' })).toBeInTheDocument();
  });

  it('should call onDelete when Delete is clicked and confirmed', () => {
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true);
    render(<CampaignCard campaign={mockCampaign} onDelete={mockOnDelete} />);

    fireEvent.click(screen.getByRole('button', { name: 'Delete' }));

    expect(confirmSpy).toHaveBeenCalledWith('Are you sure you want to delete "Test Campaign"?');
    expect(mockOnDelete).toHaveBeenCalledWith({ prefix: 'CampPlan', numeric: 42 });

    confirmSpy.mockRestore();
  });

  it('should not call onDelete when Delete is cancelled', () => {
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(false);
    render(<CampaignCard campaign={mockCampaign} onDelete={mockOnDelete} />);

    fireEvent.click(screen.getByRole('button', { name: 'Delete' }));

    expect(confirmSpy).toHaveBeenCalled();
    expect(mockOnDelete).not.toHaveBeenCalled();

    confirmSpy.mockRestore();
  });

  it('should display "Untitled Campaign" when title is empty', () => {
    const untitledCampaign = { ...mockCampaign, title: '' };
    render(<CampaignCard campaign={untitledCampaign} onDelete={mockOnDelete} />);
    expect(screen.getByText('Untitled Campaign')).toBeInTheDocument();
  });

  it('should display "No summary provided" when summary is empty', () => {
    const noSummaryCampaign = { ...mockCampaign, summary: '' };
    render(<CampaignCard campaign={noSummaryCampaign} onDelete={mockOnDelete} />);
    expect(screen.getByText('No summary provided')).toBeInTheDocument();
  });
});
