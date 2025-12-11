import { withFieldGroup } from "../ctx";
import { Item, PREFIXES } from "../../../../schemas";
import { ObjectIDGroup } from "./ObjectIDGroup";

export const defaultValues = {
    obj_id: {
        prefix: PREFIXES.ITEM,
        numeric: 0,
    },
    type_: '',
    description: '',
    properties: {} as Record<string, string>,
} as Item


export const ItemGroup = withFieldGroup({
    defaultValues,
    render: ({ group }) => {
        return (
            <div>
                <ObjectIDGroup
                    form={group}
                    fields="obj_id"
                />
                <group.AppField name="description">
                    {(field) => <field.TextField label="Item Description" />}
                </group.AppField>
                <group.AppField name="type_">
                    {(field) => <field.TextField label="Item Type" />}
                </group.AppField>
                <group.AppField name="properties">
                    {(field) => (
                        <div>
                            <h3>Properties</h3>
                            {Object.keys(group.state.values.properties).map((key, index) => (
                                <div key={index} style={{ border: '1px solid #ccc', padding: '10px', marginBottom: '10px' }}>
                                    <h4>Property {index + 1}</h4>
                                    <group.AppField name={`properties.${key}`}>
                                        {(field) => (
                                            <>
                                                <field.TextField label={`Property ${index + 1}`} />
                                                <field.TextField label={`Value`} />
                                            </>
                                        )}
                                    </group.AppField>
                                </div>
                            ))}
                            <button type="button" onClick={() => field.handleChange({
                                ...group.state.values.properties,
                                [`property_${Object.keys(group.state.values.properties).length + 1}`]: '',
                            })}>
                                Add Property
                            </button>
                        </div>
                    )}
                </group.AppField>
            </div>
        )
    }
})