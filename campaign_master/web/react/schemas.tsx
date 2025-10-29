import { z } from 'zod'

// For API data validation and type safety

// Should match models in campaign_master/content/planning.py, etc.

export const IDSchema = z.object({
    numeric: z.number().int().nonnegative().catch(0).default(0),
    prefix: z.string().min(1).catch('MISC').default('MISC'),
})

export const AbstractObjectSchema = z.object({
    obj_id: IDSchema
})

export const RuleSchema = AbstractObjectSchema.extend({
    description: z.string().default(''),
    effect: z.string().default(''),
    components: z.array(z.string()).default([]),
})

export const ObjectiveSchema = AbstractObjectSchema.extend({
    description: z.string().default(''),
    components: z.array(z.string()).default([]),
    prequisites: z.array(z.string()).default([]),
})

export const PointSchema = AbstractObjectSchema.extend({
    name: z.string().min(1).catch('Unnamed Point').default('Unnamed Point'),
    description: z.string().min(1).catch('No description').default('No description'),
    objective: z.optional(IDSchema),
})

export const SegmentSchema = AbstractObjectSchema.extend({
    name: z.string().min(1).catch('Unnamed Segment').default('Unnamed Segment'),
    description: z.string().min(1).catch('No description').default('No description'),
    start: PointSchema,
    end: PointSchema,
})

export const ArcSchema = AbstractObjectSchema.extend({
    name: z.string().min(1).catch('Unnamed Arc').default('Unnamed Arc'),
    description: z.string().min(1).catch('No description').default('No description'),
    segments: z.array(SegmentSchema),
})

export const ItemSchema = AbstractObjectSchema.extend({
    name: z.string().min(1).catch('Unnamed Item').default('Unnamed Item'),
    type_: z.string().min(1).catch('Misc').default('Misc'),
    description: z.string().min(1).catch('No description').default('No description'),
    properties: z.map(z.string(), z.string()),
})

export const CharacterSchema = AbstractObjectSchema.extend({
    name: z.string().min(1).catch('Unnamed Character').default('Unnamed Character'),
    role: z.string().min(1).catch('No role').default('No role'),
    backstory: z.string().min(1).catch('No backstory').default('No backstory'),
    attributes: z.map(z.string(), z.number()),
    skills: z.map(z.string(), z.number()),
    storylines: z.array(IDSchema).default([]),
    inventory: z.array(IDSchema).default([]),
})

export const LocationSchema = AbstractObjectSchema.extend({
    name: z.string().min(1).catch('Unnamed Location').default('Unnamed Location'),
    description: z.string().min(1).catch('No description').default('No description'),
    neighboring_locations: z.array(IDSchema).default([]),
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

export type ID = z.infer<typeof IDSchema>
export type AbstractObject = z.infer<typeof AbstractObjectSchema>
export type Rule = z.infer<typeof RuleSchema>
export type Objective = z.infer<typeof ObjectiveSchema>
export type Point = z.infer<typeof PointSchema>
export type Segment = z.infer<typeof SegmentSchema>
export type Arc = z.infer<typeof ArcSchema>
export type Item = z.infer<typeof ItemSchema>
export type Character = z.infer<typeof CharacterSchema>
export type Location = z.infer<typeof LocationSchema>
export type Campaign = z.infer<typeof CampaignSchema>
