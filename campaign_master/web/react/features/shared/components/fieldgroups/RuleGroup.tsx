import { withFieldGroup } from '../ctx';
import { Rule, PREFIXES } from '../../../../schemas';

export const defaultValues = {
  obj_id: {
    prefix: PREFIXES.RULE,
    numeric: 0,
  },
  description: '',
  effect: '',
  components: [],
} as Rule;

// type Props = {
//     classNames?: {
//         all?: string;
//         obj_id?: string;
//         description?: string;
//         effect?: string;
//         components?: string;
//     }
// }

export const RuleGroup = withFieldGroup({
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
        <div className="pt-2">
          <group.AppField name="description">
            {(field) => (
              <field.AITextAreaField
                label="Rule Description"
                fieldName="description"
                entityType="Rule"
              />
            )}
          </group.AppField>
        </div>
        <div>
          <group.AppField name="effect">
            {(field) => (
              <field.AITextField
                label="Rule Effect"
                fieldName="effect"
                entityType="Rule"
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
                  <div
                    key={index}
                    style={{
                      border: '1px solid #ccc',
                      padding: '10px',
                      marginBottom: '10px',
                    }}
                  >
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
      </div>
    );
  },
});
