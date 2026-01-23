import { useCallback } from 'react';
import { withFieldGroup } from '../ctx';
import { Point, PREFIXES, ObjectiveID } from '../../../../schemas';
import { useObjective } from '../../../../query';
import type { CampaignContext } from '../../../ai/types';

export const defaultValues = {
  obj_id: {
    prefix: PREFIXES.POINT,
    numeric: 0,
  },
  name: '',
  description: '',
  objective: null,
} as Point;

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
    const { data: objectives, isLoading: objectivesLoading } = useObjective();

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

    return (
      <div className="flex flex-col gap-2">
        <div className="ml-auto">
          <group.AppField name="obj_id">
            {(field) => <field.IDDisplayField />}
          </group.AppField>
        </div>
        <div>
          <group.AppField name="name">
            {(field) => (
              <field.AITextField
                label="Point Name"
                fieldName="name"
                entityType="Point"
                getCampaignContext={getCampaignContext}
              />
            )}
          </group.AppField>
        </div>
        <div>
          <group.AppField name="description">
            {(field) => (
              <field.AITextAreaField
                label="Point Description"
                fieldName="description"
                entityType="Point"
                getCampaignContext={getCampaignContext}
              />
            )}
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
                  const value = e.target.value;
                  if (value === '') {
                    field.handleChange(null);
                  } else {
                    field.handleChange({
                      prefix: PREFIXES.OBJECTIVE,
                      numeric: parseInt(value),
                    } as ObjectiveID);
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
                      {obj.obj_id.prefix}-{obj.obj_id.numeric} -{' '}
                      {obj.description.substring(0, 50)}
                    </option>
                  ))
                )}
              </select>
            )}
          </group.AppField>
        </div>
      </div>
    );
  },
});
