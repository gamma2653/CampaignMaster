import { withFieldGroup } from "../ctx";
import { Arc, Point, PREFIXES } from "../../../../schemas";
import { SegmentGroup, defaultValues as segDefaultValues } from "./SegmentGroup";

export const defaultValues = {
    obj_id: { prefix: PREFIXES.ARC, numeric: 0 },
    name: '',
    description: '',
    segments: [],
} as Arc


export const ArcGroup = withFieldGroup({
    defaultValues,
    props: {
        points: [] as Array<Point>,
    },
    render: ({ group, points }) => {
        return (
            <div>
                <group.AppField name="obj_id">
                    {(field) => <field.IDDisplayField />}
                </group.AppField>
                <group.AppField name="name">
                    {(field) => <field.TextField label="Segment Name" />}
                </group.AppField>
                <group.AppField name="description">
                    {(field) => <field.TextField label="Segment Description" />}
                </group.AppField>
                <group.AppField name="segments" mode="array">
                    {(field) => (
                        <div>
                            <h3>Segments</h3>
                            {group.state.values.segments.map((_, index) => (
                                <div key={index} style={{ border: '1px solid #ccc', padding: '10px', marginBottom: '10px' }}>
                                    <h4>Segment {index + 1}</h4>
                                    <SegmentGroup
                                        form={group}
                                        fields={`segments[${index}]`}
                                        points={points}
                                    />
                                </div>
                            ))}
                            <button
                                type="button"
                                onClick={() => {
                                    field.pushValue(segDefaultValues)
                                }}
                            >
                                Add Segment
                            </button>
                        </div>
                    )}
                </group.AppField>
            </div>
        )
    }
})