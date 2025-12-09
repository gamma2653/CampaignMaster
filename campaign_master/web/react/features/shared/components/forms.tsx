import { formOptions, createFieldMap } from '@tanstack/react-form'
import { useAppForm, withForm } from './ctx'
import type { AnyID, CampaignPlan } from '../../../schemas'
import { PREFIXES } from '../../../schemas'


const idFormOpts = formOptions({
    defaultValues: { prefix: PREFIXES.MISC, numeric: 0 } as AnyID,
})

export const IDField = withForm({
    ...idFormOpts,
    render: function IDField({ form }) {
        return (
            <div>
                Prefix field to be added
            </div>
        )
    },
})

const pointFormOpts = formOptions({
    defaultValues: {
        "obj_id": { prefix: PREFIXES.POINT, numeric: 0 },
        "name": "",
        "description": "",
        "objective": null,
    },
})

export const PointForm = withForm({
    ...pointFormOpts,
    render: function PointForm({ form }) {
        return (
            <div>
                Point form to be added
            </div>
        )
    },
})

const segmentFormOpts = formOptions({
    defaultValues: {
        "obj_id": { prefix: PREFIXES.SEGMENT, numeric: 0 },
        "name": "",
        "description": "",
        "start": null,
        "end": null,
    },
})

export const SegmentForm = withForm({
    ...segmentFormOpts,
    render: function SegmentForm({ form }) {
        return (
            <div>
                Segment form to be added
            </div>
        )
    },
})

const arcFormOpts = formOptions({
    defaultValues: {
        "obj_id": { prefix: PREFIXES.ARC, numeric: 0 },
        "name": "",
        "description": "",
        "segments": [],
    },
})

export const ArcForm = withForm({
    ...arcFormOpts,
    render: function ArcForm({ form }) {
        return (
            <div>
                Arc form to be added
            </div>
        )
    }
})

const campaignPlanFormOpts = formOptions({
    defaultValues: {
        "obj_id": { prefix: PREFIXES.CAMPAIGN_PLAN, numeric: 0 },
        "title": "",
        "version": "0.0.0",
        "setting": "",
        "summary": "",
        "storypoints": [],
        "characters": [],
        "locations": [],
        "items": [],
        "rules": [],
        "objectives": [],
    } as CampaignPlan,
})

export const CampaignPlanForm = () => {
    const form = useAppForm({
        ...campaignPlanFormOpts,
    })
    return (
        <IDField form={form} />
    )
}
