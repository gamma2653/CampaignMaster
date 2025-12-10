import { useAppForm } from '../../shared/components/ctx'
import { PREFIXES } from '../../../schemas'
import { campaignPlanOpts } from '../formOpts'
import { ArcForm } from './ArcForm'


export function CampaignPlanForm() {
    const form = useAppForm(campaignPlanOpts)
    return (
        <div>
            <form.AppField name="obj_id">
                {(field) => (
                    <div>
                        <h2>Campaign Plan ID</h2>
                    </div>
                )}
            </form.AppField>
            <form.AppField name="title">
                {(field) => <field.TextField label="Campaign Plan Title" />}
            </form.AppField>
            <form.AppField name="version">
                {(field) => <field.TextField label="Campaign Plan Version" />}
            </form.AppField>
            <form.AppField
                name="storypoints"
                mode="array"
            >
                {(storypointsField) => (
                    <div>
                        {storypointsField.state.value?.map((_, arc_index) => (
                            <ArcForm
                                key={arc_index}
                                arc_index={arc_index}
                                form={form}
                            />
                        ))}
                    </div>
                )}
            </form.AppField>
        </div>
    )
}