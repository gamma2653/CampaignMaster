import { useCallback } from 'react';
import { withFieldGroup } from '../ctx';
import { Item, PREFIXES } from '../../../../schemas';
import type { CampaignContext } from '../../../ai/types';

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
    // Access parent form's values for campaign context
    const getCampaignContext = useCallback((): CampaignContext => {
      const values = group.state.values as Record<string, unknown>;
      return {
        title: values.title as string | undefined,
        version: values.version as string | undefined,
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

    const getEntityId = useCallback(
      () => group.state.values.obj_id,
      [group.state.values.obj_id],
    );

    return (
      <div className="flex flex-col gap-2 relative">
        <div className="absolute top-0 right-0">
          <group.AppField name="obj_id">
            {(field) => <field.IDDisplayField />}
          </group.AppField>
        </div>
        <div className="pt-8">
          <group.AppField name="name">
            {(field) => (
              <field.AITextField
                label="Item Name"
                fieldName="name"
                getEntityId={getEntityId}
                getCampaignContext={getCampaignContext}
              />
            )}
          </group.AppField>
        </div>
        <div>
          <group.AppField name="description">
            {(field) => (
              <field.AITextAreaField
                label="Item Description"
                fieldName="description"
                getEntityId={getEntityId}
                getCampaignContext={getCampaignContext}
              />
            )}
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
                      {() => (
                        <>
                          <group.AppField name={`properties[${index}].name`}>
                            {(nameField) => (
                              <nameField.TextField
                                label={`Property ${index + 1}`}
                              />
                            )}
                          </group.AppField>
                          <group.AppField name={`properties[${index}].value`}>
                            {(valueField) => (
                              <valueField.TextField label={`Value`} />
                            )}
                          </group.AppField>
                        </>
                      )}
                    </group.AppField>
                  </div>
                ))}
                <input
                  type="text"
                  placeholder="New Property Name"
                  id="new-property-name"
                />
                <button
                  type="button"
                  className="add-button"
                  onClick={() => {
                    const new_property_name_field = document.getElementById(
                      'new-property-name',
                    ) as HTMLInputElement;
                    field.pushValue({
                      name: new_property_name_field.value || 'Unnamed Property',
                      value: '',
                    });
                    new_property_name_field.value = '';
                  }}
                >
                  Add Property
                </button>
              </div>
            )}
          </group.AppField>
        </div>
      </div>
    );
  },
});
