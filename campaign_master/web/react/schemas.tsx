import { z } from 'zod'

// For API data validation and type safety

// Should match models in campaign_master/content/planning.py, etc.

const DEFAULT_PREFIX = 'MISC'

export const AnyIDSchema = z.object({
    numeric: z.number().int().nonnegative().catch(0).default(0),
    prefix: z.string().min(1).catch(DEFAULT_PREFIX).default(DEFAULT_PREFIX),
})
export const RuleIDSchema = AnyIDSchema.extend({
    prefix: z.literal('R'),
})
export const ObjectiveIDSchema = AnyIDSchema.extend({
    prefix: z.literal('O'),
})
export const PointIDSchema = AnyIDSchema.extend({
    prefix: z.literal('P'),
})
export const SegmentIDSchema = AnyIDSchema.extend({
    prefix: z.literal('S'),
})
export const ArcIDSchema = AnyIDSchema.extend({
    prefix: z.literal('A'),
})
export const ItemIDSchema = AnyIDSchema.extend({
    prefix: z.literal('I'),
})
export const CharacterIDSchema = AnyIDSchema.extend({
    prefix: z.literal('C'),
})
export const LocationIDSchema = AnyIDSchema.extend({
    prefix: z.literal('L'),
})
export const CampaignIDSchema = AnyIDSchema.extend({
    prefix: z.literal('CampPlan'),
})


export const ObjectSchema = z.object({
    obj_id: AnyIDSchema
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
    objective: z.optional(AnyIDSchema),
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
    storylines: z.array(AnyIDSchema).default([]),
    inventory: z.array(AnyIDSchema).default([]),
})

export const LocationSchema = ObjectSchema.extend({
    obj_id: LocationIDSchema,
    name: z.string().min(1).catch('Unnamed Location').default('Unnamed Location'),
    description: z.string().min(1).catch('No description').default('No description'),
    neighboring_locations: z.array(AnyIDSchema).default([]),
    coords: z.optional(
        z.union([
            z.tuple([z.number(), z.number()]),
            z.tuple([z.number(), z.number(), z.number()]),
        ])
    )
})

export const CampaignSchema = ObjectSchema.extend({
    obj_id: CampaignIDSchema,
    title: z.string().min(1),
    version: z.string().min(1),
    setting: z.string().min(1),
    summary: z.string().min(1),
    storypoints: z.array(ArcSchema),
    characters: z.array(CharacterSchema),
    locations: z.array(LocationSchema),
    items: z.array(ItemSchema),
    rules: z.array(RuleSchema),
    objectives: z.array(ObjectiveSchema),
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
