import { withFieldGroup } from "../ctx";
import { Point, PREFIXES } from "../../../../schemas";
import { ObjectIDGroup } from "./ObjectIDGroup";

export const defaultValues = {
    obj_id: {
        prefix: PREFIXES.POINT,
        numeric: 0,
    },
    name: '',
    description: '',
    objective: null,
} as Point


// type Props = {
//     classNames?: {
//         all?: string;
//         obj_id?: string;
//         name?: string;
//         description?: string;
//     }
// }

export const PointGroup = withFieldGroup({
    defaultValues,
    // props: {} as Props,
    render: ({ group }) => {
        return (
            <div className="flex flex-col gap-2">
                <div className="ml-auto">
                    <group.AppField name="obj_id">
                        {(field) => <field.IDDisplayField />}
                    </group.AppField>
                </div>
                <div>
                    <group.AppField name="name">
                        {(field) => <field.TextField label="Point Name" />}
                    </group.AppField>
                </div>
                <div>
                    <group.AppField name="description">
                        {(field) => <field.TextAreaField label="Point Description" />}
                    </group.AppField>
                </div>
            </div>
        )
    }
})