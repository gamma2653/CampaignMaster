import { Point, PREFIXES } from '../../../schemas'
import { useFieldContext, useFormContext } from './ctx'

export function TextField({ label }: { label: string }) {
  // The `Field` infers that it should have a `value` type of `string`
  const field = useFieldContext<string>()
  return (
    <label>
      <span>{label}</span>
      <input
        value={field.state.value}
        onChange={(e) => field.handleChange(e.target.value)}
      />
    </label>
  )
}

export function NumberField({ label }: { label: string }) {
  // The `Field` infers that it should have a `value` type of `number`
  const field = useFieldContext<number>()
  return (
    <label>
      <span>{label}</span>
      <input
        type="number"
        value={field.state.value}
        onChange={(e) => field.handleChange(Number(e.target.value))}
      />
    </label>
  )
}

export function IDDisplayField() {
  const field = useFieldContext<{ prefix: string; numeric: number }>()
  return (
    <div>
      <span>
        ID: {field.state.value.prefix}-{field.state.value.numeric}
      </span>
    </div>
  )
}

export function PointSelectField({ label, points }: { label: string, points?: Array<Point> }) {
  const field = useFieldContext<{ prefix: string; numeric: number }>()
  return (
    <label>
      <span>{label}</span>
      <select
        value={field.state.value.numeric}
        onChange={(e) =>
          field.handleChange({
            prefix: PREFIXES.POINT,
            numeric: Number(e.target.value),
          })
        }>
        {points?.map((point) => (
          <option key={point.obj_id.numeric} value={point.obj_id.numeric}>
            {point.obj_id.prefix}-{point.obj_id.numeric} ({point.name})
          </option>
        ))}
      </select>
    </label>
  )
}

export function SubscribeButton({ label }: { label: string }) {
  const form = useFormContext()
  return (
    <form.Subscribe selector={(state) => state.isSubmitting}>
      {(isSubmitting) => (
        <button type="submit" disabled={isSubmitting}>
          {label}
        </button>
      )}
    </form.Subscribe>
  )
}