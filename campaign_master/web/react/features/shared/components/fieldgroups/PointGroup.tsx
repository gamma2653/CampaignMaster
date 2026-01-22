import { withFieldGroup } from "../ctx";
import { Point, PREFIXES, ObjectiveID } from "../../../../schemas";
import { useObjective } from "../../../../query";

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
//         objective?: string;
//     }
// }

export const PointGroup = withFieldGroup({
    defaultValues,
    // props: {} as Props,
    render: ({ group }) => {
        // Fetch available objectives
        const { data: objectives, isLoading: objectivesLoading } = useObjective()

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
                <div>
                    <label className="p-2 font-bold">Linked Objective:</label>
                    <group.AppField name="objective">
                        {(field) => (
                            <select
                                className="flex-1 p-2 border rounded"
                                value={field.state.value?.numeric || ''}
                                onChange={(e) => {
                                    const value = e.target.value
                                    if (value === '') {
                                        field.handleChange(null)
                                    } else {
                                        field.handleChange({
                                            prefix: PREFIXES.OBJECTIVE,
                                            numeric: parseInt(value),
                                        } as ObjectiveID)
                                    }
                                }}
                            >
                                <option value="">None</option>
                                {objectivesLoading ? (
                                    <option disabled>Loading objectives...</option>
                                ) : (
                                    objectives?.map((obj) => (
                                        <option
                                            key={`${obj.obj_id.prefix}-${obj.obj_id.numeric}`}
                                            value={obj.obj_id.numeric}
                                        >
                                            {obj.obj_id.prefix}-{obj.obj_id.numeric} - {obj.description.substring(0, 50)}
                                        </option>
                                    ))
                                )}
                            </select>
                        )}
                    </group.AppField>
                </div>
            </div>
        )
    }
})