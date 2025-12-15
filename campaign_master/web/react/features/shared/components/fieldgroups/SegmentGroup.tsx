import { withFieldGroup } from "../ctx";
import type { Point, Segment } from "../../../../schemas";
import { PREFIXES } from "../../../../schemas";
import { PointGroup } from "./PointGroup";

export const defaultValues = {
    obj_id: { prefix: PREFIXES.SEGMENT, numeric: 0 },
    name: '',
    description: '',
    start: { prefix: PREFIXES.POINT, numeric: 0 },
    end: { prefix: PREFIXES.POINT, numeric: 1 },
} as Segment


export const SegmentGroup = withFieldGroup({
    defaultValues,
    props: {
        points: [] as Array<Point>,
    },
    render: ({ group, points }) => {
        return (
            <div className="segment">
                <group.AppField name="obj_id">
                    {(field) => <field.IDDisplayField />}
                </group.AppField>
                <group.AppField name="name">
                    {(field) => <field.TextField label="Segment Name" />}
                </group.AppField>
                <group.AppField name="description">
                    {(field) => <field.TextAreaField label="Segment Description" />}
                </group.AppField>
                <group.AppField name="start">
                    {(field) => <field.PointSelectField label="Start Point" points={points} />}
                </group.AppField>
                <group.AppField name="end">
                    {(field) => <field.PointSelectField label="End Point" points={points} />}
                </group.AppField>
            </div>
        )
    }
})