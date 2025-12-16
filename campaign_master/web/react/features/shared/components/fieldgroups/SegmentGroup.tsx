import { withFieldGroup } from "../ctx";
import type { Point, Segment } from "../../../../schemas";
import { PREFIXES } from "../../../../schemas";
import { PointGroup } from "./PointGroup";

export const defaultValues = {
    obj_id: { prefix: PREFIXES.SEGMENT, numeric: 0 },
    name: '',
    description: '',
    start: { prefix: PREFIXES.POINT, numeric: 0 },
    end: { prefix: PREFIXES.POINT, numeric: 1 },
} as Segment


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
}

export const SegmentGroup = withFieldGroup({
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
                        {(field) => <field.TextField label="Segment Name" />}
                    </group.AppField>
                </div>
                <div>
                    <group.AppField name="description">
                        {(field) => <field.TextAreaField label="Segment Description" />}
                    </group.AppField>
                </div>
                <div>
                    <group.AppField name="start">
                        {(field) => <field.PointSelectField label="Start Point" points={points} />}
                    </group.AppField>
                </div>
                <div>
                    <group.AppField name="end">
                        {(field) => <field.PointSelectField label="End Point" points={points} />}
                    </group.AppField>
                </div>
            </div>
        )
    }
})