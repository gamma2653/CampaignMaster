import { useCallback } from 'react';
import { withFieldGroup } from '../ctx';
import type { Point, Segment } from '../../../../schemas';
import { PREFIXES } from '../../../../schemas';
import type { CampaignContext } from '../../../ai/types';

export const defaultValues = {
  obj_id: { prefix: PREFIXES.SEGMENT, numeric: 0 },
  name: '',
  description: '',
  start: { prefix: PREFIXES.POINT, numeric: 0 },
  end: { prefix: PREFIXES.POINT, numeric: 1 },
} as Segment;

type Props = {
  points: Array<Point>;
  // classNames?: {
  //     all?: string;
  //     obj_id?: string;
  //     name?: string;
  //     description?: string;
  //     start?: string;
  //     end?: string;
  // }
};

export const SegmentGroup = withFieldGroup({
  defaultValues,
  props: {} as Props,
  render: ({ group, points }) => {
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
                label="Segment Name"
                fieldName="name"
                entityType="Segment"
                getCampaignContext={getCampaignContext}
              />
            )}
          </group.AppField>
        </div>
        <div>
          <group.AppField name="description">
            {(field) => (
              <field.AITextAreaField
                label="Segment Description"
                fieldName="description"
                entityType="Segment"
                getCampaignContext={getCampaignContext}
              />
            )}
          </group.AppField>
        </div>
        <div>
          <group.AppField name="start">
            {(field) => (
              <field.PointSelectField label="Start Point" points={points} />
            )}
          </group.AppField>
        </div>
        <div>
          <group.AppField name="end">
            {(field) => (
              <field.PointSelectField label="End Point" points={points} />
            )}
          </group.AppField>
        </div>
      </div>
    );
  },
});
