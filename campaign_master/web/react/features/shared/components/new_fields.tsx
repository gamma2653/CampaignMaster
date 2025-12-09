
import { useStore } from '@tanstack/react-form'
import { useFieldContext, useFormContext } from './ctx'
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
                        field.handleChange({ prefix, numeric: parseInt(numeric) })
                    }}
                />
            </label>
        </div>
    )
}

export const defaultPointValues: Point = {
    obj_id: { prefix: PREFIXES.POINT, numeric: 0 },
    name: '',
    description: '',
    objective: { prefix: PREFIXES.OBJECTIVE, numeric: 0 },
}
export const defaultSegmentValues: Segment = {
    obj_id: { prefix: PREFIXES.SEGMENT, numeric: 0 },
    name: '',
    description: '',
    start: defaultPointValues,
    end: defaultPointValues,
}

export const defaultArcValues: Arc = {
    obj_id: { prefix: PREFIXES.ARC, numeric: 0 },
    name: '',
    description: '',
    segments: [defaultSegmentValues],
}

export const defaultCampaignPlanValues: CampaignPlan = {
    obj_id: {
        prefix: PREFIXES.CAMPAIGN_PLAN,
        numeric: 0,
    },
    title: '',
    version: '',
    setting: '',
    summary: '',
    storypoints: [
        defaultArcValues,
    ],
    characters: [],
    locations: [],
    items: [],
    rules: [],
    objectives: [],
}
