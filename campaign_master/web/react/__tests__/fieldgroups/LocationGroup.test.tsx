import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { PREFIXES } from '../../schemas';

// Mock field values and handlers
const mockFieldHandlers: Record<string, ReturnType<typeof vi.fn>> = {};
const mockFieldValues: Record<string, unknown> = {
    obj_id: { prefix: PREFIXES.LOCATION, numeric: 1 },
    name: 'Test Location',
    description: 'Test Location Description',
    coords: [10, 20],
};

// Mock the context
vi.mock('../../features/shared/components/ctx', () => ({
    withFieldGroup: ({ defaultValues, render: renderFn }: {
        defaultValues: Record<string, unknown>;
        render: (props: { group: unknown }) => React.ReactNode
    }) => {
        return function MockFieldGroup() {
            const mockGroup = {
                state: { values: mockFieldValues },
                AppField: ({ children, name }: { children: (field: unknown) => React.ReactNode; name: string }) => {
                    if (!mockFieldHandlers[name]) {
                        mockFieldHandlers[name] = vi.fn();
                    }

                    const getValue = () => {
                        // Handle nested array access like 'coords[0]'
                        if (name.includes('[')) {
                            const match = name.match(/(\w+)\[(\d+)\]/);
                            if (match) {
                                const [, arrayName, index] = match;
                                const arr = mockFieldValues[arrayName] as unknown[];
                                if (arr) {
                                    return arr[parseInt(index)];
                                }
                            }
                        }
                        return mockFieldValues[name] ?? defaultValues[name];
                    };

                    const mockField = {
                        state: { value: getValue() },
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
                                    value={String(getValue() ?? '')}
                                    onChange={(e) => mockFieldHandlers[name](e.target.value)}
                                    data-testid={`text-field-${name}`}
                                />
                            </div>
                        ),
                        TextAreaField: ({ label }: { label: string }) => (
                            <div>
                                <label>{label}:</label>
                                <textarea
                                    value={String(getValue() ?? '')}
                                    onChange={(e) => mockFieldHandlers[name](e.target.value)}
                                    data-testid={`textarea-field-${name}`}
                                />
                            </div>
                        ),
                        NumberField: ({ label }: { label: string }) => (
                            <div>
                                <label>{label}:</label>
                                <input
                                    type="number"
                                    value={Number(getValue() ?? 0)}
                                    onChange={(e) => mockFieldHandlers[name](Number(e.target.value))}
                                    data-testid={`number-field-${name}`}
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

// Mock ObjectIDGroup
vi.mock('../../features/shared/components/fieldgroups/ObjectIDGroup', () => ({
    ObjectIDGroup: () => <div>ObjectIDGroup Mock</div>,
}));

// Import after mocking
import { LocationGroup, defaultValues } from '../../features/shared/components/fieldgroups/LocationGroup';

describe('LocationGroup', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        mockFieldValues.obj_id = { prefix: PREFIXES.LOCATION, numeric: 1 };
        mockFieldValues.name = 'Test Location';
        mockFieldValues.description = 'Test Location Description';
        mockFieldValues.coords = [10, 20];
        Object.keys(mockFieldHandlers).forEach((key) => delete mockFieldHandlers[key]);
    });

    describe('defaultValues', () => {
        it('should have correct default prefix', () => {
            expect(defaultValues.obj_id.prefix).toBe(PREFIXES.LOCATION);
        });

        it('should have zero as default numeric', () => {
            expect(defaultValues.obj_id.numeric).toBe(0);
        });

        it('should have empty strings for text fields', () => {
            expect(defaultValues.name).toBe('');
            expect(defaultValues.description).toBe('');
        });

        it('should have default 2D coordinates', () => {
            expect(defaultValues.coords).toEqual([0, 0]);
        });
    });

    describe('rendering', () => {
        it('should render ID display field', () => {
            render(<LocationGroup />);
            expect(screen.getByTestId('id-display')).toBeInTheDocument();
            expect(screen.getByText(/L-1/)).toBeInTheDocument();
        });

        it('should render location name field', () => {
            render(<LocationGroup />);
            expect(screen.getByText('Location Name:')).toBeInTheDocument();
        });

        it('should render location description field', () => {
            render(<LocationGroup />);
            expect(screen.getByText('Location Description:')).toBeInTheDocument();
        });

        it('should render Coordinates section header', () => {
            render(<LocationGroup />);
            expect(screen.getByRole('heading', { name: 'Coordinates' })).toBeInTheDocument();
        });

        it('should render latitude and longitude fields', () => {
            render(<LocationGroup />);
            expect(screen.getByText('Latitude:')).toBeInTheDocument();
            expect(screen.getByText('Longitude:')).toBeInTheDocument();
        });
    });

    describe('altitude field', () => {
        it('should not render altitude field for 2D coordinates', () => {
            mockFieldValues.coords = [10, 20];
            render(<LocationGroup />);
            expect(screen.queryByText('Altitude:')).not.toBeInTheDocument();
        });

        it('should render altitude field for 3D coordinates', () => {
            mockFieldValues.coords = [10, 20, 100];
            render(<LocationGroup />);
            expect(screen.getByText('Altitude:')).toBeInTheDocument();
        });
    });
});
