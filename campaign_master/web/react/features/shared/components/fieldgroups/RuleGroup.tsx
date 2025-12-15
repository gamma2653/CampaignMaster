import { withFieldGroup } from "../ctx";
import { Rule, PREFIXES } from "../../../../schemas";
import { ObjectIDGroup } from "./ObjectIDGroup";

export const defaultValues = {
    obj_id: {
        prefix: PREFIXES.RULE,
        numeric: 0,
    },
    description: '',
    effect: '',
    components: [],
} as Rule


export const RuleGroup = withFieldGroup({
    defaultValues,
    render: ({ group }) => {
        return (
            <div className="rule">
                <group.AppField name="obj_id">
                    {(field) => <field.IDDisplayField />}
                </group.AppField>
                <group.AppField name="description">
                    {(field) => <field.TextAreaField label="Rule Description" />}
                </group.AppField>
                <group.AppField name="effect">
                    {(field) => <field.TextField label="Rule Effect" />}
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
                        <button type="button" className="add-button" onClick={() => field.pushValue('')}>
                            Add Component
                        </button>
                        </div>
                    )}
                </group.AppField>
            </div>
        )
    }
})