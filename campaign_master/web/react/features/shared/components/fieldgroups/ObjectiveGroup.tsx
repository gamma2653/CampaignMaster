import { useCallback } from 'react';
import { withFieldGroup } from '../ctx';
import { Objective, PREFIXES } from '../../../../schemas';
import type { CampaignContext } from '../../../ai/types';

export const defaultValues = {
  obj_id: {
    prefix: PREFIXES.OBJECTIVE,
    numeric: 0,
  },
  description: '',
  components: [],
  prerequisites: [],
} as Objective;

// type Props = {
//     classNames?: {
//         all?: string;
//         obj_id?: string;
//         description?: string;
//         components?: string;
//         prerequisites?: string;
//     }
// }

export const ObjectiveGroup = withFieldGroup({
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

    return (
      <div className="flex flex-col gap-2">
        <div className="ml-auto z-50">
          <group.AppField name="obj_id">
            {(field) => <field.IDDisplayField />}
          </group.AppField>
        </div>
        <div>
          <group.AppField name="description">
            {(field) => (
              <field.AITextAreaField
                label="Objective Description"
                fieldName="description"
                entityType="Objective"
                getCampaignContext={getCampaignContext}
              />
            )}
          </group.AppField>
        </div>
        <div>
          <group.AppField name="components" mode="array">
            {(field) => (
              <div>
                <h3>Components</h3>
                {group.state.values.components.map((_, index) => (
                  <div key={index} className="border p-2 mb-2">
                    <h4>Component {index + 1}</h4>
                    <group.AppField name={`components[${index}]`}>
                      {(field) => (
                        <field.TextField label={`Component ${index + 1}`} />
                      )}
                    </group.AppField>
                  </div>
                ))}
                <button
                  type="button"
                  className="add-button"
                  onClick={() => field.pushValue('')}
                >
                  Add Component
                </button>
              </div>
            )}
          </group.AppField>
        </div>
        <div>
          <group.AppField name="prerequisites" mode="array">
            {(field) => (
              <div>
                <h3>Prerequisites</h3>
                {group.state.values.prerequisites.map((_, index) => (
                  <div
                    key={index}
                    style={{
                      border: '1px solid #ccc',
                      padding: '10px',
                      marginBottom: '10px',
                    }}
                  >
                    <h4>Prerequisite {index + 1}</h4>
                    <group.AppField name={`prerequisites[${index}]`}>
                      {(field) => (
                        <field.TextField label={`Prerequisite ${index + 1}`} />
                      )}
                    </group.AppField>
                  </div>
                ))}
                <button
                  type="button"
                  className="add-button"
                  onClick={() => field.pushValue('')}
                >
                  Add Prerequisite
                </button>
              </div>
            )}
          </group.AppField>
        </div>
      </div>
    );
  },
});
