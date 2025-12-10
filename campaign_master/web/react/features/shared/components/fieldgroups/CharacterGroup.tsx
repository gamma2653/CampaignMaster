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
    attributes: {} as Record<string, number>,
    skills: {} as Record<string, number>,
    inventory: [] as ItemID[],
} as Character


export const CharacterGroup = withFieldGroup({
    defaultValues,
    render: ({ group }) => {
        return (
            <div>
                <ObjectIDGroup
                    form={group}
                    fields="obj_id"
                />
                <group.AppField name="name">
                    {(field) => <field.TextField label="Character Name" />}
                </group.AppField>
                <group.AppField name="role">
                    {(field) => <field.TextField label="Character Role" />}
                </group.AppField>
                <group.AppField name="backstory">
                    {(field) => <field.TextField label="Character Backstory" />}
                </group.AppField>
                <group.AppField name="attributes">
                    {(field) => (
                        <div>
                            <h3>Attributes</h3>
                            {(Object.entries(group.state.values.attributes)).map(([key, value], index) => (
                                <div key={index} style={{ border: '1px solid #ccc', padding: '10px', marginBottom: '10px' }}>
                                    <h4>Attribute {index + 1}</h4>
                                    <group.AppField name={`attributes.${key}`}>
                                        {(field) => (
                                            <>
                                                <field.NumberField label={`${key}`} />
                                            </>
                                        )}
                                    </group.AppField>
                                </div>
                            ))}
                            <input type="text" placeholder="New Attribute Name" id="new-attribute-name" />
                            <button type="button" onClick={() => {
                                field.handleChange({
                                    ...group.state.values.attributes,
                                    [`${(document.getElementById('new-attribute-name') as HTMLInputElement).value}`]: 0,
                                });
                                // clear text field
                                (document.getElementById('new-attribute-name') as HTMLInputElement).value = ''
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
                            {(Object.entries(group.state.values.skills)).map(([key, value], index) => (
                                <div key={index} style={{ border: '1px solid #ccc', padding: '10px', marginBottom: '10px' }}>
                                    <h4>Skill {index + 1}</h4>
                                    <group.AppField name={`skills.${key}`}>
                                        {(field) => (
                                            <>
                                                <field.TextField label={`Skill ${index + 1}`} />
                                                <field.NumberField label={`Value`} />
                                            </>
                                        )}
                                    </group.AppField>
                                </div>
                            ))}
                            <button type="button" onClick={() => field.handleChange({
                                ...group.state.values.skills,
                                [`skill_${Object.keys(group.state.values.skills).length + 1}`]: 0,
                            })}>
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
                            <button type="button" onClick={() => field.pushValue({ prefix: PREFIXES.ITEM, numeric: 0 } as ItemID)}>
                                Add Item
                            </button>
                        </div>
                    )}
                </group.AppField>
            </div>
        )
    }
})