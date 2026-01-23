import { describe, it, expect } from 'vitest';
import {
  PREFIXES,
  PREFIX_TO_NAME,
  ObjectSchema,
  RuleSchema,
  PointSchema,
  SegmentSchema,
  ArcSchema,
  ItemSchema,
  CharacterSchema,
  LocationSchema,
  CampaignSchema,
  AgentConfigSchema,
  getUrlSegment,
} from '../schemas';

describe('PREFIXES', () => {
  it('should have all expected prefix values', () => {
    expect(PREFIXES.RULE).toBe('R');
    expect(PREFIXES.OBJECTIVE).toBe('O');
    expect(PREFIXES.POINT).toBe('P');
    expect(PREFIXES.SEGMENT).toBe('S');
    expect(PREFIXES.ARC).toBe('A');
    expect(PREFIXES.ITEM).toBe('I');
    expect(PREFIXES.CHARACTER).toBe('C');
    expect(PREFIXES.LOCATION).toBe('L');
    expect(PREFIXES.CAMPAIGN_PLAN).toBe('CampPlan');
    expect(PREFIXES.AGENT_CONFIG).toBe('AG');
  });

  it('should have matching names in PREFIX_TO_NAME', () => {
    expect(PREFIX_TO_NAME[PREFIXES.RULE]).toBe('Rule');
    expect(PREFIX_TO_NAME[PREFIXES.CHARACTER]).toBe('Character');
    expect(PREFIX_TO_NAME[PREFIXES.CAMPAIGN_PLAN]).toBe('Campaign Plan');
  });
});

describe('getUrlSegment', () => {
  it('should create lowercase URL segments from ID objects', () => {
    expect(getUrlSegment({ prefix: 'R', numeric: 1 })).toBe('r/1');
    expect(getUrlSegment({ prefix: 'CampPlan', numeric: 42 })).toBe(
      'campplan/42',
    );
    expect(getUrlSegment({ prefix: 'C', numeric: 0 })).toBe('c/0');
  });
});

describe('ObjectSchema', () => {
  it('should parse a valid object with ID', () => {
    const result = ObjectSchema.parse({
      obj_id: { prefix: 'MISC', numeric: 1 },
    });
    expect(result.obj_id.prefix).toBe('MISC');
    expect(result.obj_id.numeric).toBe(1);
  });

  it('should apply defaults for missing ID fields', () => {
    const result = ObjectSchema.parse({
      obj_id: {},
    });
    expect(result.obj_id.prefix).toBe(PREFIXES.MISC);
    expect(result.obj_id.numeric).toBe(0);
  });
});

describe('RuleSchema', () => {
  it('should parse a valid rule', () => {
    const result = RuleSchema.parse({
      obj_id: { prefix: 'R', numeric: 1 },
      description: 'Test rule',
      effect: 'Does something',
      components: ['comp1', 'comp2'],
    });
    expect(result.obj_id.prefix).toBe('R');
    expect(result.description).toBe('Test rule');
    expect(result.effect).toBe('Does something');
    expect(result.components).toEqual(['comp1', 'comp2']);
  });

  it('should apply defaults for missing fields', () => {
    const result = RuleSchema.parse({
      obj_id: { prefix: 'R', numeric: 0 },
    });
    expect(result.description).toBe('');
    expect(result.effect).toBe('');
    expect(result.components).toEqual([]);
  });

  it('should reject invalid prefix', () => {
    expect(() =>
      RuleSchema.parse({
        obj_id: { prefix: 'C', numeric: 1 },
      }),
    ).toThrow();
  });
});

describe('PointSchema', () => {
  it('should parse a valid point', () => {
    const result = PointSchema.parse({
      obj_id: { prefix: 'P', numeric: 1 },
      name: 'Test Point',
      description: 'A point in the story',
      objective: { prefix: 'O', numeric: 5 },
    });
    expect(result.name).toBe('Test Point');
    expect(result.objective?.prefix).toBe('O');
  });

  it('should apply catch defaults for invalid strings', () => {
    const result = PointSchema.parse({
      obj_id: { prefix: 'P', numeric: 1 },
      name: '', // Empty string should trigger catch
      description: '',
      objective: null,
    });
    expect(result.name).toBe('Unnamed Point');
    expect(result.description).toBe('No description');
  });

  it('should allow null objective', () => {
    const result = PointSchema.parse({
      obj_id: { prefix: 'P', numeric: 1 },
      name: 'Test',
      description: 'Desc',
      objective: null,
    });
    expect(result.objective).toBeNull();
  });
});

describe('SegmentSchema', () => {
  it('should parse a valid segment with start and end points', () => {
    const result = SegmentSchema.parse({
      obj_id: { prefix: 'S', numeric: 1 },
      name: 'Test Segment',
      description: 'A segment',
      start: { prefix: 'P', numeric: 1 },
      end: { prefix: 'P', numeric: 2 },
    });
    expect(result.start.prefix).toBe('P');
    expect(result.end.numeric).toBe(2);
  });
});

describe('ArcSchema', () => {
  it('should parse an arc with segments', () => {
    const result = ArcSchema.parse({
      obj_id: { prefix: 'A', numeric: 1 },
      name: 'Test Arc',
      description: 'An arc',
      segments: [
        {
          obj_id: { prefix: 'S', numeric: 1 },
          name: 'Seg 1',
          description: 'First segment',
          start: { prefix: 'P', numeric: 1 },
          end: { prefix: 'P', numeric: 2 },
        },
      ],
    });
    expect(result.segments).toHaveLength(1);
    expect(result.segments[0].name).toBe('Seg 1');
  });
});

describe('ItemSchema', () => {
  it('should parse a valid item with properties', () => {
    const result = ItemSchema.parse({
      obj_id: { prefix: 'I', numeric: 1 },
      name: 'Magic Sword',
      type_: 'Weapon',
      description: 'A powerful weapon',
      properties: { damage: '2d6', magical: 'true' },
    });
    expect(result.name).toBe('Magic Sword');
    expect(result.type_).toBe('Weapon');
    expect(result.properties.damage).toBe('2d6');
  });

  it('should apply defaults', () => {
    const result = ItemSchema.parse({
      obj_id: { prefix: 'I', numeric: 1 },
    });
    expect(result.name).toBe('Unnamed Item');
    expect(result.type_).toBe('Misc');
    expect(result.properties).toEqual({});
  });
});

describe('CharacterSchema', () => {
  it('should parse a valid character', () => {
    const result = CharacterSchema.parse({
      obj_id: { prefix: 'C', numeric: 1 },
      name: 'Hero',
      role: 'Protagonist',
      backstory: 'A brave adventurer',
      attributes: { strength: 18, dexterity: 14 },
      skills: { athletics: 5 },
      storylines: [{ prefix: 'A', numeric: 1 }],
      inventory: [{ prefix: 'I', numeric: 1 }],
    });
    expect(result.name).toBe('Hero');
    expect(result.attributes.strength).toBe(18);
    expect(result.inventory).toHaveLength(1);
  });

  it('should apply defaults for missing fields', () => {
    const result = CharacterSchema.parse({
      obj_id: { prefix: 'C', numeric: 1 },
    });
    expect(result.name).toBe('Unnamed Character');
    expect(result.role).toBe('No role');
    expect(result.attributes).toEqual({});
    expect(result.skills).toEqual({});
    expect(result.storylines).toEqual([]);
    expect(result.inventory).toEqual([]);
  });
});

describe('LocationSchema', () => {
  it('should parse a location with 2D coordinates', () => {
    const result = LocationSchema.parse({
      obj_id: { prefix: 'L', numeric: 1 },
      name: 'Village',
      description: 'A small village',
      neighboring_locations: [{ prefix: 'L', numeric: 2 }],
      coords: [10, 20],
    });
    expect(result.coords).toEqual([10, 20]);
  });

  it('should parse a location with 3D coordinates', () => {
    const result = LocationSchema.parse({
      obj_id: { prefix: 'L', numeric: 1 },
      name: 'Cave',
      description: 'Underground cave',
      neighboring_locations: [],
      coords: [10, 20, -5],
    });
    expect(result.coords).toEqual([10, 20, -5]);
  });

  it('should allow undefined coordinates', () => {
    const result = LocationSchema.parse({
      obj_id: { prefix: 'L', numeric: 1 },
      name: 'Mystery Place',
      description: 'Unknown location',
      neighboring_locations: [],
    });
    expect(result.coords).toBeUndefined();
  });
});

describe('CampaignSchema', () => {
  it('should parse a complete campaign', () => {
    const result = CampaignSchema.parse({
      obj_id: { prefix: 'CampPlan', numeric: 1 },
      title: 'Epic Quest',
      version: '1.0.0',
      setting: 'Fantasy',
      summary: 'An epic adventure',
      storyline: [],
      storypoints: [],
      characters: [],
      locations: [],
      items: [],
      rules: [],
      objectives: [],
    });
    expect(result.title).toBe('Epic Quest');
    expect(result.version).toBe('1.0.0');
    expect(result.setting).toBe('Fantasy');
  });

  it('should apply defaults for missing fields', () => {
    const result = CampaignSchema.parse({
      obj_id: { prefix: 'CampPlan', numeric: 1 },
    });
    expect(result.title).toBe('Unnamed Campaign');
    expect(result.version).toBe('0.0.0');
    expect(result.setting).toBe('Generic');
    expect(result.summary).toBe('No summary');
    expect(result.storyline).toEqual([]);
  });

  it('should parse nested entities within campaign', () => {
    const result = CampaignSchema.parse({
      obj_id: { prefix: 'CampPlan', numeric: 1 },
      title: 'Test',
      version: '1.0.0',
      setting: 'Test',
      summary: 'Test',
      storyline: [],
      storypoints: [
        {
          obj_id: { prefix: 'P', numeric: 1 },
          name: 'Point 1',
          description: 'First point',
          objective: null,
        },
      ],
      characters: [
        {
          obj_id: { prefix: 'C', numeric: 1 },
          name: 'Hero',
          role: 'PC',
          backstory: 'Story',
          attributes: {},
          skills: {},
          storylines: [],
          inventory: [],
        },
      ],
      locations: [],
      items: [],
      rules: [],
      objectives: [],
    });
    expect(result.storypoints).toHaveLength(1);
    expect(result.characters).toHaveLength(1);
    expect(result.characters[0].name).toBe('Hero');
  });
});

describe('AgentConfigSchema', () => {
  it('should parse a valid agent config', () => {
    const result = AgentConfigSchema.parse({
      obj_id: { prefix: 'AG', numeric: 1 },
      name: 'GPT-4',
      provider_type: 'openai',
      api_key: 'sk-xxx',
      base_url: 'https://api.openai.com',
      model: 'gpt-4',
      max_tokens: 1000,
      temperature: 0.5,
      is_default: true,
      is_enabled: true,
      system_prompt: 'You are a helpful assistant.',
    });
    expect(result.name).toBe('GPT-4');
    expect(result.max_tokens).toBe(1000);
    expect(result.is_default).toBe(true);
  });

  it('should apply defaults', () => {
    const result = AgentConfigSchema.parse({
      obj_id: { prefix: 'AG', numeric: 1 },
    });
    expect(result.name).toBe('');
    expect(result.max_tokens).toBe(500);
    expect(result.temperature).toBe(0.7);
    expect(result.is_default).toBe(false);
    expect(result.is_enabled).toBe(true);
  });
});
