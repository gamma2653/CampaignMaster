import { withForm } from '../../shared/components/ctx'
import { campaignPlanOpts } from '../formOpts'
import { ObjectIDGroup } from '../../shared/components/ObjectIDGroup'
import { PREFIXES } from '../../../schemas'

export const PointForm = withForm({
    ...campaignPlanOpts,
    props: {
        arc_index: 0,
        segment_index: 0,
    },
    render: ({ form, arc_index, segment_index }) => {
        return (
            <div>
                <form.AppField name={`storypoints[${arc_index}].segments[${segment_index}].end`}>
                    {(field) => (
                        <div>
                            <h3>End Point Form</h3>
                            <div>
                                <ObjectIDGroup
                                    form={form}
                                    fields={`storypoints[${arc_index}].segments[${segment_index}].end.obj_id`}
                                />
                            </div>
                            <div>
                                <form.AppField
                                    name={`storypoints[${arc_index}].segments[${segment_index}].start.name`}
                                >
                                    {(nameField) => nameField.TextField({ label: 'Point Name' })}
                                </form.AppField>
                                <form.AppField
                                    name={`storypoints[${arc_index}].segments[${segment_index}].start.description`}
                                >
                                    {(descField) =>
                                        descField.TextField({ label: 'Point Description' })
                                    }
                                </form.AppField>
                            </div>
                        </div>
                    )}
                </form.AppField>
            </div>
        )
    }
})
