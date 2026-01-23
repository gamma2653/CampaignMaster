import { withFieldGroup } from '../ctx';
import { AnyID, PREFIXES, PREFIXES_T } from '../../../../schemas';

const defaultValues = {
  prefix: PREFIXES.MISC as PREFIXES_T,
  numeric: 0,
} as AnyID;

// type Props = {
//     classNames?: {
//         all?: string;
//         prefix?: string;
//         numeric?: string;
//     }
// }

export const ObjectIDGroup = withFieldGroup({
  defaultValues,
  // props: {} as Props,
  // render: ({ group, classNames }) => {
  render: ({ group }) => {
    return (
      <div className="flex flex-col gap-2">
        <group.AppField name="prefix">
          {(field) => (
            <label>
              Prefix:
              <select value={field.state.value} disabled={true}>
                {Object.values(PREFIXES).map((pref) => (
                  <option key={pref} value={pref}>
                    {pref}
                  </option>
                ))}
              </select>
            </label>
          )}
        </group.AppField>
        <group.AppField name="numeric">
          {(field) => (
            <label>
              Numeric ID:
              <input
                type="number"
                value={field.state.value}
                onChange={(e) => field.handleChange(Number(e.target.value))}
              />
            </label>
          )}
        </group.AppField>
      </div>
    );
  },
});
