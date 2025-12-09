
import { useStore } from '@tanstack/react-form'
import { useFieldContext, useFormContext, useAppForm_RT } from './ctx'
import type { AnyID, Arc, CampaignPlan, Point, Segment, PREFIXES_T } from '../../../schemas'
import { PREFIX_TO_NAME, PREFIXES } from '../../../schemas'
// import type { UpdateMetaOptions } from '@tanstack/react-form'



export const TextField = ({ label, prior_prefix }: { label: string; prior_prefix?: string }) => {
    const field = useFieldContext<string>()
    const errors = useStore(
        field.store,
        (state) => state.meta.errors
    )

    // const style = useFormContext()?.formProps?.errorMessageStyle

    return (
        <div>
            <label>
                <div>{label}</div>
                <input
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                    onBlur={field.handleBlur}
                />
            </label>
            {errors.map((error: string) => (
                <div key={error} style={{ color: 'red' }}>
                    {error}
                </div>
            ))}
        </div>
    )
}

export const SubscribeButton = ({ label }: { label: string }) => {
    const form = useFormContext()
    return (
        <form.Subscribe selector={(state) => state.isSubmitting}>
            {(isSubmitting) => <button disabled={isSubmitting}>{label}</button>}
        </form.Subscribe>
    )
}

export const IDField = ({ label, prefix, prior_prefix }: { label?: string; prefix: PREFIXES_T; prior_prefix?: string }) => {
    // Prefix is passed as a prop, user only has access to edit numeric part
    // const field = useFieldContext<{ numeric: number }>()
    const field = useFieldContext<AnyID>()
    // const form = field.form as useAppForm_RT
    const humanLabel = label || `${PREFIX_TO_NAME[prefix]} ID`
    return (
        <div>
            <label>
                <div>{humanLabel}</div>
                <input
                    value={`${prefix}-${field.state.value?.numeric}`}
                    onChange={(e) => {
                        const [, numeric] = e.target.value.split('-')
                        console.log('IDField onChange:', e.target.value, prefix, numeric)
                        field.handleChange({ prefix, numeric: parseInt(numeric) })
                    }}
                />
            </label>
        </div>
    )
}


export const PointField = ({ label }: { label: string }) => {
    const field = useFieldContext<Point>()
    const form = field.form as useAppForm_RT
    return (
        <div>
            <h3>{label}</h3>
            <form.AppField
                name="obj_id"
                children={(subField) => <subField.IDField prefix={PREFIXES.POINT} label="Point ID" />}
            />
            <form.AppField
                name="name"
                children={(subField) => <subField.TextField label="Name" />}
            />
            <form.AppField
                name="description"
                children={(subField) => <subField.TextField label="Description" />}
            />
            <form.AppField
                name="objective"
                children={(subField) => <subField.IDField prefix={PREFIXES.OBJECTIVE} label="Objective ID" />}
            />
        </div>
    )
}

export const SegmentField = ({ label }: { label: string }) => {
    const field = useFieldContext<Segment>()
    const form = field.form as useAppForm_RT
    return (
        <div>
            <h3>{label}</h3>
            <form.AppField
                name="obj_id"
                children={(subField) => <subField.IDField prefix={PREFIXES.SEGMENT} label="Segment ID" />}
            />
            <form.AppField
                name="name"
                children={(subField) => <subField.TextField label="Name" />}
            />
            <form.AppField
                name="description"
                children={(subField) => <subField.TextField label="Description" />}
            />
            <form.AppField
                name="start"
                children={(subField) => <subField.PointField label="Start Point" />}
            />
            <form.AppField
                name="end"
                children={(subField) => <subField.PointField label="End Point" />}
            />
        </div>
    )
}

export const ArcField = ({ label }: { label: string }) => {
    const field = useFieldContext<Arc>()
    const form = field.form as useAppForm_RT
    return (
        <div>
            <h3>{label}</h3>
            <form.AppField
                name="obj_id"
                children={(subField) => <subField.IDField prefix={PREFIXES.ARC} label="Arc ID" />}
            />
            <form.AppField
                name="name"
                children={(subField) => <subField.TextField label="Name" />}
            />
            <form.AppField
                name="description"
                children={(subField) => <subField.TextField label="Description" />}
            />
            <form.AppField
                name="segments"
                mode="array"
                children={(subField) => <subField.SegmentField label="Segments" />}
            />
        </div>
    )
}

export const CampaignPlanField = ({ label }: { label: string }) => {
    const field = useFieldContext<CampaignPlan>()
    const form = field.form as useAppForm_RT
    console.log(`CampaignPlan values in Field:`, field.state.value)
    return (
        <div>
            <h2>{label}</h2>
            <form.AppField
                name="obj_id"
                children={(idField) => <idField.IDField prefix={PREFIXES.CAMPAIGN_PLAN} label="Campaign Plan ID" />}
            />
            <form.AppField
                name="title"
                children={(titleField) => <titleField.TextField label="Title" />}
            />
            <form.AppField
                name="version"
                children={(versionField) => <versionField.TextField label="Version" />}
            />
            <form.AppField
                name="setting"
                children={(settingField) => <settingField.TextField label="Setting" />}
            />
            <form.AppField
                name="summary"
                children={(summaryField) => <summaryField.TextField label="Summary" />}
            />
            <form.AppField
                name="storypoints"
                mode="array"
                children={(arcField) => <arcField.ArcField label="Storypoints (Arcs)" />}
            />
        </div>
    )
}

export const defaultPointValues: Point = {
    obj_id: { prefix: PREFIXES.POINT, numeric: 0 },
    name: 'point name',
    description: 'point description',
    objective: { prefix: PREFIXES.OBJECTIVE, numeric: 0 },
}

export const defaultSegmentValues: Segment = {
    obj_id: { prefix: PREFIXES.SEGMENT, numeric: 0 },
    name: 'segment name',
    description: 'segment description',
    start: defaultPointValues,
    end: defaultPointValues,
}

export const defaultArcValues: Arc = {
    obj_id: { prefix: PREFIXES.ARC, numeric: 0 },
    name: 'arc name',
    description: 'arc description',
    segments: [defaultSegmentValues],
}

export const defaultCampaignPlanValues: CampaignPlan = {
    obj_id: {
        prefix: PREFIXES.CAMPAIGN_PLAN,
        numeric: 0,
    },
    title: 'campaign plan title',
    version: '0.1',
    setting: 'Dark Fantasy',
    summary: 'Story summary goes here.',
    storypoints: [
        defaultArcValues,
    ],
    characters: [],
    locations: [],
    items: [],
    rules: [],
    objectives: [],
}


