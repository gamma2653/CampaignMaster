import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { PREFIXES } from '../../schemas';

// Mock field values and handlers
const mockFieldHandlers: Record<string, ReturnType<typeof vi.fn>> = {};
const mockPushValueHandlers: Record<string, ReturnType<typeof vi.fn>> = {};
const mockFieldValues: Record<string, unknown> = {
  obj_id: { prefix: PREFIXES.RULE, numeric: 1 },
  description: 'Test Rule Description',
  effect: 'Test Rule Effect',
  components: [] as string[],
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
  ObjectIDGroup: () => <div>ObjectIDGroup Mock</div>,
}));

// Import after mocking
import {
  RuleGroup,
  defaultValues,
} from '../../features/shared/components/fieldgroups/RuleGroup';

describe('RuleGroup', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockFieldValues.obj_id = { prefix: PREFIXES.RULE, numeric: 1 };
    mockFieldValues.description = 'Test Rule Description';
    mockFieldValues.effect = 'Test Rule Effect';
    mockFieldValues.components = [];
    Object.keys(mockFieldHandlers).forEach(
      (key) => delete mockFieldHandlers[key],
    );
    Object.keys(mockPushValueHandlers).forEach(
      (key) => delete mockPushValueHandlers[key],
    );
  });

  describe('defaultValues', () => {
    it('should have correct default prefix', () => {
      expect(defaultValues.obj_id.prefix).toBe(PREFIXES.RULE);
    });

    it('should have zero as default numeric', () => {
      expect(defaultValues.obj_id.numeric).toBe(0);
    });

    it('should have empty strings for text fields', () => {
      expect(defaultValues.description).toBe('');
      expect(defaultValues.effect).toBe('');
    });

    it('should have empty components array', () => {
      expect(defaultValues.components).toEqual([]);
    });
  });

  describe('rendering', () => {
    it('should render ID display field', () => {
      render(<RuleGroup />);
      expect(screen.getByTestId('id-display')).toBeInTheDocument();
      expect(screen.getByText(/R-1/)).toBeInTheDocument();
    });

    it('should render rule description field', () => {
      render(<RuleGroup />);
      expect(screen.getByText('Rule Description:')).toBeInTheDocument();
    });

    it('should render rule effect field', () => {
      render(<RuleGroup />);
      expect(screen.getByText('Rule Effect:')).toBeInTheDocument();
    });

    it('should render Components section header', () => {
      render(<RuleGroup />);
      expect(
        screen.getByRole('heading', { name: 'Components' }),
      ).toBeInTheDocument();
    });

    it('should render Add Component button', () => {
      render(<RuleGroup />);
      expect(
        screen.getByRole('button', { name: 'Add Component' }),
      ).toBeInTheDocument();
    });
  });

  describe('components array', () => {
    it('should render existing components', () => {
      mockFieldValues.components = ['Component A', 'Component B'];
      render(<RuleGroup />);
      expect(screen.getByText('Component 1')).toBeInTheDocument();
      expect(screen.getByText('Component 2')).toBeInTheDocument();
    });

    it('should render component input fields', () => {
      mockFieldValues.components = ['Component A'];
      render(<RuleGroup />);
      expect(screen.getByText('Component 1:')).toBeInTheDocument();
    });

    it('should render empty components area when no components', () => {
      mockFieldValues.components = [];
      render(<RuleGroup />);
      expect(screen.queryByText('Component 1')).not.toBeInTheDocument();
    });
  });
});
