/**
 * Tests for sequential ID creation behavior in React mutation hooks.
 *
 * These tests verify that the React frontend correctly handles sequential IDs
 * returned by the API when creating CampaignPlan components. The API generates
 * IDs sequentially (1, 2, 3, etc.) for each resource type, and the frontend
 * should correctly receive and display these IDs.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import {
  createMockPoint,
  createMockPointID,
  createMockCharacter,
  createMockCharacterID,
  createMockRule,
  createMockRuleID,
  createMockItem,
  createMockItemID,
  createMockLocation,
  createMockLocationID,
  createMockObjective,
  createMockObjectiveID,
  createMockArc,
  createMockArcID,
  createMockSegment,
  createMockSegmentID,
  createMockCampaign,
  createMockCampaignID,
} from './test-utils';
import { PREFIXES } from '../schemas';

// Create a wrapper with QueryClientProvider for testing hooks
function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
      mutations: {
        retry: false,
      },
    },
  });
  return function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );
  };
}

// Mock fetch globally
const mockFetch = vi.fn();
global.fetch = mockFetch;

// Import hooks after setting up mocks
import {
  useCreatePoint,
  useCreateCharacter,
  useCreateRule,
  useCreateItem,
  useCreateLocation,
  useCreateObjective,
  useCreateArc,
  useCreateSegment,
  useCreateCampaignPlan,
} from '../query';

describe('Sequential ID Creation - Mutation Hooks', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  describe('useCreatePoint', () => {
    it('should receive sequential IDs starting from 1', async () => {
      // Simulate server returning sequential IDs
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: () =>
            Promise.resolve(createMockPoint({ obj_id: createMockPointID(1) })),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () =>
            Promise.resolve(createMockPoint({ obj_id: createMockPointID(2) })),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () =>
            Promise.resolve(createMockPoint({ obj_id: createMockPointID(3) })),
        });

      const { result } = renderHook(() => useCreatePoint(), {
        wrapper: createWrapper(),
      });

      // Create first point
      const createData = {
        name: 'Test Point',
        description: 'Test',
        objective: null,
      };

      // First creation - should get ID 1
      result.current.mutate(createData);
      await waitFor(() => expect(result.current.isSuccess).toBe(true));
      expect(result.current.data?.obj_id.numeric).toBe(1);
      expect(result.current.data?.obj_id.prefix).toBe(PREFIXES.POINT);
    });

    it('should correctly parse Point ID from API response', async () => {
      const expectedPoint = createMockPoint({
        obj_id: { prefix: PREFIXES.POINT, numeric: 42 },
        name: 'Test Point',
      });

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(expectedPoint),
      });

      const { result } = renderHook(() => useCreatePoint(), {
        wrapper: createWrapper(),
      });

      result.current.mutate({
        name: 'Test Point',
        description: '',
        objective: null,
      });
      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      expect(result.current.data?.obj_id).toEqual({ prefix: 'P', numeric: 42 });
    });
  });

  describe('useCreateCharacter', () => {
    it('should receive sequential IDs starting from 1', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () =>
          Promise.resolve(
            createMockCharacter({ obj_id: createMockCharacterID(1) }),
          ),
      });

      const { result } = renderHook(() => useCreateCharacter(), {
        wrapper: createWrapper(),
      });

      result.current.mutate({
        name: 'Test Character',
        role: 'NPC',
        backstory: '',
        attributes: {},
        skills: {},
        storylines: [],
        inventory: [],
      });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));
      expect(result.current.data?.obj_id.numeric).toBe(1);
      expect(result.current.data?.obj_id.prefix).toBe(PREFIXES.CHARACTER);
    });
  });

  describe('useCreateRule', () => {
    it('should receive sequential IDs starting from 1', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () =>
          Promise.resolve(createMockRule({ obj_id: createMockRuleID(1) })),
      });

      const { result } = renderHook(() => useCreateRule(), {
        wrapper: createWrapper(),
      });

      result.current.mutate({
        description: 'Test Rule',
        effect: '',
        components: [],
      });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));
      expect(result.current.data?.obj_id.numeric).toBe(1);
      expect(result.current.data?.obj_id.prefix).toBe(PREFIXES.RULE);
    });
  });

  describe('useCreateItem', () => {
    it('should receive sequential IDs starting from 1', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () =>
          Promise.resolve(createMockItem({ obj_id: createMockItemID(1) })),
      });

      const { result } = renderHook(() => useCreateItem(), {
        wrapper: createWrapper(),
      });

      result.current.mutate({
        name: 'Test Item',
        type_: 'weapon',
        description: '',
        properties: {},
      });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));
      expect(result.current.data?.obj_id.numeric).toBe(1);
      expect(result.current.data?.obj_id.prefix).toBe(PREFIXES.ITEM);
    });
  });

  describe('useCreateLocation', () => {
    it('should receive sequential IDs starting from 1', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () =>
          Promise.resolve(
            createMockLocation({ obj_id: createMockLocationID(1) }),
          ),
      });

      const { result } = renderHook(() => useCreateLocation(), {
        wrapper: createWrapper(),
      });

      result.current.mutate({
        name: 'Test Location',
        description: '',
        neighboring_locations: [],
        coords: null,
      });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));
      expect(result.current.data?.obj_id.numeric).toBe(1);
      expect(result.current.data?.obj_id.prefix).toBe(PREFIXES.LOCATION);
    });
  });

  describe('useCreateObjective', () => {
    it('should receive sequential IDs starting from 1', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () =>
          Promise.resolve(
            createMockObjective({ obj_id: createMockObjectiveID(1) }),
          ),
      });

      const { result } = renderHook(() => useCreateObjective(), {
        wrapper: createWrapper(),
      });

      result.current.mutate({
        description: 'Test Objective',
        components: [],
        prerequisites: [],
      });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));
      expect(result.current.data?.obj_id.numeric).toBe(1);
      expect(result.current.data?.obj_id.prefix).toBe(PREFIXES.OBJECTIVE);
    });
  });

  describe('useCreateArc', () => {
    it('should receive sequential IDs starting from 1', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () =>
          Promise.resolve(createMockArc({ obj_id: createMockArcID(1) })),
      });

      const { result } = renderHook(() => useCreateArc(), {
        wrapper: createWrapper(),
      });

      result.current.mutate({
        name: 'Test Arc',
        description: '',
        segments: [],
      });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));
      expect(result.current.data?.obj_id.numeric).toBe(1);
      expect(result.current.data?.obj_id.prefix).toBe(PREFIXES.ARC);
    });
  });

  describe('useCreateSegment', () => {
    it('should receive sequential IDs starting from 1', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () =>
          Promise.resolve(
            createMockSegment({ obj_id: createMockSegmentID(1) }),
          ),
      });

      const { result } = renderHook(() => useCreateSegment(), {
        wrapper: createWrapper(),
      });

      result.current.mutate({
        name: 'Test Segment',
        description: '',
        start: { prefix: 'P', numeric: 1 },
        end: { prefix: 'P', numeric: 2 },
      });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));
      expect(result.current.data?.obj_id.numeric).toBe(1);
      expect(result.current.data?.obj_id.prefix).toBe(PREFIXES.SEGMENT);
    });
  });

  describe('useCreateCampaignPlan', () => {
    it('should receive sequential IDs starting from 1', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () =>
          Promise.resolve(
            createMockCampaign({ obj_id: createMockCampaignID(1) }),
          ),
      });

      const { result } = renderHook(() => useCreateCampaignPlan(), {
        wrapper: createWrapper(),
      });

      result.current.mutate({
        title: 'Test Campaign',
        version: '1.0',
        setting: 'Fantasy',
        summary: '',
        storyline: [],
        storypoints: [],
        characters: [],
        locations: [],
        items: [],
        rules: [],
        objectives: [],
      });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));
      expect(result.current.data?.obj_id.numeric).toBe(1);
      expect(result.current.data?.obj_id.prefix).toBe(PREFIXES.CAMPAIGN_PLAN);
    });
  });
});

describe('Sequential ID Creation - Multiple Resources Simulation', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  it('should correctly handle multiple Points with sequential IDs in listing', async () => {
    // Simulate API returning a list with sequential IDs
    const mockPoints = [
      createMockPoint({ obj_id: createMockPointID(1), name: 'Point 1' }),
      createMockPoint({ obj_id: createMockPointID(2), name: 'Point 2' }),
      createMockPoint({ obj_id: createMockPointID(3), name: 'Point 3' }),
    ];

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockPoints),
    });

    // Import usePoint for listing
    const { usePoint } = await import('../query');

    const { result } = renderHook(() => usePoint(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toHaveLength(3);
    expect(result.current.data?.[0].obj_id.numeric).toBe(1);
    expect(result.current.data?.[1].obj_id.numeric).toBe(2);
    expect(result.current.data?.[2].obj_id.numeric).toBe(3);
  });

  it('should maintain correct ID structure after create mutation', async () => {
    // First call: create returns new resource with ID
    const createdPoint = createMockPoint({
      obj_id: { prefix: PREFIXES.POINT, numeric: 1 },
      name: 'New Point',
    });

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(createdPoint),
    });

    const { result } = renderHook(() => useCreatePoint(), {
      wrapper: createWrapper(),
    });

    result.current.mutate({
      name: 'New Point',
      description: '',
      objective: null,
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    // Verify the ID structure is preserved
    expect(result.current.data?.obj_id).toMatchObject({
      prefix: 'P',
      numeric: 1,
    });

    // Verify fetch was called with correct endpoint
    expect(mockFetch).toHaveBeenCalledWith(
      '/api/campaign/p',
      expect.objectContaining({
        method: 'POST',
      }),
    );
  });
});

describe('Sequential ID Display Format', () => {
  /**
   * These tests verify that the ID format matches what users expect to see.
   * IDs are displayed as PREFIX-NUMERIC (e.g., P-000001).
   */

  it('should have consistent prefix for Point IDs', () => {
    const pointId = createMockPointID(1);
    expect(pointId.prefix).toBe('P');
  });

  it('should have consistent prefix for Character IDs', () => {
    const characterId = createMockCharacterID(1);
    expect(characterId.prefix).toBe('C');
  });

  it('should have consistent prefix for Rule IDs', () => {
    const ruleId = createMockRuleID(1);
    expect(ruleId.prefix).toBe('R');
  });

  it('should have consistent prefix for Item IDs', () => {
    const itemId = createMockItemID(1);
    expect(itemId.prefix).toBe('I');
  });

  it('should have consistent prefix for Location IDs', () => {
    const locationId = createMockLocationID(1);
    expect(locationId.prefix).toBe('L');
  });

  it('should have consistent prefix for Objective IDs', () => {
    const objectiveId = createMockObjectiveID(1);
    expect(objectiveId.prefix).toBe('O');
  });

  it('should have consistent prefix for Arc IDs', () => {
    const arcId = createMockArcID(1);
    expect(arcId.prefix).toBe('A');
  });

  it('should have consistent prefix for Segment IDs', () => {
    const segmentId = createMockSegmentID(1);
    expect(segmentId.prefix).toBe('S');
  });

  it('should have consistent prefix for CampaignPlan IDs', () => {
    const campaignId = createMockCampaignID(1);
    expect(campaignId.prefix).toBe('CampPlan');
  });
});

describe('ID Sequence Independence', () => {
  /**
   * These tests verify that different resource types have independent ID sequences.
   * Creating a Point with ID 1 should not affect Character IDs.
   */

  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  it('should show different resource types can have same numeric ID', async () => {
    // Both Point and Character can have numeric ID 1
    const point = createMockPoint({ obj_id: createMockPointID(1) });
    const character = createMockCharacter({ obj_id: createMockCharacterID(1) });

    // Mock responses for creating both
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(point),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(character),
      });

    const { result: pointResult } = renderHook(() => useCreatePoint(), {
      wrapper: createWrapper(),
    });

    const { result: characterResult } = renderHook(() => useCreateCharacter(), {
      wrapper: createWrapper(),
    });

    // Create Point
    pointResult.current.mutate({
      name: 'Point',
      description: '',
      objective: null,
    });
    await waitFor(() => expect(pointResult.current.isSuccess).toBe(true));

    // Create Character
    characterResult.current.mutate({
      name: 'Character',
      role: 'NPC',
      backstory: '',
      attributes: {},
      skills: {},
      storylines: [],
      inventory: [],
    });
    await waitFor(() => expect(characterResult.current.isSuccess).toBe(true));

    // Both should have numeric 1 but different prefixes
    expect(pointResult.current.data?.obj_id.numeric).toBe(1);
    expect(pointResult.current.data?.obj_id.prefix).toBe('P');

    expect(characterResult.current.data?.obj_id.numeric).toBe(1);
    expect(characterResult.current.data?.obj_id.prefix).toBe('C');
  });
});
