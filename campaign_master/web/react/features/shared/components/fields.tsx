import { Field, Label, Description, Textarea, Input } from '@headlessui/react'

import { Point, PREFIXES } from '../../../schemas'
import { useFieldContext, useFormContext } from './ctx'

export function TextField({ label }: { label: string }) {
    // The `Field` infers that it should have a `value` type of `string`
    const field = useFieldContext<string>()
    const textId = `text-${label.replace(/\s+/g, '-').toLowerCase()}`
    const labelEl = label ? <Label className='p-2 font-bold'>{label}:</Label> : null
    return (
        <Field className='flex flex-row'>
            {labelEl}
            <Input
                id={textId}
                className='flex-1'
                value={field.state.value}
                onChange={(e) => field.handleChange(e.target.value)}
            />
        </Field>
    )
}

export function TextAreaField({ label, id, description }: { label: string, id?: string, description?: string }) {
    // The `Field` infers that it should have a `value` type of `string`
    const field = useFieldContext<string>()
    const labelEl = label ? <Label className='p-2 font-bold'>{label}:</Label> : null
    const descriptionEl = description ? <Description className='p-2 text-sm text-gray-500'>{description}</Description> : null
    return (
        <Field>
            {labelEl}
            {descriptionEl}
            <Textarea
                value={field.state.value}
                className='min-h-full min-w-full'
                onChange={(e) => field.handleChange(e.target.value)}
            />
        </Field>
    )
}

export function NumberField({ label, id }: { label: string, id?: string }) {
    // The `Field` infers that it should have a `value` type of `number`
    const field = useFieldContext<number>()
    const labelEl = label ? <Label className='p-2 font-bold'>{label}:</Label> : null
    return (
        <Field>
            {labelEl}
            <Input
                id={id}
                type="number"
                value={field.state.value}
                onChange={(e) => field.handleChange(Number(e.target.value))}
            />
        </Field>
    )
}

export function IDDisplayField() {
    const field = useFieldContext<{ prefix: string; numeric: number }>()
    return (
        <p className='p-2'>
            <span className='font-bold'>ID:</span> {field.state.value.prefix}-{field.state.value.numeric}
        </p>
    )
}

export function NameValueCombo() {
    const field = useFieldContext<{ name: string; value: number }>()
    return (
        <div className="name-value-combo">
            <input type="text" value={field.state.value.name} onChange={(e) => field.handleChange({ ...field.state.value, name: e.target.value })} />
            <input type="number" value={field.state.value.value} onChange={(e) => field.handleChange({ ...field.state.value, value: Number(e.target.value) })} />
        </div>
    )
}

export function PointSelectField({ label, points, id }: { label: string, points?: Array<Point>, id?: string }) {
    const field = useFieldContext<{ prefix: string; numeric: number }>()
    return (
        <>
            <label htmlFor={id}>{label}:</label>
            <select
                id={id}
                value={field.state.value.numeric}
                onChange={(e) => {
                    field.handleChange({
                        prefix: PREFIXES.POINT,
                        numeric: Number(e.target.value),
                    })
                    console.log('Selected point ID:', e.target.value)
                }
                }>
                {points?.map((point, index) => (
                    <option key={index} value={point.obj_id.numeric}>
                        {point.obj_id.prefix}-{point.obj_id.numeric} ({point.name})
                    </option>
                ))}
            </select>
        </>
    )
}

export function SubscribeButton({ label, className }: { label: string, className?: string }) {
    const form = useFormContext()
    return (
        <form.Subscribe selector={(state) => state.isSubmitting}>
            {(isSubmitting) => (
                <button type="submit" disabled={isSubmitting} className={className}>
                    {label}
                </button>
            )}
        </form.Subscribe>
    )
}