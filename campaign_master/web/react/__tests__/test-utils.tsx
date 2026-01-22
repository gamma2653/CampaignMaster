import React from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import type {
    CampaignPlan, Point, Character, Location, Item, Rule, Objective, Arc, Segment,
    CampaignID, PointID, CharacterID, LocationID, ItemID, RuleID, ObjectiveID, ArcID, SegmentID,
} from '../schemas';
import { PREFIXES } from '../schemas';

// Create a fresh QueryClient for each test
export function createTestQueryClient() {
    return new QueryClient({
        defaultOptions: {
            queries: {
                retry: false,
            },
        },
    });
}

// Custom render function that wraps components with QueryClientProvider
interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
    queryClient?: QueryClient;
}

export function renderWithProviders(
    ui: React.ReactElement,
    { queryClient = createTestQueryClient(), ...options }: CustomRenderOptions = {}
) {
    function Wrapper({ children }: { children: React.ReactNode }) {
        return (
            <QueryClientProvider client={queryClient}>
                {children}
            </QueryClientProvider>
        );
    }

    return {
        ...render(ui, { wrapper: Wrapper, ...options }),
        queryClient,
    };
}

// ============================================
// Mock Data Factories
// ============================================

// ID Factories
export function createMockCampaignID(numeric: number = 1): CampaignID {
    return { prefix: PREFIXES.CAMPAIGN_PLAN, numeric };
}

export function createMockPointID(numeric: number = 1): PointID {
    return { prefix: PREFIXES.POINT, numeric };
}

export function createMockCharacterID(numeric: number = 1): CharacterID {
    return { prefix: PREFIXES.CHARACTER, numeric };
}

export function createMockLocationID(numeric: number = 1): LocationID {
    return { prefix: PREFIXES.LOCATION, numeric };
}

export function createMockItemID(numeric: number = 1): ItemID {
    return { prefix: PREFIXES.ITEM, numeric };
}

export function createMockRuleID(numeric: number = 1): RuleID {
    return { prefix: PREFIXES.RULE, numeric };
}

export function createMockObjectiveID(numeric: number = 1): ObjectiveID {
    return { prefix: PREFIXES.OBJECTIVE, numeric };
}

export function createMockArcID(numeric: number = 1): ArcID {
    return { prefix: PREFIXES.ARC, numeric };
}

export function createMockSegmentID(numeric: number = 1): SegmentID {
    return { prefix: PREFIXES.SEGMENT, numeric };
}

// Entity Factories
export function createMockPoint(overrides: Partial<Point> = {}): Point {
    return {
        obj_id: createMockPointID(1),
        name: 'Test Point',
        description: 'A test point description',
        objective: null,
        ...overrides,
    };
}

export function createMockObjective(overrides: Partial<Objective> = {}): Objective {
    return {
        obj_id: createMockObjectiveID(1),
        description: 'Test objective description',
        components: [],
        prerequisites: [],
        ...overrides,
    };
}

export function createMockRule(overrides: Partial<Rule> = {}): Rule {
    return {
        obj_id: createMockRuleID(1),
        description: 'Test rule description',
        effect: 'Test rule effect',
        components: [],
        ...overrides,
    };
}

export function createMockItem(overrides: Partial<Item> = {}): Item {
    return {
        obj_id: createMockItemID(1),
        name: 'Test Item',
        type_: 'Weapon',
        description: 'A test item description',
        properties: {},
        ...overrides,
    };
}

export function createMockLocation(overrides: Partial<Location> = {}): Location {
    return {
        obj_id: createMockLocationID(1),
        name: 'Test Location',
        description: 'A test location description',
        neighboring_locations: [],
        coords: [0, 0],
        ...overrides,
    };
}

export function createMockCharacter(overrides: Partial<Character> = {}): Character {
    return {
        obj_id: createMockCharacterID(1),
        name: 'Test Character',
        role: 'NPC',
        backstory: 'A mysterious character',
        attributes: {},
        skills: {},
        storylines: [],
        inventory: [],
        ...overrides,
    };
}

export function createMockSegment(overrides: Partial<Segment> = {}): Segment {
    return {
        obj_id: createMockSegmentID(1),
        name: 'Test Segment',
        description: 'A test segment description',
        start: createMockPointID(1),
        end: createMockPointID(2),
        ...overrides,
    };
}

export function createMockArc(overrides: Partial<Arc> = {}): Arc {
    return {
        obj_id: createMockArcID(1),
        name: 'Test Arc',
        description: 'A test arc description',
        segments: [],
        ...overrides,
    };
}

export function createMockCampaign(overrides: Partial<CampaignPlan> = {}): CampaignPlan {
    return {
        obj_id: createMockCampaignID(1),
        title: 'Test Campaign',
        version: '1.0.0',
        setting: 'Fantasy',
        summary: 'A test campaign summary',
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

// ============================================
// Mock Hook Results
// ============================================

export interface MockQueryResult<T> {
    data: T | undefined;
    isLoading: boolean;
    error: Error | null;
}

export interface MockMutationResult {
    mutate: ReturnType<typeof vi.fn>;
    isPending: boolean;
}

export function createMockQueryResult<T>(data: T): MockQueryResult<T> {
    return {
        data,
        isLoading: false,
        error: null,
    };
}

export function createMockLoadingQueryResult<T>(): MockQueryResult<T> {
    return {
        data: undefined,
        isLoading: true,
        error: null,
    };
}

export function createMockErrorQueryResult<T>(message: string): MockQueryResult<T> {
    return {
        data: undefined,
        isLoading: false,
        error: new Error(message),
    };
}

export function createMockMutationResult(isPending: boolean = false): MockMutationResult {
    return {
        mutate: vi.fn(),
        isPending,
    };
}

// ============================================
// Mock Field Context
// ============================================

export function createMockFieldState<T>(value: T) {
    return {
        state: { value },
        handleChange: vi.fn(),
    };
}

// ============================================
// Mock Form Context
// ============================================

export function createMockFormState<T extends Record<string, unknown>>(values: T) {
    return {
        state: { values, isSubmitting: false },
        handleSubmit: vi.fn(),
        Subscribe: ({ children, selector }: { children: (value: unknown) => React.ReactNode; selector?: (state: { isSubmitting: boolean }) => unknown }) => {
            // Simple mock that extracts the value from selector if provided
            if (selector) {
                const result = selector({ isSubmitting: false });
                return <>{children(result)}</>;
            }
            return <>{children(false)}</>;
        },
        AppField: ({ children, name }: { children: (field: unknown) => React.ReactNode; name: string }) => {
            // Return a mock field for testing
            return <>{children(createMockFieldState(values[name] ?? ''))}</>;
        },
    };
}

// ============================================
// Import vi from vitest for use in this module
// ============================================
import { vi } from 'vitest';

// Re-export everything from @testing-library/react for convenience
export * from '@testing-library/react';
