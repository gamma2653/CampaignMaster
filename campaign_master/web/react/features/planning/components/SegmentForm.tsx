import { withForm } from '../../shared/components/ctx'
import { campaignPlanOpts } from '../formOpts'
import { PointForm } from './PointForm'

export const SegmentForm = withForm({
    ...campaignPlanOpts,
    props: {
        arc_index: 0,
        segment_index: 0,
    },
    render: ({ form, arc_index, segment_index }) => {
        return (
            <div>
                <form.AppField name={`storypoints[${arc_index}].segments[${segment_index}]`}>
                    {(field) => (
                        <div>
                            <h2>Segment Form</h2>
                            <div>
                                <form.AppField
                                    name={`storypoints[${arc_index}].segments[${segment_index}].name`}
                                >
                                    {(nameField) => (
                                        <div>
                                            <label>
                                                Segment Name:
                                                <input
                                                    type="text"
                                                    value={nameField.state.value || ''}
                                                    onChange={(e) =>
                                                        nameField.handleChange(e.target.value)
                                                    }
                                                />
                                            </label>
                                        </div>
                                    )}
                                </form.AppField>
                                <form.AppField
                                    name={`storypoints[${arc_index}].segments[${segment_index}].description`}
                                >
                                    {(descField) => (
                                        <div>
                                            <label>
                                                Segment Description:
                                                <input
                                                    type="text"
                                                    value={descField.state.value || ''}
                                                    onChange={(e) =>
                                                        descField.handleChange(e.target.value)
                                                    }
                                                />
                                            </label>
                                        </div>
                                    )}
                                </form.AppField>
                                <PointForm
                                    arc_index={arc_index}
                                    segment_index={segment_index}
                                    form={form}
                                />
                            </div>
                        </div>
                    )}
                </form.AppField>
            </div>
        )
    }
})
