import { z } from 'zod'

// For API data validation and type safety

// Should match models in campaign_master/content/planning.py, etc.

// HACK: Using a constant object to define prefixes for ID types, while also defining a TypeScript interface for type safety
//  Necessary for endpoint generation in `query.tsx`
// NOTE: Must be a bijection (one-to-one mapping) between names and prefix literals
export const PREFIXES = {
    MISC: 'MISC',
    RULE: 'R',
    OBJECTIVE: 'O',
    POINT: 'P',
    SEGMENT: 'S',
    ARC: 'A',
    ITEM: 'I',
    CHARACTER: 'C',
    LOCATION: 'L',
    CAMPAIGN: 'CampPlan',
} as const
// Zod prototype schemas
const AnyIDSchema = z.object({
    numeric: z.number().int().nonnegative().catch(0).default(0),
    prefix: z.string().min(1).catch(PREFIXES.MISC).default(PREFIXES.MISC),
})

const RuleIDSchema = AnyIDSchema.extend({
    prefix: z.literal(PREFIXES.RULE),
})
const ObjectiveIDSchema = AnyIDSchema.extend({
    prefix: z.literal(PREFIXES.OBJECTIVE),
})
const PointIDSchema = AnyIDSchema.extend({
    prefix: z.literal(PREFIXES.POINT),
})
const SegmentIDSchema = AnyIDSchema.extend({
    prefix: z.literal(PREFIXES.SEGMENT),
})
const ArcIDSchema = AnyIDSchema.extend({
    prefix: z.literal(PREFIXES.ARC),
})
const ItemIDSchema = AnyIDSchema.extend({
    prefix: z.literal(PREFIXES.ITEM),
})
const CharacterIDSchema = AnyIDSchema.extend({
    prefix: z.literal(PREFIXES.CHARACTER),
})
const LocationIDSchema = AnyIDSchema.extend({
    prefix: z.literal(PREFIXES.LOCATION),
})
const CampaignIDSchema = AnyIDSchema.extend({
    prefix: z.literal(PREFIXES.CAMPAIGN),
})


export const ObjectSchema = z.object({
    obj_id: AnyIDSchema,
})

export const RuleSchema = ObjectSchema.extend({
    obj_id: RuleIDSchema,
    description: z.string().default(''),
    effect: z.string().default(''),
    components: z.array(z.string()).default([]),
})

export const ObjectiveSchema = ObjectSchema.extend({
    obj_id: ObjectiveIDSchema,
    description: z.string().default(''),
    components: z.array(z.string()).default([]),
    prerequisites: z.array(z.string()).default([]),
})

export const PointSchema = ObjectSchema.extend({
    obj_id: PointIDSchema,
    name: z.string().min(1).catch('Unnamed Point').default('Unnamed Point'),
    description: z.string().min(1).catch('No description').default('No description'),
    objective: z.optional(ObjectiveIDSchema),
})

export const SegmentSchema = ObjectSchema.extend({
    obj_id: SegmentIDSchema,
    name: z.string().min(1).catch('Unnamed Segment').default('Unnamed Segment'),
    description: z.string().min(1).catch('No description').default('No description'),
    start: PointSchema,
    end: PointSchema,
})

export const ArcSchema = ObjectSchema.extend({
    obj_id: ArcIDSchema,
    name: z.string().min(1).catch('Unnamed Arc').default('Unnamed Arc'),
    description: z.string().min(1).catch('No description').default('No description'),
    segments: z.array(SegmentSchema),
})

export const ItemSchema = ObjectSchema.extend({
    obj_id: ItemIDSchema,
    name: z.string().min(1).catch('Unnamed Item').default('Unnamed Item'),
    type_: z.string().min(1).catch('Misc').default('Misc'),
    description: z.string().min(1).catch('No description').default('No description'),
    properties: z.map(z.string(), z.string()),
})

export const CharacterSchema = ObjectSchema.extend({
    obj_id: CharacterIDSchema,
    name: z.string().min(1).catch('Unnamed Character').default('Unnamed Character'),
    role: z.string().min(1).catch('No role').default('No role'),
    backstory: z.string().min(1).catch('No backstory').default('No backstory'),
    attributes: z.map(z.string(), z.number()),
    skills: z.map(z.string(), z.number()),
    inventory: z.array(ItemIDSchema).default([]),
})

export const LocationSchema = ObjectSchema.extend({
    obj_id: LocationIDSchema,
    name: z.string().min(1).catch('Unnamed Location').default('Unnamed Location'),
    description: z.string().min(1).catch('No description').default('No description'),
    neighboring_locations: z.array(LocationIDSchema).default([]),
    coords: z.optional(
        z.union([
            z.tuple([z.number(), z.number()]),
            z.tuple([z.number(), z.number(), z.number()]),
        ])
    )
})

export const CampaignSchema = ObjectSchema.extend({
    obj_id: CampaignIDSchema,
    title: z.string().min(1).catch('Unnamed Campaign').default('Unnamed Campaign'),
    version: z.string().min(1).catch('0.0.0').default('0.0.0'),
    setting: z.string().min(1).catch('Generic').default('Generic'),
    summary: z.string().min(1).catch('No summary').default('No summary'),
    storypoints: z.array(ArcSchema).catch([]).default([]),
    characters: z.array(CharacterSchema).catch([]).default([]),
    locations: z.array(LocationSchema).catch([]).default([]),
    items: z.array(ItemSchema).catch([]).default([]),
    rules: z.array(RuleSchema).catch([]).default([]),
    objectives: z.array(ObjectiveSchema).catch([]).default([]),
})

// Higher order type (ID)
export type AnyID = z.infer<typeof AnyIDSchema>
export type RuleID = z.infer<typeof RuleIDSchema>
export type ObjectiveID = z.infer<typeof ObjectiveIDSchema>
export type PointID = z.infer<typeof PointIDSchema>
export type SegmentID = z.infer<typeof SegmentIDSchema>
export type ArcID = z.infer<typeof ArcIDSchema>
export type ItemID = z.infer<typeof ItemIDSchema>
export type CharacterID = z.infer<typeof CharacterIDSchema>
export type LocationID = z.infer<typeof LocationIDSchema>
export type CampaignID = z.infer<typeof CampaignIDSchema>
// Lower order types
export type Object = z.infer<typeof ObjectSchema>
export type Rule = z.infer<typeof RuleSchema>
export type Objective = z.infer<typeof ObjectiveSchema>
export type Point = z.infer<typeof PointSchema>
export type Segment = z.infer<typeof SegmentSchema>
export type Arc = z.infer<typeof ArcSchema>
export type Item = z.infer<typeof ItemSchema>
export type Character = z.infer<typeof CharacterSchema>
export type Location = z.infer<typeof LocationSchema>
export type CampaignPlan = z.infer<typeof CampaignSchema>
export type AnyObject = Object | Rule | Objective | Point | Segment | Arc | Item | Character | Location | CampaignPlan

// NOTE: No equivalent for the above Higher order type (ID)
//  in Python because of the way Pydantic models are structured there.
//  Maybe there is something funky I could do with Annotated types, but not important right now.

// Example Point object
// const examplePoint: Point = PointSchema.parse({
//     obj_id: { numeric: 1 },
//     name: 'Example Point',
//     description: 'This is an example point in the campaign.',
//     objective: undefined,
// })

// Heck, a campaign plan can be initialized from scratch with just this:
// const exampleCampaignPlan: CampaignPlan = CampaignSchema.parse({
//     obj_id: { numeric: 1 },
// })


// Util function
export const getUrlSegment = (idObj: AnyID) => {
    return `${idObj.prefix.toLowerCase()}/${idObj.numeric}`
}

export default {
    AnyIDSchema,
    ObjectSchema,
    RuleIDSchema,
    RuleSchema,
    ObjectiveIDSchema,
    ObjectiveSchema,
    PointIDSchema,
    PointSchema,
    SegmentIDSchema,
    SegmentSchema,
    ArcIDSchema,
    ArcSchema,
    ItemIDSchema,
    ItemSchema,
    CharacterIDSchema,
    CharacterSchema,
    LocationIDSchema,
    LocationSchema,
    CampaignIDSchema,
    CampaignSchema,
}
