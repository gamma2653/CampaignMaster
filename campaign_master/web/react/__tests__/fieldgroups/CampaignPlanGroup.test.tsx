import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { PREFIXES } from '../../schemas';

// Mock field values and handlers
const mockFieldHandlers: Record<string, ReturnType<typeof vi.fn>> = {};
const mockPushValueHandlers: Record<string, ReturnType<typeof vi.fn>> = {};
const mockFieldValues: Record<string, unknown> = {
  obj_id: { prefix: PREFIXES.CAMPAIGN_PLAN, numeric: 1 },
  title: 'Test Campaign',
  version: '1.0.0',
  setting: 'Fantasy',
  summary: 'A test campaign',
  storyline: [],
  storypoints: [],
  characters: [],
  locations: [],
  items: [],
  rules: [],
  objectives: [],
};

// Mock HeadlessUI components
vi.mock('@headlessui/react', () => ({
  Disclosure: ({
    children,
    defaultOpen,
  }: {
    children: (props: { open: boolean }) => React.ReactNode;
    defaultOpen?: boolean;
  }) => {
    const [isOpen] = React.useState(defaultOpen ?? false);
    return <div data-testid="disclosure">{children({ open: isOpen })}</div>;
  },
  DisclosureButton: ({
    children,
    className,
    onClick,
  }: {
    children: React.ReactNode;
    className?: string;
    onClick?: () => void;
  }) => (
    <button
      className={className}
      onClick={onClick}
      data-testid="disclosure-button"
    >
      {children}
    </button>
  ),
  DisclosurePanel: ({
    children,
    className,
  }: {
    children: React.ReactNode;
    className?: string;
  }) => (
    <div className={className} data-testid="disclosure-panel">
      {children}
    </div>
  ),
}));

// Mock heroicons
vi.mock('@heroicons/react/20/solid', () => ({
  ChevronDownIcon: ({ className }: { className?: string }) => (
    <span className={className} data-testid="chevron-icon">
      v
    </span>
  ),
}));

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
        Subscribe: ({
          children,
          selector,
        }: {
          children: (value: unknown) => React.ReactNode;
          selector: (state: { values: unknown }) => unknown;
        }) => {
          const value = selector({ values: mockFieldValues });
          return <>{children(value)}</>;
        },
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

// Mock all child fieldgroups
vi.mock('../../features/shared/components/fieldgroups/ArcGroup', () => ({
  ArcGroup: ({
    fields,
  }: {
    form: unknown;
    fields: string;
    points: unknown[];
  }) => <div data-testid={`arc-group-${fields}`}>ArcGroup: {fields}</div>,
  defaultValues: {
    obj_id: { prefix: PREFIXES.ARC, numeric: 0 },
    name: '',
    description: '',
    segments: [],
  },
}));

vi.mock('../../features/shared/components/fieldgroups/CharacterGroup', () => ({
  CharacterGroup: ({ fields }: { form: unknown; fields: string }) => (
    <div data-testid={`character-group-${fields}`}>
      CharacterGroup: {fields}
    </div>
  ),
  defaultValues: {
    obj_id: { prefix: PREFIXES.CHARACTER, numeric: 0 },
    name: '',
    role: '',
    backstory: '',
    attributes: [],
    skills: [],
    inventory: [],
  },
}));

vi.mock('../../features/shared/components/fieldgroups/LocationGroup', () => ({
  LocationGroup: ({ fields }: { form: unknown; fields: string }) => (
    <div data-testid={`location-group-${fields}`}>LocationGroup: {fields}</div>
  ),
  defaultValues: {
    obj_id: { prefix: PREFIXES.LOCATION, numeric: 0 },
    name: '',
    description: '',
    coords: [0, 0],
  },
}));

vi.mock('../../features/shared/components/fieldgroups/ItemGroup', () => ({
  ItemGroup: ({ fields }: { form: unknown; fields: string }) => (
    <div data-testid={`item-group-${fields}`}>ItemGroup: {fields}</div>
  ),
  defaultValues: {
    obj_id: { prefix: PREFIXES.ITEM, numeric: 0 },
    name: '',
    type_: '',
    description: '',
    properties: [],
  },
}));

vi.mock('../../features/shared/components/fieldgroups/RuleGroup', () => ({
  RuleGroup: ({ fields }: { form: unknown; fields: string }) => (
    <div data-testid={`rule-group-${fields}`}>RuleGroup: {fields}</div>
  ),
  defaultValues: {
    obj_id: { prefix: PREFIXES.RULE, numeric: 0 },
    description: '',
    effect: '',
    components: [],
  },
}));

vi.mock('../../features/shared/components/fieldgroups/ObjectiveGroup', () => ({
  ObjectiveGroup: ({ fields }: { form: unknown; fields: string }) => (
    <div data-testid={`objective-group-${fields}`}>
      ObjectiveGroup: {fields}
    </div>
  ),
  defaultValues: {
    obj_id: { prefix: PREFIXES.OBJECTIVE, numeric: 0 },
    description: '',
    components: [],
    prerequisites: [],
  },
}));

vi.mock('../../features/shared/components/fieldgroups/PointGroup', () => ({
  PointGroup: ({ fields }: { form: unknown; fields: string }) => (
    <div data-testid={`point-group-${fields}`}>PointGroup: {fields}</div>
  ),
  defaultValues: {
    obj_id: { prefix: PREFIXES.POINT, numeric: 0 },
    name: '',
    description: '',
    objective: null,
  },
}));

// Import after mocking
import { CampaignPlanGroup } from '../../features/shared/components/fieldgroups/CampaignPlanGroup';

describe('CampaignPlanGroup', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockFieldValues.obj_id = { prefix: PREFIXES.CAMPAIGN_PLAN, numeric: 1 };
    mockFieldValues.title = 'Test Campaign';
    mockFieldValues.version = '1.0.0';
    mockFieldValues.setting = 'Fantasy';
    mockFieldValues.summary = 'A test campaign';
    mockFieldValues.storyline = [];
    mockFieldValues.storypoints = [];
    mockFieldValues.characters = [];
    mockFieldValues.locations = [];
    mockFieldValues.items = [];
    mockFieldValues.rules = [];
    mockFieldValues.objectives = [];
    Object.keys(mockFieldHandlers).forEach(
      (key) => delete mockFieldHandlers[key],
    );
    Object.keys(mockPushValueHandlers).forEach(
      (key) => delete mockPushValueHandlers[key],
    );
  });

  describe('main structure', () => {
    it('should render Campaign Plan heading', () => {
      render(<CampaignPlanGroup />);
      expect(
        screen.getByRole('heading', { name: 'Campaign Plan' }),
      ).toBeInTheDocument();
    });

    it('should have campaign-plan-group id', () => {
      render(<CampaignPlanGroup />);
      expect(
        document.getElementById('campaign-plan-group'),
      ).toBeInTheDocument();
    });
  });

  describe('disclosure sections', () => {
    it('should render Campaign Plan Metadata section', () => {
      render(<CampaignPlanGroup />);
      expect(screen.getByText('Campaign Plan Metadata')).toBeInTheDocument();
    });

    it('should render Story Points section', () => {
      render(<CampaignPlanGroup />);
      expect(screen.getByText('Story Points (discrete)')).toBeInTheDocument();
    });

    it('should render Storyline Arcs section', () => {
      render(<CampaignPlanGroup />);
      expect(
        screen.getByText('Storyline Arcs (continuous)'),
      ).toBeInTheDocument();
    });

    it('should render Characters section button', () => {
      render(<CampaignPlanGroup />);
      // Use getAllByText since there's both a button and a heading with "Characters"
      const characterElements = screen.getAllByText('Characters');
      expect(characterElements.length).toBeGreaterThanOrEqual(1);
    });

    it('should render Locations section button', () => {
      render(<CampaignPlanGroup />);
      const locationElements = screen.getAllByText('Locations');
      expect(locationElements.length).toBeGreaterThanOrEqual(1);
    });

    it('should render Items section button', () => {
      render(<CampaignPlanGroup />);
      const itemElements = screen.getAllByText('Items');
      expect(itemElements.length).toBeGreaterThanOrEqual(1);
    });

    it('should render Rules section button', () => {
      render(<CampaignPlanGroup />);
      const ruleElements = screen.getAllByText('Rules');
      expect(ruleElements.length).toBeGreaterThanOrEqual(1);
    });

    it('should render Objectives section button', () => {
      render(<CampaignPlanGroup />);
      const objectiveElements = screen.getAllByText('Objectives');
      expect(objectiveElements.length).toBeGreaterThanOrEqual(1);
    });
  });

  describe('metadata fields', () => {
    it('should render ID display', () => {
      render(<CampaignPlanGroup />);
      expect(screen.getByTestId('id-display')).toBeInTheDocument();
      expect(screen.getByText(/CampPlan-1/)).toBeInTheDocument();
    });

    it('should render Campaign Plan Title field', () => {
      render(<CampaignPlanGroup />);
      expect(screen.getByText('Campaign Plan Title:')).toBeInTheDocument();
    });

    it('should render Campaign Plan Version field', () => {
      render(<CampaignPlanGroup />);
      expect(screen.getByText('Campaign Plan Version:')).toBeInTheDocument();
    });

    it('should render Campaign Plan Setting field', () => {
      render(<CampaignPlanGroup />);
      expect(screen.getByText('Campaign Plan Setting:')).toBeInTheDocument();
    });

    it('should render Campaign Plan Summary field', () => {
      render(<CampaignPlanGroup />);
      expect(screen.getByText('Campaign Plan Summary:')).toBeInTheDocument();
    });
  });

  describe('add buttons', () => {
    it('should render Add Story Point button', () => {
      render(<CampaignPlanGroup />);
      expect(
        screen.getByRole('button', { name: 'Add Story Point' }),
      ).toBeInTheDocument();
    });

    it('should render Add Storyline Arc button', () => {
      render(<CampaignPlanGroup />);
      expect(
        screen.getByRole('button', { name: 'Add Storyline Arc' }),
      ).toBeInTheDocument();
    });

    it('should render Add Character button', () => {
      render(<CampaignPlanGroup />);
      expect(
        screen.getByRole('button', { name: 'Add Character' }),
      ).toBeInTheDocument();
    });

    it('should render Add Location button', () => {
      render(<CampaignPlanGroup />);
      expect(
        screen.getByRole('button', { name: 'Add Location' }),
      ).toBeInTheDocument();
    });

    it('should render Add Item button', () => {
      render(<CampaignPlanGroup />);
      expect(
        screen.getByRole('button', { name: 'Add Item' }),
      ).toBeInTheDocument();
    });

    it('should render Add Rule button', () => {
      render(<CampaignPlanGroup />);
      expect(
        screen.getByRole('button', { name: 'Add Rule' }),
      ).toBeInTheDocument();
    });

    it('should render Add Objective button', () => {
      render(<CampaignPlanGroup />);
      expect(
        screen.getByRole('button', { name: 'Add Objective' }),
      ).toBeInTheDocument();
    });
  });

  describe('entity arrays', () => {
    it('should render existing storypoints', () => {
      mockFieldValues.storypoints = [
        { obj_id: { prefix: PREFIXES.POINT, numeric: 1 }, name: 'Point 1' },
        { obj_id: { prefix: PREFIXES.POINT, numeric: 2 }, name: 'Point 2' },
      ];
      render(<CampaignPlanGroup />);
      expect(
        screen.getByTestId('point-group-storypoints[0]'),
      ).toBeInTheDocument();
      expect(
        screen.getByTestId('point-group-storypoints[1]'),
      ).toBeInTheDocument();
    });

    it('should render existing characters', () => {
      mockFieldValues.characters = [
        { obj_id: { prefix: PREFIXES.CHARACTER, numeric: 1 }, name: 'Hero' },
      ];
      render(<CampaignPlanGroup />);
      expect(
        screen.getByTestId('character-group-characters[0]'),
      ).toBeInTheDocument();
    });

    it('should render existing locations', () => {
      mockFieldValues.locations = [
        { obj_id: { prefix: PREFIXES.LOCATION, numeric: 1 }, name: 'Castle' },
      ];
      render(<CampaignPlanGroup />);
      expect(
        screen.getByTestId('location-group-locations[0]'),
      ).toBeInTheDocument();
    });

    it('should render existing items', () => {
      mockFieldValues.items = [
        { obj_id: { prefix: PREFIXES.ITEM, numeric: 1 }, name: 'Sword' },
      ];
      render(<CampaignPlanGroup />);
      expect(screen.getByTestId('item-group-items[0]')).toBeInTheDocument();
    });

    it('should render existing rules', () => {
      mockFieldValues.rules = [
        {
          obj_id: { prefix: PREFIXES.RULE, numeric: 1 },
          description: 'Rule 1',
        },
      ];
      render(<CampaignPlanGroup />);
      expect(screen.getByTestId('rule-group-rules[0]')).toBeInTheDocument();
    });

    it('should render existing objectives', () => {
      mockFieldValues.objectives = [
        {
          obj_id: { prefix: PREFIXES.OBJECTIVE, numeric: 1 },
          description: 'Obj 1',
        },
      ];
      render(<CampaignPlanGroup />);
      expect(
        screen.getByTestId('objective-group-objectives[0]'),
      ).toBeInTheDocument();
    });

    it('should render existing storyline arcs', () => {
      mockFieldValues.storyline = [
        { obj_id: { prefix: PREFIXES.ARC, numeric: 1 }, name: 'Main Arc' },
      ];
      render(<CampaignPlanGroup />);
      expect(screen.getByTestId('arc-group-storyline[0]')).toBeInTheDocument();
    });
  });

  describe('section headers', () => {
    it('should render Storyline section header', () => {
      render(<CampaignPlanGroup />);
      expect(
        screen.getByRole('heading', { name: 'Storyline (continuous)' }),
      ).toBeInTheDocument();
    });

    it('should render Characters section header in panel', () => {
      render(<CampaignPlanGroup />);
      expect(
        screen.getByRole('heading', { name: 'Characters' }),
      ).toBeInTheDocument();
    });

    it('should render Locations section header in panel', () => {
      render(<CampaignPlanGroup />);
      expect(
        screen.getByRole('heading', { name: 'Locations' }),
      ).toBeInTheDocument();
    });

    it('should render Items section header in panel', () => {
      render(<CampaignPlanGroup />);
      expect(
        screen.getByRole('heading', { name: 'Items' }),
      ).toBeInTheDocument();
    });

    it('should render Rules section header in panel', () => {
      render(<CampaignPlanGroup />);
      expect(
        screen.getByRole('heading', { name: 'Rules' }),
      ).toBeInTheDocument();
    });

    it('should render Objectives section header in panel', () => {
      render(<CampaignPlanGroup />);
      expect(
        screen.getByRole('heading', { name: 'Objectives' }),
      ).toBeInTheDocument();
    });
  });
});
