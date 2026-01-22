import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { PREFIXES } from '../../schemas';

// Mock field values and handlers
const mockFieldHandlers: Record<string, ReturnType<typeof vi.fn>> = {};
const mockPushValueHandlers: Record<string, ReturnType<typeof vi.fn>> = {};
const mockFieldValues: Record<string, unknown> = {
    obj_id: { prefix: PREFIXES.ITEM, numeric: 1 },
    name: 'Test Item',
    type_: 'Weapon',
    description: 'Test Item Description',
    properties: [] as { name: string; value: string }[],
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
                    if (!mockPushValueHandlers[name]) {
                        mockPushValueHandlers[name] = vi.fn();
                    }

                    const getValue = () => {
                        if (name.includes('[')) {
                            const match = name.match(/(\w+)\[(\d+)\](?:\.(\w+))?/);
                            if (match) {
                                const [, arrayName, index, propName] = match;
                                const arr = mockFieldValues[arrayName] as unknown[];
                                if (arr && arr[parseInt(index)]) {
                                    if (propName) {
                                        return (arr[parseInt(index)] as Record<string, unknown>)[propName];
                                    }
                                    return arr[parseInt(index)];
                                }
                            }
                        }
                        return mockFieldValues[name] ?? defaultValues[name];
                    };

                    const mockField = {
                        state: { value: getValue() },
                        handleChange: mockFieldHandlers[name],
                        pushValue: mockPushValueHandlers[name],
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
import { ItemGroup, defaultValues } from '../../features/shared/components/fieldgroups/ItemGroup';

describe('ItemGroup', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        mockFieldValues.obj_id = { prefix: PREFIXES.ITEM, numeric: 1 };
        mockFieldValues.name = 'Test Item';
        mockFieldValues.type_ = 'Weapon';
        mockFieldValues.description = 'Test Item Description';
        mockFieldValues.properties = [];
        Object.keys(mockFieldHandlers).forEach((key) => delete mockFieldHandlers[key]);
        Object.keys(mockPushValueHandlers).forEach((key) => delete mockPushValueHandlers[key]);
    });

    describe('defaultValues', () => {
        it('should have correct default prefix', () => {
            expect(defaultValues.obj_id.prefix).toBe(PREFIXES.ITEM);
        });

        it('should have zero as default numeric', () => {
            expect(defaultValues.obj_id.numeric).toBe(0);
        });

        it('should have empty strings for text fields', () => {
            expect(defaultValues.name).toBe('');
            expect(defaultValues.type_).toBe('');
            expect(defaultValues.description).toBe('');
        });

        it('should have empty properties array', () => {
            expect(defaultValues.properties).toEqual([]);
        });
    });

    describe('rendering', () => {
        it('should render ID display field', () => {
            render(<ItemGroup />);
            expect(screen.getByTestId('id-display')).toBeInTheDocument();
            expect(screen.getByText(/I-1/)).toBeInTheDocument();
        });

        it('should render item description field', () => {
            render(<ItemGroup />);
            expect(screen.getByText('Item Description:')).toBeInTheDocument();
        });

        it('should render item type field', () => {
            render(<ItemGroup />);
            expect(screen.getByText('Item Type:')).toBeInTheDocument();
        });

        it('should render Properties section header', () => {
            render(<ItemGroup />);
            expect(screen.getByRole('heading', { name: 'Properties' })).toBeInTheDocument();
        });

        it('should render Add Property button', () => {
            render(<ItemGroup />);
            expect(screen.getByRole('button', { name: 'Add Property' })).toBeInTheDocument();
        });
    });

    describe('properties array', () => {
        it('should render existing properties', () => {
            mockFieldValues.properties = [
                { name: 'Damage', value: '10' },
                { name: 'Weight', value: '5' },
            ];
            render(<ItemGroup />);
            expect(screen.getByText('Property 1:')).toBeInTheDocument();
            expect(screen.getByText('Property 2:')).toBeInTheDocument();
        });

        it('should have input for new property name', () => {
            render(<ItemGroup />);
            expect(screen.getByPlaceholderText('New Property Name')).toBeInTheDocument();
        });

        it('should render empty properties area when no properties', () => {
            mockFieldValues.properties = [];
            render(<ItemGroup />);
            expect(screen.queryByText('Property 1:')).not.toBeInTheDocument();
        });
    });
});
