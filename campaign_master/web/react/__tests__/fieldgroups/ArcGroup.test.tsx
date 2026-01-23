import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { PREFIXES } from '../../schemas';
import { createMockPoint, createMockSegment } from '../test-utils';

// Mock field values and handlers
const mockFieldHandlers: Record<string, ReturnType<typeof vi.fn>> = {};
const mockPushValueHandlers: Record<string, ReturnType<typeof vi.fn>> = {};
const mockFieldValues: Record<string, unknown> = {
  obj_id: { prefix: PREFIXES.ARC, numeric: 1 },
  name: 'Test Arc',
  description: 'Test Arc Description',
  segments: [],
};

// Mock the context
vi.mock('../../features/shared/components/ctx', () => ({
  withFieldGroup: ({
    defaultValues,
    render: renderFn,
  }: {
    defaultValues: Record<string, unknown>;
    render: (props: { group: unknown; points?: unknown[] }) => React.ReactNode;
  }) => {
    return function MockFieldGroup({
      points,
    }: {
      form?: unknown;
      fields?: unknown;
      points?: unknown[];
    }) {
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

// Mock SegmentGroup
vi.mock('../../features/shared/components/fieldgroups/SegmentGroup', () => ({
  SegmentGroup: ({
    fields,
    points,
  }: {
    form: unknown;
    fields: string;
    points: unknown[];
  }) => (
    <div data-testid={`segment-group-${fields}`}>
      SegmentGroup: {fields} (points: {points?.length ?? 0})
    </div>
  ),
  defaultValues: {
    obj_id: { prefix: PREFIXES.SEGMENT, numeric: 0 },
    name: '',
    description: '',
    start: { prefix: PREFIXES.POINT, numeric: 0 },
    end: { prefix: PREFIXES.POINT, numeric: 1 },
  },
}));

// Import after mocking
import {
  ArcGroup,
  defaultValues,
} from '../../features/shared/components/fieldgroups/ArcGroup';

describe('ArcGroup', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockFieldValues.obj_id = { prefix: PREFIXES.ARC, numeric: 1 };
    mockFieldValues.name = 'Test Arc';
    mockFieldValues.description = 'Test Arc Description';
    mockFieldValues.segments = [];
    Object.keys(mockFieldHandlers).forEach(
      (key) => delete mockFieldHandlers[key],
    );
    Object.keys(mockPushValueHandlers).forEach(
      (key) => delete mockPushValueHandlers[key],
    );
  });

  describe('defaultValues', () => {
    it('should have correct default prefix', () => {
      expect(defaultValues.obj_id.prefix).toBe(PREFIXES.ARC);
    });

    it('should have zero as default numeric', () => {
      expect(defaultValues.obj_id.numeric).toBe(0);
    });

    it('should have empty strings for text fields', () => {
      expect(defaultValues.name).toBe('');
      expect(defaultValues.description).toBe('');
    });

    it('should have empty segments array', () => {
      expect(defaultValues.segments).toEqual([]);
    });
  });

  describe('rendering', () => {
    it('should render ID display field', () => {
      render(<ArcGroup points={[]} />);
      expect(screen.getByTestId('id-display')).toBeInTheDocument();
      expect(screen.getByText(/A-1/)).toBeInTheDocument();
    });

    it('should render arc name field', () => {
      render(<ArcGroup points={[]} />);
      expect(screen.getByText('Arc Name:')).toBeInTheDocument();
    });

    it('should render arc description field', () => {
      render(<ArcGroup points={[]} />);
      expect(screen.getByText('Arc Description:')).toBeInTheDocument();
    });

    it('should render Segments section header', () => {
      render(<ArcGroup points={[]} />);
      expect(
        screen.getByRole('heading', { name: 'Segments' }),
      ).toBeInTheDocument();
    });

    it('should render Add Segment button', () => {
      render(<ArcGroup points={[]} />);
      expect(
        screen.getByRole('button', { name: 'Add Segment' }),
      ).toBeInTheDocument();
    });
  });

  describe('segments array', () => {
    it('should render existing segments', () => {
      const segment1 = createMockSegment({
        obj_id: { prefix: PREFIXES.SEGMENT, numeric: 1 },
      });
      const segment2 = createMockSegment({
        obj_id: { prefix: PREFIXES.SEGMENT, numeric: 2 },
      });
      mockFieldValues.segments = [segment1, segment2];

      render(<ArcGroup points={[]} />);

      expect(
        screen.getByTestId('segment-group-segments[0]'),
      ).toBeInTheDocument();
      expect(
        screen.getByTestId('segment-group-segments[1]'),
      ).toBeInTheDocument();
    });

    it('should pass points prop to SegmentGroup children', () => {
      const points = [
        createMockPoint({
          obj_id: { prefix: PREFIXES.POINT, numeric: 1 },
          name: 'Start',
        }),
        createMockPoint({
          obj_id: { prefix: PREFIXES.POINT, numeric: 2 },
          name: 'End',
        }),
      ];
      const segment = createMockSegment();
      mockFieldValues.segments = [segment];

      render(<ArcGroup points={points} />);

      expect(screen.getByText(/points: 2/)).toBeInTheDocument();
    });

    it('should render empty segments area when no segments', () => {
      mockFieldValues.segments = [];
      render(<ArcGroup points={[]} />);

      expect(screen.queryByTestId(/segment-group-/)).not.toBeInTheDocument();
    });
  });
});
