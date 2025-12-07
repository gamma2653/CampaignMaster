import { useStore } from '@tanstack/react-form'
import { fieldContext, useFieldContext, formContext, useFormContext } from './ctx'
import type { PREFIXES_T } from '../../../schemas'

export function TextField({ label }: { label: string }) {
    // const field = useFieldContext<string>()

    // const errors = useStore(field.store, (state) => state.meta.errors)
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

export function SubscribeButton({ label }: { label: string }) {
    const form = useFormContext()
    return (
        <form.Subscribe selector={(state) => state.isSubmitting}>
            {(isSubmitting) => <button disabled={isSubmitting}>{label}</button>}
        </form.Subscribe>
    )
}

export function IDField({ label, prefix }: { label: string; prefix: PREFIXES_T }) {
    // Prefix is passed as a prop, user only has access to edit numeric part
    const field = useFieldContext<{ numeric: number }>()
    return (
        <div>
            <label>
                <div>{label}</div>
                <input
                    value={`${prefix}-${field.state.value.numeric}`}
                    onChange={(e) => {
                        const [, numeric] = e.target.value.split('-')
                        field.handleChange({ numeric: Number(numeric) })
                    }}
                />
            </label>
        </div>
    )
}