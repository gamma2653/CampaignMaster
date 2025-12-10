import { withFieldGroup } from "../ctx";
import { Segment, PREFIXES } from "../../../../schemas";
import { ObjectIDGroup } from "./ObjectIDGroup";
import { PointGroup } from "./PointGroup";

export const defaultValues = {
    obj_id: { prefix: PREFIXES.SEGMENT, numeric: 0 },
    name: '',
    description: '',
    start: {
        obj_id: { prefix: PREFIXES.POINT, numeric: 0 },
    },
    end: {
        obj_id: { prefix: PREFIXES.POINT, numeric: 1 },
    },
} as Segment


export const SegmentGroup = withFieldGroup({
    defaultValues,
    render: ({ group }) => {
        return (
            <div>
                <ObjectIDGroup
                    form={group}
                    fields="obj_id"
                />
                <group.AppField name="name">
                    {(field) => <field.TextField label="Segment Name" />}
                </group.AppField>
                <group.AppField name="description">
                    {(field) => <field.TextField label="Segment Description" />}
                </group.AppField>
                <PointGroup
                    form={group}
                    fields="start"
                />
                <PointGroup
                    form={group}
                    fields="end"
                />
            </div>
        )
    }
})