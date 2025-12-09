
import { formOptions, useStore } from '@tanstack/react-form'
import { useFieldContext, useFormContext, useAppForm_RT, withForm } from './ctx'
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


