import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { PREFIXES } from '../../schemas';

// Mock field values and handlers
const mockFieldHandlers: Record<string, ReturnType<typeof vi.fn>> = {};
const mockPushValueHandlers: Record<string, ReturnType<typeof vi.fn>> = {};
const mockFieldValues: Record<string, unknown> = {
  obj_id: { prefix: PREFIXES.CHARACTER, numeric: 1 },
  name: 'Test Character',
  role: 'Hero',
  backstory: 'A brave adventurer',
  attributes: [] as { name: string; value: number }[],
  skills: [] as { name: string; value: number }[],
  inventory: [] as { prefix: string; numeric: number }[],
};

// Mock the context
vi.mock('../../features/shared/components/ctx', () => ({
  withFieldGroup: ({
    defaultValues,
    render: renderFn,
  }: {
    defaultValues: Record<string, unknown>;
    render: (props: { group: unknown }) => React.ReactNode;
  }) => {
    return function MockFieldGroup() {
      const mockGroup = {
        state: { values: mockFieldValues },
        AppField: ({
          children,
          name,
        }: {
          children: (field: unknown) => React.ReactNode;
          name: string;
          mode?: string;
        }) => {
          if (!mockFieldHandlers[name]) {
            mockFieldHandlers[name] = vi.fn();
          }
          if (!mockPushValueHandlers[name]) {
            mockPushValueHandlers[name] = vi.fn();
          }

          const getValue = () => {
            // Handle nested names like 'attributes[0].name'
            if (name.includes('[')) {
              const match = name.match(/(\w+)\[(\d+)\](?:\.(\w+))?/);
              if (match) {
                const [, arrayName, index, propName] = match;
                const arr = mockFieldValues[arrayName] as unknown[];
                if (arr && arr[parseInt(index)]) {
                  if (propName) {
                    return (arr[parseInt(index)] as Record<string, unknown>)[
                      propName
                    ];
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
                ID:{' '}
                {
                  (
                    mockFieldValues.obj_id as {
                      prefix: string;
                      numeric: number;
                    }
                  ).prefix
                }
                -
                {
                  (
                    mockFieldValues.obj_id as {
                      prefix: string;
                      numeric: number;
                    }
                  ).numeric
                }
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
                  onChange={(e) =>
                    mockFieldHandlers[name](Number(e.target.value))
                  }
                  data-testid={`number-field-${name}`}
                />
              </div>
            ),
            AITextField: ({ label }: { label: string }) => (
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
            AITextAreaField: ({ label }: { label: string }) => (
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
  ObjectIDGroup: ({ fields }: { form: unknown; fields: string }) => (
    <div data-testid={`object-id-group-${fields}`}>ObjectIDGroup: {fields}</div>
  ),
}));

// Import after mocking
import {
  CharacterGroup,
  defaultValues,
} from '../../features/shared/components/fieldgroups/CharacterGroup';

describe('CharacterGroup', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset mock values
    mockFieldValues.obj_id = { prefix: PREFIXES.CHARACTER, numeric: 1 };
    mockFieldValues.name = 'Test Character';
    mockFieldValues.role = 'Hero';
    mockFieldValues.backstory = 'A brave adventurer';
    mockFieldValues.attributes = [];
    mockFieldValues.skills = [];
    mockFieldValues.inventory = [];
    // Clear field handlers
    Object.keys(mockFieldHandlers).forEach(
      (key) => delete mockFieldHandlers[key],
    );
    Object.keys(mockPushValueHandlers).forEach(
      (key) => delete mockPushValueHandlers[key],
    );
  });

  describe('defaultValues', () => {
    it('should have correct default prefix', () => {
      expect(defaultValues.obj_id.prefix).toBe(PREFIXES.CHARACTER);
    });

    it('should have zero as default numeric', () => {
      expect(defaultValues.obj_id.numeric).toBe(0);
    });

    it('should have empty strings for text fields', () => {
      expect(defaultValues.name).toBe('');
      expect(defaultValues.role).toBe('');
      expect(defaultValues.backstory).toBe('');
    });

    it('should have empty arrays for collection fields', () => {
      expect(defaultValues.attributes).toEqual([]);
      expect(defaultValues.skills).toEqual([]);
      expect(defaultValues.inventory).toEqual([]);
    });
  });

  describe('rendering', () => {
    it('should render ID display field', () => {
      render(<CharacterGroup />);
      expect(screen.getByTestId('id-display')).toBeInTheDocument();
      expect(screen.getByText(/C-1/)).toBeInTheDocument();
    });

    it('should render character name field', () => {
      render(<CharacterGroup />);
      expect(screen.getByText('Character Name:')).toBeInTheDocument();
    });

    it('should render character role field', () => {
      render(<CharacterGroup />);
      expect(screen.getByText('Character Role:')).toBeInTheDocument();
    });

    it('should render character backstory field', () => {
      render(<CharacterGroup />);
      expect(screen.getByText('Character Backstory:')).toBeInTheDocument();
    });

    it('should render Attributes section header', () => {
      render(<CharacterGroup />);
      expect(
        screen.getByRole('heading', { name: 'Attributes' }),
      ).toBeInTheDocument();
    });

    it('should render Skills section header', () => {
      render(<CharacterGroup />);
      expect(
        screen.getByRole('heading', { name: 'Skills' }),
      ).toBeInTheDocument();
    });

    it('should render Inventory section header', () => {
      render(<CharacterGroup />);
      expect(
        screen.getByRole('heading', { name: 'Inventory' }),
      ).toBeInTheDocument();
    });
  });

  describe('attributes array', () => {
    it('should render Add Attribute button', () => {
      render(<CharacterGroup />);
      expect(
        screen.getByRole('button', { name: 'Add Attribute' }),
      ).toBeInTheDocument();
    });

    it('should render existing attributes', () => {
      mockFieldValues.attributes = [
        { name: 'Strength', value: 10 },
        { name: 'Dexterity', value: 15 },
      ];
      render(<CharacterGroup />);
      expect(screen.getByText('Attribute 1')).toBeInTheDocument();
      expect(screen.getByText('Attribute 2')).toBeInTheDocument();
    });

    it('should render attribute name and value inputs', () => {
      mockFieldValues.attributes = [{ name: 'Strength', value: 10 }];
      render(<CharacterGroup />);
      expect(screen.getByText('Attribute Name:')).toBeInTheDocument();
      expect(screen.getByText('Attribute Value:')).toBeInTheDocument();
    });

    it('should have input for new attribute name', () => {
      render(<CharacterGroup />);
      expect(
        screen.getByPlaceholderText('New Attribute Name'),
      ).toBeInTheDocument();
    });
  });

  describe('skills array', () => {
    it('should render Add Skill button', () => {
      render(<CharacterGroup />);
      expect(
        screen.getByRole('button', { name: 'Add Skill' }),
      ).toBeInTheDocument();
    });

    it('should render existing skills', () => {
      mockFieldValues.skills = [
        { name: 'Swordsmanship', value: 5 },
        { name: 'Archery', value: 3 },
      ];
      render(<CharacterGroup />);
      expect(screen.getByText('Skill 1')).toBeInTheDocument();
      expect(screen.getByText('Skill 2')).toBeInTheDocument();
    });

    it('should have input for new skill name', () => {
      render(<CharacterGroup />);
      expect(screen.getByPlaceholderText('New Skill Name')).toBeInTheDocument();
    });
  });

  describe('inventory array', () => {
    it('should render Add Item button', () => {
      render(<CharacterGroup />);
      expect(
        screen.getByRole('button', { name: 'Add Item' }),
      ).toBeInTheDocument();
    });

    it('should render existing inventory items', () => {
      mockFieldValues.inventory = [
        { prefix: PREFIXES.ITEM, numeric: 1 },
        { prefix: PREFIXES.ITEM, numeric: 2 },
      ];
      render(<CharacterGroup />);
      expect(screen.getByText('Item 1')).toBeInTheDocument();
      expect(screen.getByText('Item 2')).toBeInTheDocument();
    });
  });
});
