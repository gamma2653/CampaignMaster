import { withFieldGroup } from "../ctx";
import { Location, PREFIXES } from "../../../../schemas";
import { ObjectIDGroup } from "./ObjectIDGroup";

export const defaultValues = {
    obj_id: {
        prefix: PREFIXES.LOCATION,
        numeric: 0,
    },
    name: '',
    description: '',
    coords: [ 0, 0 ],
} as Location


export const LocationGroup = withFieldGroup({
    defaultValues,
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
            <div>
                <ObjectIDGroup
                    form={group}
                    fields="obj_id"
                />
                <group.AppField name="name">
                    {(field) => <field.TextField label="Location Name" />}
                </group.AppField>
                <group.AppField name="description">
                    {(field) => <field.TextField label="Location Description" />}
                </group.AppField>
                <group.AppField name="coords">
                    {(field) => (
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
        )
    }
})