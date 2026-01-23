import { withFieldGroup } from '../ctx';
import { Arc, Point, PREFIXES } from '../../../../schemas';
import {
  SegmentGroup,
  defaultValues as segDefaultValues,
} from './SegmentGroup';

export const defaultValues = {
  obj_id: { prefix: PREFIXES.ARC, numeric: 0 },
  name: '',
  description: '',
  segments: [],
} as Arc;

type Props = {
  points: Array<Point>;
  // classNames?: {
  //     all?: string;
  //     obj_id?: string;
  //     name?: string;
  //     description?: string;
  //     segments?: string;
  // }
};

export const ArcGroup = withFieldGroup({
  defaultValues,
  props: {} as Props,
  render: ({ group, points }) => {
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
                label="Arc Name"
                fieldName="name"
                entityType="Arc"
              />
            )}
          </group.AppField>
        </div>
        <div>
          <group.AppField name="description">
            {(field) => (
              <field.AITextAreaField
                label="Arc Description"
                fieldName="description"
                entityType="Arc"
              />
            )}
          </group.AppField>
        </div>
        <div>
          <group.AppField name="segments" mode="array">
            {(field) => (
              <div>
                <h3 className="text-lg">Segments</h3>
                {group.state.values.segments.map((_, index) => (
                  <div key={index} className="border p-2 mb-2">
                    {/* <h4>Segment {index + 1}</h4> */}
                    <SegmentGroup
                      form={group}
                      fields={`segments[${index}]`}
                      points={points}
                    />
                  </div>
                ))}
                <button
                  type="button"
                  className="add-button"
                  onClick={() => {
                    field.pushValue(segDefaultValues);
                  }}
                >
                  Add Segment
                </button>
              </div>
            )}
          </group.AppField>
        </div>
      </div>
    );
  },
});
