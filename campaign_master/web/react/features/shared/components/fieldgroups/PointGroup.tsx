import { withFieldGroup } from "../ctx";
import { Point, PREFIXES } from "../../../../schemas";
import { ObjectIDGroup } from "./ObjectIDGroup";

const defaultValues = {
    obj_id: {
        prefix: PREFIXES.POINT,
        numeric: 0,
    },
    name: '',
    description: '',
    objective: null,
} as Point


export const PointGroup = withFieldGroup({
    defaultValues,
    render: ({ group }) => {
        return (
            <div>
                <ObjectIDGroup
                    form={group}
                    fields="obj_id"
                />
                <group.AppField name="name">
                    {(field) => <field.TextField label="Point Name" />}
                </group.AppField>
                <group.AppField name="description">
                    {(field) => <field.TextField label="Point Description" />}
                </group.AppField>
            </div>
        )
    }
})