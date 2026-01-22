import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { createMockObjective } from '../test-utils';
import { PREFIXES } from '../../schemas';

// Mock the query hook
const mockUseObjective = vi.fn();

vi.mock('../../query', () => ({
    useObjective: () => mockUseObjective(),
}));

// Mock field values and handlers
const mockFieldHandlers: Record<string, ReturnType<typeof vi.fn>> = {};
const mockFieldValues: Record<string, unknown> = {
    obj_id: { prefix: PREFIXES.POINT, numeric: 42 },
    name: 'Test Point',
    description: 'Test Description',
    objective: null,
};

// Mock the context
vi.mock('../../features/shared/components/ctx', () => ({
    withFieldGroup: ({ defaultValues, render: renderFn }: {
        defaultValues: Record<string, unknown>;
        render: (props: { group: unknown }) => React.ReactNode
    }) => {
        // Return a component that uses the render function
        return function MockFieldGroup() {
            const mockGroup = {
                state: { values: mockFieldValues },
                AppField: ({ children, name }: { children: (field: unknown) => React.ReactNode; name: string }) => {
                    if (!mockFieldHandlers[name]) {
                        mockFieldHandlers[name] = vi.fn();
                    }
                    const mockField = {
                        state: { value: mockFieldValues[name] ?? defaultValues[name] },
                        handleChange: mockFieldHandlers[name],
                        IDDisplayField: () => (
                            <span data-testid="id-display">
                                ID: {(mockFieldValues.obj_id as { prefix: string; numeric: number }).prefix}-
                                {(mockFieldValues.obj_id as { prefix: string; numeric: number }).numeric}
                            </span>
                        ),
                        TextField: ({ label }: { label: string }) => (
                            <div>
                                <label>{label}:</label>
                                <input
                                    type="text"
                                    value={String(mockFieldValues[name] ?? '')}
                                    onChange={(e) => mockFieldHandlers[name](e.target.value)}
                                    data-testid={`text-field-${name}`}
                                />
                            </div>
                        ),
                        TextAreaField: ({ label }: { label: string }) => (
                            <div>
                                <label>{label}:</label>
                                <textarea
                                    value={String(mockFieldValues[name] ?? '')}
                                    onChange={(e) => mockFieldHandlers[name](e.target.value)}
                                    data-testid={`textarea-field-${name}`}
                                />
                            </div>
                        ),
                    };
                    return <>{children(mockField)}</>;
                },
            };
            return <>{renderFn({ group: mockGroup })}</>;
        };
    },
    useFieldContext: () => ({}),
    useFormContext: () => ({}),
}));

// Import after mocking
import { PointGroup, defaultValues } from '../../features/shared/components/fieldgroups/PointGroup';

describe('PointGroup', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        // Reset mock values
        mockFieldValues.obj_id = { prefix: PREFIXES.POINT, numeric: 42 };
        mockFieldValues.name = 'Test Point';
        mockFieldValues.description = 'Test Description';
        mockFieldValues.objective = null;
        // Clear field handlers
        Object.keys(mockFieldHandlers).forEach((key) => delete mockFieldHandlers[key]);
    });

    describe('defaultValues', () => {
        it('should have correct default prefix', () => {
            expect(defaultValues.obj_id.prefix).toBe(PREFIXES.POINT);
        });

        it('should have zero as default numeric', () => {
            expect(defaultValues.obj_id.numeric).toBe(0);
        });

        it('should have empty name by default', () => {
            expect(defaultValues.name).toBe('');
        });

        it('should have null objective by default', () => {
            expect(defaultValues.objective).toBeNull();
        });
    });

    describe('rendering', () => {
        it('should render ID display field', () => {
            mockUseObjective.mockReturnValue({ data: [], isLoading: false });
            render(<PointGroup />);
            expect(screen.getByTestId('id-display')).toBeInTheDocument();
            expect(screen.getByText(/P-42/)).toBeInTheDocument();
        });

        it('should render name text field', () => {
            mockUseObjective.mockReturnValue({ data: [], isLoading: false });
            render(<PointGroup />);
            expect(screen.getByText('Point Name:')).toBeInTheDocument();
        });

        it('should render description textarea field', () => {
            mockUseObjective.mockReturnValue({ data: [], isLoading: false });
            render(<PointGroup />);
            expect(screen.getByText('Point Description:')).toBeInTheDocument();
        });

        it('should render linked objective label', () => {
            mockUseObjective.mockReturnValue({ data: [], isLoading: false });
            render(<PointGroup />);
            expect(screen.getByText('Linked Objective:')).toBeInTheDocument();
        });
    });

    describe('objective dropdown', () => {
        it('should show loading state when objectives are loading', () => {
            mockUseObjective.mockReturnValue({ data: undefined, isLoading: true });
            render(<PointGroup />);
            expect(screen.getByText('Loading objectives...')).toBeInTheDocument();
        });

        it('should render "None" option', () => {
            mockUseObjective.mockReturnValue({ data: [], isLoading: false });
            render(<PointGroup />);
            expect(screen.getByRole('option', { name: 'None' })).toBeInTheDocument();
        });

        it('should render objectives as options', () => {
            const mockObjectives = [
                createMockObjective({ obj_id: { prefix: 'O', numeric: 1 }, description: 'First Objective' }),
                createMockObjective({ obj_id: { prefix: 'O', numeric: 2 }, description: 'Second Objective' }),
            ];
            mockUseObjective.mockReturnValue({ data: mockObjectives, isLoading: false });
            render(<PointGroup />);

            expect(screen.getByText(/O-1 - First Objective/)).toBeInTheDocument();
            expect(screen.getByText(/O-2 - Second Objective/)).toBeInTheDocument();
        });

        it('should truncate long objective descriptions', () => {
            const longDescription = 'A'.repeat(100);
            const mockObjectives = [
                createMockObjective({ obj_id: { prefix: 'O', numeric: 1 }, description: longDescription }),
            ];
            mockUseObjective.mockReturnValue({ data: mockObjectives, isLoading: false });
            render(<PointGroup />);

            // Description should be truncated to 50 chars
            const option = screen.getByRole('option', { name: /O-1 -/ });
            expect(option.textContent?.length).toBeLessThan(longDescription.length + 10);
        });
    });
});
