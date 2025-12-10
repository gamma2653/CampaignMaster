import { withForm } from '../../shared/components/ctx'
import { campaignPlanOpts } from '../formOpts'
import { SegmentForm } from './SegmentForm'


export const ArcForm = withForm({
    ...campaignPlanOpts,
    props: {
        arc_index: 0,
    },
    render: ({ form, arc_index }) => {
        return (
            <div>
                <form.AppField name={`storypoints[${arc_index}]`}>
                    {(field) => (
                        <div>
                            <h1>Arc Form</h1>
                            <div>
                                <form.AppField
                                    name={`storypoints[${arc_index}].name`}
                                >
                                    {(nameField) => (
                                        <div>
                                            <label>
                                                Arc Name:
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
                                    name={`storypoints[${arc_index}].description`}
                                >
                                    {(descField) => (
                                        <div>
                                            <label>
                                                Arc Description:
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
                                <form.AppField
                                    name={`storypoints[${arc_index}].segments`}
                                    mode="array"
                                    // segments are an array of SegmentForms
                                >
                                    {(segmentsField) => (
                                        <div>
                                            <h2>Segments</h2>
                                            {segmentsField.state.value?.map(
                                                (_segment, segment_index) => (
                                                    <SegmentForm
                                                        key={segment_index}
                                                        arc_index={arc_index}
                                                        segment_index={segment_index}
                                                        form={form}
                                                    />
                                                )
                                            )}
                                        </div>
                                    )}
                                </form.AppField>
                            </div>
                        </div>
                    )}
                </form.AppField>
            </div>
        )
    }
})