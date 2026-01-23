import { useCallback } from 'react';
import { withFieldGroup } from '../ctx';
import { Location, PREFIXES } from '../../../../schemas';
import type { CampaignContext } from '../../../ai/types';

export const defaultValues = {
  obj_id: {
    prefix: PREFIXES.LOCATION,
    numeric: 0,
  },
  name: '',
  description: '',
  coords: [0, 0],
} as Location;

// type Props = {
//     classNames?: {
//         all?: string;
//         obj_id?: string;
//         name?: string;
//         description?: string;
//         coords?: string;
//     }
// }

export const LocationGroup = withFieldGroup({
  defaultValues,
  // props: {} as Props,
  render: ({ group }) => {
    // Access parent form's values for campaign context
    const getCampaignContext = useCallback((): CampaignContext => {
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

    let altitude = null;
    // Populate altitude field if coords has length 3
    if (group.state.values.coords?.length === 3) {
      altitude = (
        <group.AppField name="coords[2]">
          {(subField) => <subField.NumberField label="Altitude" />}
        </group.AppField>
      );
    }
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
                label="Location Name"
                fieldName="name"
                entityType="Location"
                getCampaignContext={getCampaignContext}
              />
            )}
          </group.AppField>
        </div>
        <div>
          <group.AppField name="description">
            {(field) => (
              <field.AITextAreaField
                label="Location Description"
                fieldName="description"
                entityType="Location"
                getCampaignContext={getCampaignContext}
              />
            )}
          </group.AppField>
        </div>
        <div>
          <group.AppField name="coords">
            {() => (
              <div>
                <h3>Coordinates</h3>
                <group.AppField name="coords[0]">
                  {(subField) => <subField.NumberField label="Latitude" />}
                </group.AppField>
                <group.AppField name="coords[1]">
                  {(subField) => <subField.NumberField label="Longitude" />}
                </group.AppField>
                {altitude}
              </div>
            )}
          </group.AppField>
        </div>
      </div>
    );
  },
});
