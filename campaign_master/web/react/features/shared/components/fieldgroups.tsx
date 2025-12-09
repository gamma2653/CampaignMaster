import { withFieldGroup } from './new_ctx'
import { defaultPointValues, defaultSegmentValues, defaultArcValues, defaultCampaignPlanValues } from './new_fields'
import { PREFIXES, PREFIX_TO_NAME } from '../../../schemas'

export const PointFieldGroup = withFieldGroup({
    defaultValues: defaultPointValues,
    props: {
        label: 'Point'
    },
    render: function Render({ group, label }) {
        return (
            <div>
                <h2>{label}</h2>
                    <group.AppField
                        name='obj_id'
                        children={(field) => <field.IDField label="Point ID" prefix={PREFIXES.POINT} />}
                    />
                    <group.AppField
                        name='name'
                        children={(field) => <field.TextField label="Point Name" />}
                    />
                    <group.AppField
                        name='description'
                        children={(field) => <field.TextField label="Point Description" />}
                    />
                    <group.AppField
                        name='objective'
                        children={(field) => <field.IDField label="Objective" prefix={PREFIXES.OBJECTIVE} />}
                    />
            </div>
        )
    }
})

export const SegmentFieldGroup = withFieldGroup({
    defaultValues: defaultSegmentValues,
    props: {
        label: 'Segment'
    },
    render: function Render({ group, label }) {
        return (
            <div>
                <h2>{label}</h2>
                <group.AppField
                    name='obj_id'
                    children={(field) => <field.IDField label="Segment ID" prefix={PREFIXES.SEGMENT} />}
                />
                <group.AppField
                    name='name'
                    children={(field) => <field.TextField label="Segment Name" />}
                />
                <group.AppField
                    name='description'
                    children={(field) => <field.TextField label="Segment Description" />}
                />
                <group.AppField
                    name='start'
                    children={(field) => (
                        <PointFieldGroup
                            label="Start Point"
                            form={field.form}
                            fields="start"
                        />
                    )}
                />
                <group.AppField
                    name='end'
                    children={(field) => (
                        <PointFieldGroup
                            label="End Point"
                            form={field.form}
                        />
                    )}
                />
            </div>
        )
    }
})


export const ArcFieldGroup = withFieldGroup({
    defaultValues: defaultArcValues,
    props: {
        label: 'Arc'
    },
    render: function Render({ group, label }) {
        return (
            <div>
                <h2>{label}</h2>
                <group.AppField
                    name="obj_id"
                    children={
                        (field) => <field.IDField prefix={PREFIXES.ARC} />
                    }
                />
                <group.AppField
                    name="name"
                    children={
                        (field) => <field.TextField label="Arc Name" />
                    }
                />
                <group.AppField
                    name="description"
                    children={
                        (field) => <field.TextField label="Arc Description" />
                    }
                />
                <group.AppField
                    name="segments"
                    mode="array"
                    children={(segmentField) => (
                        // segmentField ~= Segment[]
                        <div>
                            {segmentField.state.value.map((_, i) => (
                                <div>
                                    <SegmentFieldGroup
                                        label={`Segment ${i + 1}`}
                                        form={segmentField.form}
                                    />
                                </div>
                            ))}
                        </div>
                    )}
                />
            </div>
        )
    }
})

export const CampaignPlanFieldGroup = withFieldGroup({
    defaultValues: defaultCampaignPlanValues,
    props: {
        label: 'Campaign Plan'
    },
    render: ({ group, label }) => {
        return (
            <div>
                <h2>{label}</h2>
                <group.AppField
                    name="obj_id"
                    children={
                        (field) => <field.IDField prefix={PREFIXES.CAMPAIGN_PLAN} />
                    }
                />
                <group.AppField
                    name="title"
                    children={
                        (field) => <field.TextField label="Title" />
                    }
                />
                <group.AppField
                    name="version"
                    children={
                        (field) => <field.TextField label="Version" />
                    }
                />
                <group.AppField
                    name="setting"
                    children={
                        (field) => <field.TextField label="Setting" />
                    }
                />
                <group.AppField
                    name="summary"
                    children={
                        (field) => <field.TextField label="Summary" />
                    }
                />
                <group.AppField
                    name="storypoints"
                    mode="array"
                    children={(arcField) => (
                        // arcField ~= Arc[]
                        <div>
                            {arcField.state.value.map((_, i) => (
                                <div>
                                    <ArcFieldGroup
                                        label={`Story Arc ${i + 1}`}
                                        form={arcField.form}
                                    />
                                </div>
                            ))}
                        </div>
                    )}
                />
            </div>
        )
    }
})
