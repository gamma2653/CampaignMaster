import { withFieldGroup } from "../ctx";
import { Location, PREFIXES } from "../../../../schemas";

export const defaultValues = {
    obj_id: {
        prefix: PREFIXES.LOCATION,
        numeric: 0,
    },
    name: '',
    description: '',
    coords: [ 0, 0 ],
} as Location

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
                        {(field) => <field.TextField label="Location Name" />}
                    </group.AppField>
                </div>
                <div>
                    <group.AppField name="description">
                        {(field) => <field.TextAreaField label="Location Description" />}
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
        )
    }
})