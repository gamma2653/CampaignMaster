import { withFieldGroup } from "../ctx";
import { Objective, PREFIXES } from "../../../../schemas";
import { ObjectIDGroup } from "./ObjectIDGroup";

export const defaultValues = {
    obj_id: {
        prefix: PREFIXES.OBJECTIVE,
        numeric: 0,
    },
    description: '',
    components: [],
    prerequisites: [],
} as Objective


export const ObjectiveGroup = withFieldGroup({
    defaultValues,
    render: ({ group }) => {
        return (
            <div className="objective">
                <group.AppField name="obj_id">
                    {(field) => <field.IDDisplayField />}
                </group.AppField>
                <group.AppField name="description">
                    {(field) => <field.TextField label="Objective Description" />}
                </group.AppField>
                <group.AppField name="components" mode="array">
                    {(field) => (
                        <div>
                            <h3>Components</h3>
                            {group.state.values.components.map((_, index) => (
                                <div key={index} style={{ border: '1px solid #ccc', padding: '10px', marginBottom: '10px' }}>
                                    <h4>Component {index + 1}</h4>
                                    <group.AppField name={`components[${index}]`}>
                                        {(field) => <field.TextField label={`Component ${index + 1}`} />}
                                    </group.AppField>
                                </div>
                            ))}
                            <button type="button" onClick={() => field.pushValue('')}>
                                Add Component
                            </button>
                        </div>
                    )}
                </group.AppField>
                <group.AppField name="prerequisites" mode="array">
                    {(field) => (
                        <div>
                            <h3>Prerequisites</h3>
                            {group.state.values.prerequisites.map((_, index) => (
                                <div key={index} style={{ border: '1px solid #ccc', padding: '10px', marginBottom: '10px' }}>
                                    <h4>Prerequisite {index + 1}</h4>
                                    <group.AppField name={`prerequisites[${index}]`}>
                                        {(field) => <field.TextField label={`Prerequisite ${index + 1}`} />}
                                    </group.AppField>
                                </div>
                            ))}
                            <button type="button" onClick={() => field.pushValue('')}>
                                Add Prerequisite
                            </button>
                        </div>
                    )}
                </group.AppField>
            </div>
        )
    }
})