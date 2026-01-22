import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { PREFIXES } from '../../schemas';
import { createMockPoint } from '../test-utils';

// Mock field values and handlers
const mockFieldHandlers: Record<string, ReturnType<typeof vi.fn>> = {};
const mockFieldValues: Record<string, unknown> = {
    obj_id: { prefix: PREFIXES.SEGMENT, numeric: 1 },
    name: 'Test Segment',
    description: 'Test Segment Description',
    start: { prefix: PREFIXES.POINT, numeric: 1 },
    end: { prefix: PREFIXES.POINT, numeric: 2 },
};

// Mock the context
vi.mock('../../features/shared/components/ctx', () => ({
    withFieldGroup: ({ defaultValues, props, render: renderFn }: {
        defaultValues: Record<string, unknown>;
        props?: Record<string, unknown>;
        render: (props: { group: unknown; points?: unknown[] }) => React.ReactNode
    }) => {
        return function MockFieldGroup({ form, fields, points }: { form?: unknown; fields?: unknown; points?: unknown[] }) {
            const mockGroup = {
                state: { values: mockFieldValues },
                AppField: ({ children, name }: { children: (field: unknown) => React.ReactNode; name: string }) => {
                    if (!mockFieldHandlers[name]) {
                        mockFieldHandlers[name] = vi.fn();
                    }

                    const getValue = () => {
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
                        PointSelectField: ({ label, points: pts }: { label: string; points?: unknown[] }) => (
                            <div>
                                <label>{label}:</label>
                                <select data-testid={`point-select-${name}`}>
                                    {(pts || points || []).map((p, i) => {
                                        const point = p as { obj_id: { prefix: string; numeric: number }; name: string };
                                        return (
                                            <option key={i} value={point.obj_id.numeric}>
                                                {point.obj_id.prefix}-{point.obj_id.numeric} ({point.name})
                                            </option>
                                        );
                                    })}
                                </select>
                            </div>
                        ),
                    };
                    return <>{children(mockField)}</>;
                },
            };
            return <>{renderFn({ group: mockGroup, points: points || [] })}</>;
        };
    },
    useFieldContext: () => ({}),
    useFormContext: () => ({}),
}));

// Mock PointGroup (not used in SegmentGroup but imported)
vi.mock('../../features/shared/components/fieldgroups/PointGroup', () => ({
    PointGroup: () => <div>PointGroup Mock</div>,
}));

// Import after mocking
import { SegmentGroup, defaultValues } from '../../features/shared/components/fieldgroups/SegmentGroup';

describe('SegmentGroup', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        mockFieldValues.obj_id = { prefix: PREFIXES.SEGMENT, numeric: 1 };
        mockFieldValues.name = 'Test Segment';
        mockFieldValues.description = 'Test Segment Description';
        mockFieldValues.start = { prefix: PREFIXES.POINT, numeric: 1 };
        mockFieldValues.end = { prefix: PREFIXES.POINT, numeric: 2 };
        Object.keys(mockFieldHandlers).forEach((key) => delete mockFieldHandlers[key]);
    });

    describe('defaultValues', () => {
        it('should have correct default prefix', () => {
            expect(defaultValues.obj_id.prefix).toBe(PREFIXES.SEGMENT);
        });

        it('should have zero as default numeric', () => {
            expect(defaultValues.obj_id.numeric).toBe(0);
        });

        it('should have empty strings for text fields', () => {
            expect(defaultValues.name).toBe('');
            expect(defaultValues.description).toBe('');
        });

        it('should have default start point', () => {
            expect(defaultValues.start).toEqual({ prefix: PREFIXES.POINT, numeric: 0 });
        });

        it('should have default end point', () => {
            expect(defaultValues.end).toEqual({ prefix: PREFIXES.POINT, numeric: 1 });
        });
    });

    describe('rendering', () => {
        it('should render ID display field', () => {
            render(<SegmentGroup points={[]} />);
            expect(screen.getByTestId('id-display')).toBeInTheDocument();
            expect(screen.getByText(/S-1/)).toBeInTheDocument();
        });

        it('should render segment name field', () => {
            render(<SegmentGroup points={[]} />);
            expect(screen.getByText('Segment Name:')).toBeInTheDocument();
        });

        it('should render segment description field', () => {
            render(<SegmentGroup points={[]} />);
            expect(screen.getByText('Segment Description:')).toBeInTheDocument();
        });

        it('should render start point select', () => {
            render(<SegmentGroup points={[]} />);
            expect(screen.getByText('Start Point:')).toBeInTheDocument();
            expect(screen.getByTestId('point-select-start')).toBeInTheDocument();
        });

        it('should render end point select', () => {
            render(<SegmentGroup points={[]} />);
            expect(screen.getByText('End Point:')).toBeInTheDocument();
            expect(screen.getByTestId('point-select-end')).toBeInTheDocument();
        });
    });

    describe('point selection', () => {
        it('should render points as options in start select', () => {
            const points = [
                createMockPoint({ obj_id: { prefix: PREFIXES.POINT, numeric: 1 }, name: 'Beginning' }),
                createMockPoint({ obj_id: { prefix: PREFIXES.POINT, numeric: 2 }, name: 'Middle' }),
            ];

            render(<SegmentGroup points={points} />);

            const startSelect = screen.getByTestId('point-select-start');
            expect(startSelect).toContainHTML('P-1 (Beginning)');
            expect(startSelect).toContainHTML('P-2 (Middle)');
        });

        it('should render points as options in end select', () => {
            const points = [
                createMockPoint({ obj_id: { prefix: PREFIXES.POINT, numeric: 1 }, name: 'Beginning' }),
                createMockPoint({ obj_id: { prefix: PREFIXES.POINT, numeric: 2 }, name: 'End' }),
            ];

            render(<SegmentGroup points={points} />);

            const endSelect = screen.getByTestId('point-select-end');
            expect(endSelect).toContainHTML('P-1 (Beginning)');
            expect(endSelect).toContainHTML('P-2 (End)');
        });

        it('should render empty selects when no points provided', () => {
            render(<SegmentGroup points={[]} />);

            const startSelect = screen.getByTestId('point-select-start');
            const endSelect = screen.getByTestId('point-select-end');

            expect(startSelect.children.length).toBe(0);
            expect(endSelect.children.length).toBe(0);
        });
    });
});
