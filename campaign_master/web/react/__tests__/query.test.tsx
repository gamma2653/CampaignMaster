import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import {
    createMockCampaign,
    createMockRule,
    createMockObjective,
    createMockPoint,
    createMockCharacter,
    createMockLocation,
    createMockItem,
} from './test-utils';
import { PREFIXES } from '../schemas';

// Create a wrapper with QueryClientProvider for testing hooks
function createWrapper() {
    const queryClient = new QueryClient({
        defaultOptions: {
            queries: {
                retry: false,
            },
        },
    });
    return function Wrapper({ children }: { children: React.ReactNode }) {
        return (
            <QueryClientProvider client={queryClient}>
                {children}
            </QueryClientProvider>
        );
    };
}

// Mock fetch globally
const mockFetch = vi.fn();
global.fetch = mockFetch;

// Import hooks after setting up mocks
import {
    useCampaignPlan,
    useCampaignPlanByID,
    useRule,
    useObjective,
    usePoint,
    useCharacter,
    useLocation,
    useItem,
    useCreateCampaignPlan,
    useUpdateCampaignPlan,
    useDeleteCampaignPlan,
} from '../query';

describe('Query Hooks', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    afterEach(() => {
        vi.resetAllMocks();
    });

    describe('useCampaignPlan', () => {
        it('should fetch campaigns from correct endpoint', async () => {
            const mockCampaigns = [createMockCampaign(), createMockCampaign({ obj_id: { prefix: 'CampPlan', numeric: 2 } })];
            mockFetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(mockCampaigns),
            });

            const { result } = renderHook(() => useCampaignPlan(), {
                wrapper: createWrapper(),
            });

            await waitFor(() => expect(result.current.isSuccess).toBe(true));

            expect(mockFetch).toHaveBeenCalledWith('/api/campaign/campplan');
            expect(result.current.data).toEqual(mockCampaigns);
        });
    });

    describe('useCampaignPlanByID', () => {
        it('should fetch campaign by ID from correct endpoint', async () => {
            const mockCampaign = createMockCampaign({ obj_id: { prefix: 'CampPlan', numeric: 42 } });
            mockFetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(mockCampaign),
            });

            const { result } = renderHook(
                () => useCampaignPlanByID({ prefix: PREFIXES.CAMPAIGN_PLAN, numeric: 42 }),
                { wrapper: createWrapper() }
            );

            await waitFor(() => expect(result.current.isSuccess).toBe(true));

            expect(mockFetch).toHaveBeenCalledWith('/api/campaign/campplan/42');
            expect(result.current.data).toEqual(mockCampaign);
        });
    });

    describe('useRule', () => {
        it('should fetch rules from correct endpoint', async () => {
            const mockRules = [createMockRule(), createMockRule({ obj_id: { prefix: 'R', numeric: 2 } })];
            mockFetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(mockRules),
            });

            const { result } = renderHook(() => useRule(), {
                wrapper: createWrapper(),
            });

            await waitFor(() => expect(result.current.isSuccess).toBe(true));

            expect(mockFetch).toHaveBeenCalledWith('/api/campaign/r');
            expect(result.current.data).toEqual(mockRules);
        });
    });

    describe('useObjective', () => {
        it('should fetch objectives from correct endpoint', async () => {
            const mockObjectives = [createMockObjective()];
            mockFetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(mockObjectives),
            });

            const { result } = renderHook(() => useObjective(), {
                wrapper: createWrapper(),
            });

            await waitFor(() => expect(result.current.isSuccess).toBe(true));

            expect(mockFetch).toHaveBeenCalledWith('/api/campaign/o');
        });
    });

    describe('usePoint', () => {
        it('should fetch points from correct endpoint', async () => {
            const mockPoints = [createMockPoint()];
            mockFetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(mockPoints),
            });

            const { result } = renderHook(() => usePoint(), {
                wrapper: createWrapper(),
            });

            await waitFor(() => expect(result.current.isSuccess).toBe(true));

            expect(mockFetch).toHaveBeenCalledWith('/api/campaign/p');
        });
    });

    describe('useCharacter', () => {
        it('should fetch characters from correct endpoint', async () => {
            const mockCharacters = [createMockCharacter()];
            mockFetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(mockCharacters),
            });

            const { result } = renderHook(() => useCharacter(), {
                wrapper: createWrapper(),
            });

            await waitFor(() => expect(result.current.isSuccess).toBe(true));

            expect(mockFetch).toHaveBeenCalledWith('/api/campaign/c');
        });
    });

    describe('useLocation', () => {
        it('should fetch locations from correct endpoint', async () => {
            const mockLocations = [createMockLocation()];
            mockFetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(mockLocations),
            });

            const { result } = renderHook(() => useLocation(), {
                wrapper: createWrapper(),
            });

            await waitFor(() => expect(result.current.isSuccess).toBe(true));

            expect(mockFetch).toHaveBeenCalledWith('/api/campaign/l');
        });
    });

    describe('useItem', () => {
        it('should fetch items from correct endpoint', async () => {
            const mockItems = [createMockItem()];
            mockFetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(mockItems),
            });

            const { result } = renderHook(() => useItem(), {
                wrapper: createWrapper(),
            });

            await waitFor(() => expect(result.current.isSuccess).toBe(true));

            expect(mockFetch).toHaveBeenCalledWith('/api/campaign/i');
        });
    });
});

describe('Mutation Hooks', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    afterEach(() => {
        vi.resetAllMocks();
    });

    describe('useCreateCampaignPlan', () => {
        it('should POST to correct endpoint', async () => {
            const newCampaign = {
                title: 'New Campaign',
                version: '1.0.0',
                setting: 'Fantasy',
                summary: 'A new adventure',
                storyline: [],
                storypoints: [],
                characters: [],
                locations: [],
                items: [],
                rules: [],
                objectives: [],
            };
            const createdCampaign = createMockCampaign({ ...newCampaign });

            mockFetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(createdCampaign),
            });

            const { result } = renderHook(() => useCreateCampaignPlan(), {
                wrapper: createWrapper(),
            });

            result.current.mutate(newCampaign);

            await waitFor(() => expect(result.current.isSuccess).toBe(true));

            expect(mockFetch).toHaveBeenCalledWith(
                '/api/campaign/campplan',
                expect.objectContaining({
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(newCampaign),
                })
            );
        });

        it('should throw error when create fails', async () => {
            mockFetch.mockResolvedValueOnce({
                ok: false,
            });

            const { result } = renderHook(() => useCreateCampaignPlan(), {
                wrapper: createWrapper(),
            });

            result.current.mutate({
                title: 'Test',
                version: '1.0',
                setting: '',
                summary: '',
                storyline: [],
                storypoints: [],
                characters: [],
                locations: [],
                items: [],
                rules: [],
                objectives: [],
            });

            await waitFor(() => expect(result.current.isError).toBe(true));
            expect(result.current.error?.message).toBe('Create failed');
        });
    });

    describe('useUpdateCampaignPlan', () => {
        it('should PUT to correct endpoint with ID', async () => {
            const updatedCampaign = createMockCampaign({
                obj_id: { prefix: 'CampPlan', numeric: 42 },
                title: 'Updated Campaign',
            });

            mockFetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(updatedCampaign),
            });

            const { result } = renderHook(() => useUpdateCampaignPlan(), {
                wrapper: createWrapper(),
            });

            result.current.mutate(updatedCampaign);

            await waitFor(() => expect(result.current.isSuccess).toBe(true));

            expect(mockFetch).toHaveBeenCalledWith(
                '/api/campaign/campplan/42',
                expect.objectContaining({
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(updatedCampaign),
                })
            );
        });

        it('should throw error when update fails', async () => {
            mockFetch.mockResolvedValueOnce({
                ok: false,
            });

            const { result } = renderHook(() => useUpdateCampaignPlan(), {
                wrapper: createWrapper(),
            });

            result.current.mutate(createMockCampaign());

            await waitFor(() => expect(result.current.isError).toBe(true));
            expect(result.current.error?.message).toBe('Update failed');
        });
    });

    describe('useDeleteCampaignPlan', () => {
        it('should DELETE to correct endpoint with ID', async () => {
            mockFetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve({ success: true }),
            });

            const { result } = renderHook(() => useDeleteCampaignPlan(), {
                wrapper: createWrapper(),
            });

            result.current.mutate({ prefix: PREFIXES.CAMPAIGN_PLAN, numeric: 42 });

            await waitFor(() => expect(result.current.isSuccess).toBe(true));

            expect(mockFetch).toHaveBeenCalledWith(
                '/api/campaign/campplan/42',
                expect.objectContaining({
                    method: 'DELETE',
                })
            );
        });

        it('should throw error when delete fails', async () => {
            mockFetch.mockResolvedValueOnce({
                ok: false,
            });

            const { result } = renderHook(() => useDeleteCampaignPlan(), {
                wrapper: createWrapper(),
            });

            result.current.mutate({ prefix: PREFIXES.CAMPAIGN_PLAN, numeric: 1 });

            await waitFor(() => expect(result.current.isError).toBe(true));
            expect(result.current.error?.message).toBe('Delete failed');
        });
    });
});
