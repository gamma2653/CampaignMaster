import { useCallback } from 'react';
import { withFieldGroup } from '../ctx';
import { Character, ItemID, PREFIXES } from '../../../../schemas';
import { ObjectIDGroup } from './ObjectIDGroup';
import type { CampaignContext } from '../../../ai/types';

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
} as Character;

// type Props = {
//     classNames?: {
//         all?: string;
//         obj_id?: string;
//         name?: string;
//         role?: string;
//         backstory?: string;
//         attributes?: string;
//         skills?: string;
//         inventory?: string;
//     }
// }

export const CharacterGroup = withFieldGroup({
  defaultValues,
  // props: {} as Props,
  // render: ({ group, classNames }) => {
  render: ({ group }) => {
    // Access parent form's values for campaign context
    // The group here is the parent CampaignPlan form when used within CampaignPlanGroup
    const getCampaignContext = useCallback((): CampaignContext => {
      // Try to access campaign-level values from the parent form
      const values = group.state.values as Record<string, unknown>;
      return {
        title: values.title as string | undefined,
        setting: values.setting as string | undefined,
        summary: values.summary as string | undefined,
        storyline: values.storyline as CampaignContext['storyline'],
        storypoints: values.storypoints as CampaignContext['storypoints'],
        characters: values.characters as CampaignContext['characters'],
        locations: values.locations as CampaignContext['locations'],
        items: values.items as CampaignContext['items'],
        rules: values.rules as CampaignContext['rules'],
        objectives: values.objectives as CampaignContext['objectives'],
      };
    }, [group.state.values]);

    return (
      <div className="flex flex-col relative">
        <div className="absolute top-0 right-0">
          <group.AppField name="obj_id">
            {(field) => <field.IDDisplayField />}
          </group.AppField>
        </div>
        <div className="pt-8">
          <group.AppField name="name">
            {(field) => (
              <field.AITextField
                label="Character Name"
                fieldName="name"
                entityType="Character"
                getCampaignContext={getCampaignContext}
              />
            )}
          </group.AppField>
        </div>
        <div>
          <group.AppField name="role">
            {(field) => <field.TextField label="Character Role" />}
          </group.AppField>
        </div>
        <div>
          <group.AppField name="backstory">
            {(field) => (
              <field.AITextAreaField
                label="Character Backstory"
                fieldName="backstory"
                entityType="Character"
                getCampaignContext={getCampaignContext}
              />
            )}
          </group.AppField>
        </div>
        <group.AppField name="attributes" mode="array">
          {(field) => (
            <div>
              <h3>Attributes</h3>
              {group.state.values.attributes.map((_, index) => (
                <div key={index} className="border p-2 mb-2 ">
                  <h4>Attribute {index + 1}</h4>
                  <group.AppField name={`attributes[${index}].name`}>
                    {(subField) => (
                      <subField.TextField label="Attribute Name" />
                    )}
                  </group.AppField>
                  <group.AppField name={`attributes[${index}].value`}>
                    {(subField) => (
                      <subField.NumberField label="Attribute Value" />
                    )}
                  </group.AppField>
                </div>
              ))}
              <input
                type="text"
                placeholder="New Attribute Name"
                id="new-attribute-name"
              />
              <button
                type="button"
                className="add-button"
                onClick={() => {
                  const new_attr_name_field = document.getElementById(
                    'new-attribute-name',
                  ) as HTMLInputElement;
                  field.pushValue({
                    name: new_attr_name_field?.value || 'Unnamed Attribute',
                    value: 0,
                  });
                  new_attr_name_field.value = '';
                }}
              >
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
                <div key={index} className="border p-2 mb-2 ">
                  <h4>Skill {index + 1}</h4>
                  <group.AppField name={`skills[${index}].name`}>
                    {(subField) => <subField.TextField label="Skill Name" />}
                  </group.AppField>
                  <group.AppField name={`skills[${index}].value`}>
                    {(subField) => <subField.NumberField label="Skill Value" />}
                  </group.AppField>
                </div>
              ))}
              <input
                type="text"
                placeholder="New Skill Name"
                id="new-skill-name"
              />
              <button
                type="button"
                className="add-button"
                onClick={() => {
                  const new_skill_name_field = document.getElementById(
                    'new-skill-name',
                  ) as HTMLInputElement;
                  field.pushValue({
                    name: new_skill_name_field?.value || 'Unnamed Skill',
                    value: 0,
                  });
                  new_skill_name_field.value = '';
                }}
              >
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
                <div key={index} className="border p-2 mb-2 ">
                  <h4>Item {index + 1}</h4>
                  <group.AppField name={`inventory[${index}]`}>
                    {() => (
                      <ObjectIDGroup
                        form={group}
                        fields={`inventory[${index}]`}
                      />
                    )}
                  </group.AppField>
                </div>
              ))}
              <button
                type="button"
                className="add-button"
                onClick={() =>
                  field.pushValue({
                    prefix: PREFIXES.ITEM,
                    numeric: 0,
                  } as ItemID)
                }
              >
                Add Item
              </button>
            </div>
          )}
        </group.AppField>
      </div>
    );
  },
});
