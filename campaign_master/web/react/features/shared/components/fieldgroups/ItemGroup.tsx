import { withFieldGroup } from "../ctx";
import { Item, PREFIXES } from "../../../../schemas";
import { ObjectIDGroup } from "./ObjectIDGroup";

export const defaultValues = {
    obj_id: {
        prefix: PREFIXES.ITEM,
        numeric: 0,
    },
    name: '',
    type_: '',
    description: '',
    properties: [] as { name: string; value: string }[],
} as Item;


export const ItemGroup = withFieldGroup({
    defaultValues,
    // props: {} as Props,
    render: ({ group }) => {
        return (
            <div className="flex flex-col gap-2 relative">
                <div className="absolute top-0 right-0">
                    <group.AppField name="obj_id">
                        {(field) => <field.IDDisplayField />}
                    </group.AppField>
                </div>
                <div className="pt-8">
                    <group.AppField name="description">
                        {(field) => <field.TextAreaField label="Item Description" />}
                    </group.AppField>
                </div>
                <div>
                    <group.AppField name="type_">
                        {(field) => <field.TextField label="Item Type" />}
                    </group.AppField>
                </div>
                <div>
                    <group.AppField name="properties">
                        {(field) => (
                            <div>
                                <h3>Properties</h3>
                                {group.state.values.properties.map((_, index) => (
                                    <div key={index}>
                                        <group.AppField name={`properties[${index}]`}>
                                            {(field) => (
                                                <>
                                                    <group.AppField name={`properties[${index}].name`}>
                                                        {(field) => <field.TextField label={`Property ${index + 1}`} />}
                                                    </group.AppField>
                                                    <group.AppField name={`properties[${index}].value`}>
                                                        {(field) => <field.TextField label={`Value`} />}
                                                    </group.AppField>
                                                </>
                                            )}
                                        </group.AppField>
                                    </div>
                                ))}
                                <input type="text" placeholder="New Property Name" id="new-property-name" />
                                <button type="button" className="add-button" onClick={() => {
                                    const new_property_name_field = document.getElementById('new-property-name') as HTMLInputElement;
                                    field.pushValue({
                                        name: new_property_name_field.value || 'Unnamed Property',
                                        value: '',
                                    });
                                    new_property_name_field.value = '';
                                }}>
                                    Add Property
                                </button>
                            </div>
                        )}
                    </group.AppField>
                </div>
            </div>
        )
    }
})