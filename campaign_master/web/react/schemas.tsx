import { z } from 'zod'

// For API data validation and type safety

// Should match types in campaign_master/content/planning.py, etc.

export const IDSchema = z.object({
    numeric: z.number().int().nonnegative(),
    prefix: z.string().min(1),
})

export const AbstractObjectSchema = z.object({
    obj_id: IDSchema
})

export const RuleSchema = AbstractObjectSchema.extend({
    description: z.string().min(1),
    effect: z.string().min(1),
    components: z.array(z.string()),
})

export const ObjectiveSchema = AbstractObjectSchema.extend({
    description: z.string().min(1),
    components: z.array(z.string()),
    prequisites: z.array(z.string().min(1)),
})

export const PointSchema = AbstractObjectSchema.extend({
    name: z.string().min(1),
    description: z.string().min(1),
    objective: z.optional(IDSchema),
})

export const SegmentSchema = AbstractObjectSchema.extend({
    name: z.string().min(1),
    description: z.string().min(1),
    start: PointSchema,
    end: PointSchema,
})

export const ArcSchema = AbstractObjectSchema.extend({
    name: z.string().min(1),
    description: z.string().min(1),
    segments: z.array(SegmentSchema),
})

export const ItemSchema = AbstractObjectSchema.extend({
    name: z.string().min(1),
    type_: z.string().min(1),
    description: z.string().min(1),
    properties: z.map(z.string(), z.string()),
})

export const CharacterSchema = AbstractObjectSchema.extend({
    name: z.string().min(1),
    role: z.string().min(1),
    backstory: z.string().min(1),
    attributes: z.map(z.string(), z.number()),
    skills: z.map(z.string(), z.number()),
    storylines: z.array(IDSchema),
    inventory: z.array(IDSchema),
})

export const LocationSchema = AbstractObjectSchema.extend({
    name: z.string().min(1),
    description: z.string().min(1),
    neighboring_locations: z.array(IDSchema),
    coords: z.optional(
        z.union([
            z.tuple([z.number(), z.number()]),
            z.tuple([z.number(), z.number(), z.number()]),
        ])
    )
})

export const CampaignSchema = AbstractObjectSchema.extend({
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
