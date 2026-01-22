import { describe, it, expect } from 'vitest';
import schemas, {
    PREFIXES,
    PREFIX_TO_NAME,
    getUrlSegment,
    PointSchema,
    SegmentSchema,
    ArcSchema,
    RuleSchema,
    ObjectiveSchema,
    ItemSchema,
    CharacterSchema,
    LocationSchema,
    CampaignSchema,
    ObjectSchema,
} from '../schemas';

describe('PREFIXES', () => {
    it('should have correct prefix values', () => {
        expect(PREFIXES.RULE).toBe('R');
        expect(PREFIXES.OBJECTIVE).toBe('O');
        expect(PREFIXES.POINT).toBe('P');
        expect(PREFIXES.SEGMENT).toBe('S');
        expect(PREFIXES.ARC).toBe('A');
        expect(PREFIXES.ITEM).toBe('I');
        expect(PREFIXES.CHARACTER).toBe('C');
        expect(PREFIXES.LOCATION).toBe('L');
        expect(PREFIXES.CAMPAIGN_PLAN).toBe('CampPlan');
    });

    it('should have MISC as fallback prefix', () => {
        expect(PREFIXES.MISC).toBe('MISC');
    });
});

describe('PREFIX_TO_NAME', () => {
    it('should map prefixes to human-readable names', () => {
        expect(PREFIX_TO_NAME[PREFIXES.RULE]).toBe('Rule');
        expect(PREFIX_TO_NAME[PREFIXES.CHARACTER]).toBe('Character');
        expect(PREFIX_TO_NAME[PREFIXES.CAMPAIGN_PLAN]).toBe('Campaign Plan');
    });
});

describe('getUrlSegment', () => {
    it('should return lowercase prefix/numeric format', () => {
        expect(getUrlSegment({ prefix: 'P', numeric: 42 })).toBe('p/42');
    });

    it('should handle CampaignPlan prefix', () => {
        expect(getUrlSegment({ prefix: 'CampPlan', numeric: 1 })).toBe('campplan/1');
    });

    it('should handle zero numeric', () => {
        expect(getUrlSegment({ prefix: 'R', numeric: 0 })).toBe('r/0');
    });

    it('should handle large numeric values', () => {
        expect(getUrlSegment({ prefix: 'C', numeric: 999999 })).toBe('c/999999');
    });
});

describe('ObjectSchema', () => {
    it('should validate object with valid ID', () => {
        const result = ObjectSchema.safeParse({
            obj_id: { prefix: 'P', numeric: 1 },
        });
        expect(result.success).toBe(true);
    });

    it('should use default values for invalid ID fields', () => {
        const result = ObjectSchema.parse({
            obj_id: { prefix: '', numeric: -1 },
        });
        expect(result.obj_id.prefix).toBe('MISC');
        expect(result.obj_id.numeric).toBe(0);
    });
});

describe('PointSchema', () => {
    it('should validate valid Point', () => {
        const result = PointSchema.safeParse({
            obj_id: { prefix: 'P', numeric: 1 },
            name: 'Test Point',
            description: 'A description',
            objective: null,
        });
        expect(result.success).toBe(true);
    });

    it('should use default name when empty', () => {
        const result = PointSchema.parse({
            obj_id: { prefix: 'P', numeric: 1 },
            name: '',
            description: 'Desc',
            objective: null,
        });
        expect(result.name).toBe('Unnamed Point');
    });

    it('should use catch value for invalid description', () => {
        const result = PointSchema.parse({
            obj_id: { prefix: 'P', numeric: 1 },
            name: 'Test',
            description: '',
            objective: null,
        });
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

    it('should accept valid objective ID', () => {
        const result = PointSchema.parse({
            obj_id: { prefix: 'P', numeric: 1 },
            name: 'Test',
            description: 'Desc',
            objective: { prefix: 'O', numeric: 1 },
        });
        expect(result.objective).toEqual({ prefix: 'O', numeric: 1 });
    });
});

describe('RuleSchema', () => {
    it('should validate valid Rule', () => {
        const result = RuleSchema.safeParse({
            obj_id: { prefix: 'R', numeric: 1 },
            description: 'Rule description',
            effect: 'Rule effect',
            components: ['comp1', 'comp2'],
        });
        expect(result.success).toBe(true);
    });

    it('should use default empty array for components', () => {
        const result = RuleSchema.parse({
            obj_id: { prefix: 'R', numeric: 1 },
        });
        expect(result.components).toEqual([]);
    });

    it('should use default empty string for description', () => {
        const result = RuleSchema.parse({
            obj_id: { prefix: 'R', numeric: 1 },
        });
        expect(result.description).toBe('');
    });
});

describe('CharacterSchema', () => {
    it('should validate valid Character', () => {
        const result = CharacterSchema.safeParse({
            obj_id: { prefix: 'C', numeric: 1 },
            name: 'Hero',
            role: 'Protagonist',
            backstory: 'A brave adventurer',
            attributes: { strength: 10 },
            skills: { swordsmanship: 5 },
            storylines: [],
            inventory: [],
        });
        expect(result.success).toBe(true);
    });

    it('should use default values for missing fields', () => {
        const result = CharacterSchema.parse({
            obj_id: { prefix: 'C', numeric: 1 },
        });
        expect(result.name).toBe('Unnamed Character');
        expect(result.role).toBe('No role');
        expect(result.backstory).toBe('No backstory');
        expect(result.attributes).toEqual({});
        expect(result.skills).toEqual({});
        expect(result.storylines).toEqual([]);
        expect(result.inventory).toEqual([]);
    });
});

describe('ItemSchema', () => {
    it('should validate valid Item', () => {
        const result = ItemSchema.safeParse({
            obj_id: { prefix: 'I', numeric: 1 },
            name: 'Sword',
            type_: 'Weapon',
            description: 'A sharp sword',
            properties: { damage: '10' },
        });
        expect(result.success).toBe(true);
    });

    it('should use default values for missing fields', () => {
        const result = ItemSchema.parse({
            obj_id: { prefix: 'I', numeric: 1 },
        });
        expect(result.name).toBe('Unnamed Item');
        expect(result.type_).toBe('Misc');
        expect(result.description).toBe('No description');
        expect(result.properties).toEqual({});
    });
});

describe('LocationSchema', () => {
    it('should validate valid Location', () => {
        const result = LocationSchema.safeParse({
            obj_id: { prefix: 'L', numeric: 1 },
            name: 'Castle',
            description: 'A grand castle',
            neighboring_locations: [],
            coords: [10, 20],
        });
        expect(result.success).toBe(true);
    });

    it('should accept 3D coordinates', () => {
        const result = LocationSchema.parse({
            obj_id: { prefix: 'L', numeric: 1 },
            name: 'Sky Castle',
            description: 'A floating castle',
            neighboring_locations: [],
            coords: [10, 20, 100],
        });
        expect(result.coords).toEqual([10, 20, 100]);
    });

    it('should allow undefined coords', () => {
        const result = LocationSchema.parse({
            obj_id: { prefix: 'L', numeric: 1 },
            name: 'Test',
            description: 'Desc',
            neighboring_locations: [],
        });
        expect(result.coords).toBeUndefined();
    });
});

describe('ArcSchema', () => {
    it('should validate valid Arc', () => {
        const result = ArcSchema.safeParse({
            obj_id: { prefix: 'A', numeric: 1 },
            name: 'Main Quest',
            description: 'The main story arc',
            segments: [],
        });
        expect(result.success).toBe(true);
    });

    it('should validate Arc with nested Segments', () => {
        const result = ArcSchema.safeParse({
            obj_id: { prefix: 'A', numeric: 1 },
            name: 'Main Quest',
            description: 'Main arc',
            segments: [
                {
                    obj_id: { prefix: 'S', numeric: 1 },
                    name: 'Segment 1',
                    description: 'First segment',
                    start: { prefix: 'P', numeric: 1 },
                    end: { prefix: 'P', numeric: 2 },
                },
            ],
        });
        expect(result.success).toBe(true);
    });
});

describe('CampaignSchema', () => {
    it('should validate valid Campaign', () => {
        const result = CampaignSchema.safeParse({
            obj_id: { prefix: 'CampPlan', numeric: 1 },
            title: 'Epic Adventure',
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
        expect(result.success).toBe(true);
    });

    it('should use default values for all missing fields', () => {
        const result = CampaignSchema.parse({
            obj_id: { prefix: 'CampPlan', numeric: 1 },
        });
        expect(result.title).toBe('Unnamed Campaign');
        expect(result.version).toBe('0.0.0');
        expect(result.setting).toBe('Generic');
        expect(result.summary).toBe('No summary');
        expect(result.storyline).toEqual([]);
        expect(result.storypoints).toEqual([]);
        expect(result.characters).toEqual([]);
        expect(result.locations).toEqual([]);
        expect(result.items).toEqual([]);
        expect(result.rules).toEqual([]);
        expect(result.objectives).toEqual([]);
    });

    it('should validate Campaign with nested entities', () => {
        const result = CampaignSchema.safeParse({
            obj_id: { prefix: 'CampPlan', numeric: 1 },
            title: 'Test',
            version: '1.0',
            setting: 'Fantasy',
            summary: 'Summary',
            storyline: [],
            storypoints: [
                {
                    obj_id: { prefix: 'P', numeric: 1 },
                    name: 'Point',
                    description: 'Desc',
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
        expect(result.success).toBe(true);
    });
});

describe('Default exports', () => {
    it('should export all schemas', () => {
        expect(schemas.PointSchema).toBeDefined();
        expect(schemas.SegmentSchema).toBeDefined();
        expect(schemas.ArcSchema).toBeDefined();
        expect(schemas.RuleSchema).toBeDefined();
        expect(schemas.ObjectiveSchema).toBeDefined();
        expect(schemas.ItemSchema).toBeDefined();
        expect(schemas.CharacterSchema).toBeDefined();
        expect(schemas.LocationSchema).toBeDefined();
        expect(schemas.CampaignSchema).toBeDefined();
    });

    it('should export ID schemas', () => {
        expect(schemas.PointIDSchema).toBeDefined();
        expect(schemas.SegmentIDSchema).toBeDefined();
        expect(schemas.ArcIDSchema).toBeDefined();
        expect(schemas.RuleIDSchema).toBeDefined();
        expect(schemas.ObjectiveIDSchema).toBeDefined();
        expect(schemas.ItemIDSchema).toBeDefined();
        expect(schemas.CharacterIDSchema).toBeDefined();
        expect(schemas.LocationIDSchema).toBeDefined();
        expect(schemas.CampaignIDSchema).toBeDefined();
    });
});
