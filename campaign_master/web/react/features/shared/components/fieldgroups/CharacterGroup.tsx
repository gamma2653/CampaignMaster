import { withFieldGroup } from "../ctx";
import { Character, ItemID, PREFIXES } from "../../../../schemas";
import { ObjectIDGroup } from "./ObjectIDGroup";

export const defaultValues = {
    obj_id: {
        prefix: PREFIXES.CHARACTER,
        numeric: 0,
    },
    name: '',
    role: '',
    backstory: '',
    attributes: [] as { name: string; value: number }[],
    skills: [] as { name: string; value: number }[],
    inventory: [] as ItemID[],
} as Character


export const CharacterGroup = withFieldGroup({
    defaultValues,
    render: ({ group }) => {
        return (
            <div className="character">
                <group.AppField name="obj_id">
                    {(field) => <field.IDDisplayField />}
                </group.AppField>
                <group.AppField name="name">
                    {(field) => <field.TextField label="Character Name" />}
                </group.AppField>
                <group.AppField name="role">
                    {(field) => <field.TextField label="Character Role" />}
                </group.AppField>
                <group.AppField name="backstory">
                    {(field) => <field.TextAreaField label="Character Backstory" />}
                </group.AppField>
                <group.AppField name="attributes" mode="array">
                    {(field) => (
                        <div>
                            <h3>Attributes</h3>
                            {group.state.values.attributes.map((_, index) => (
                                <div key={index}>
                                    <h4>Attribute {index + 1}</h4>
                                    <group.AppField name={`attributes[${index}].name`}>
                                        {(subField) => <subField.TextField label="Attribute Name" />}
                                    </group.AppField>
                                    <group.AppField name={`attributes[${index}].value`}>
                                        {(subField) => <subField.NumberField label="Attribute Value" />}
                                    </group.AppField>
                                </div>
                            ))}
                            <input type="text" placeholder="New Attribute Name" id="new-attribute-name" />
                            <button type="button" className="add-button" onClick={() => {
                                const new_attr_name_field = document.getElementById('new-attribute-name') as HTMLInputElement;
                                field.pushValue({
                                    name: new_attr_name_field?.value || 'Unnamed Attribute',
                                    value: 0,
                                });
                                new_attr_name_field.value = '';
                            }}>
                                Add Attribute
                            </button>
                        </div>
                    )}
                </group.AppField>
                <group.AppField name="skills">
                    {(field) => (
                        <div>
                            <h3>Skills</h3>
                            {group.state.values.skills.map((_, index) => (
                                <div key={index}>
                                    <h4>Skill {index + 1}</h4>
                                    <group.AppField name={`skills[${index}].name`}>
                                        {(subField) => <subField.TextField label="Skill Name" />}
                                    </group.AppField>
                                    <group.AppField name={`skills[${index}].value`}>
                                        {(subField) => <subField.NumberField label="Skill Value" />}
                                    </group.AppField>
                                </div>
                            ))}
                            <input type="text" placeholder="New Skill Name" id="new-skill-name" />
                            <button type="button" className="add-button" onClick={() => {
                                const new_skill_name_field = document.getElementById('new-skill-name') as HTMLInputElement;
                                field.pushValue({
                                    name: new_skill_name_field?.value || 'Unnamed Skill',
                                    value: 0,
                                });
                                new_skill_name_field.value = '';
                            }}>
                                Add Skill
                            </button>
                        </div>
                    )}
                </group.AppField>
                <group.AppField name="inventory" mode="array">
                    {(field) => (
                        <div>
                            <h3>Inventory</h3>
                            {group.state.values.inventory.map((_, index) => (
                                <div key={index} style={{ border: '1px solid #ccc', padding: '10px', marginBottom: '10px' }}>
                                    <h4>Item {index + 1}</h4>
                                    <group.AppField name={`inventory[${index}]`}>
                                        {(field) => <ObjectIDGroup form={group} fields={`inventory[${index}]`} />}
                                    </group.AppField>
                                </div>
                            ))}
                            <button type="button" className="add-button" onClick={() => field.pushValue({ prefix: PREFIXES.ITEM, numeric: 0 } as ItemID)}>
                                Add Item
                            </button>
                        </div>
                    )}
                </group.AppField>
            </div>
        )
    }
})