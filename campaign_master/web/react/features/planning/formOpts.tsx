import { formOptions } from '@tanstack/react-form'
import type { AnyID, CampaignPlan, Point, Segment } from '../../schemas'
import { PREFIXES } from '../../schemas'


export const pointOpts = formOptions({
    defaultValues: {
        obj_id: { prefix: PREFIXES.POINT, numeric: 0 },

    } as Point,
})

export const segmentOpts = formOptions({
    defaultValues: {
        obj_id: { prefix: PREFIXES.SEGMENT, numeric: 0 },
        name: '',
        description: '',
        start: pointOpts.defaultValues,
        end: {
            obj_id: { prefix: PREFIXES.POINT, numeric: 1 },
        },
    } as Segment,
})

export const arcOpts = formOptions({
    defaultValues: {
        obj_id: { prefix: PREFIXES.ARC, numeric: 0 },
        name: '',
        description: '',
        segments: [segmentOpts.defaultValues] as Segment[],
    },
})

export const campaignPlanOpts = formOptions({
    defaultValues: {
        obj_id: { prefix: PREFIXES.CAMPAIGN_PLAN, numeric: 0 } as AnyID,
        title: '',
        version: '',
        setting: '',
        summary: '',
        storypoints: [arcOpts.defaultValues],
        characters: [],
        locations: [],
        items: [],
        rules: [],
        objectives: [],

    } as CampaignPlan,
})