import { createFieldMap, formOptions } from '@tanstack/react-form'
import type { CampaignPlan } from '../../../schemas'
import { PREFIXES } from '../../../schemas'
import { useAppForm } from '../../shared/components/ctx'
import { CampaignPlanGroup } from '../../shared/components/fieldgroups/CampaignPlanGroup'

export const campaignPlanOpts = formOptions({
    defaultValues: {
        obj_id: { prefix: PREFIXES.CAMPAIGN_PLAN, numeric: 0 },
        title: '',
        version: '',
        setting: '',
        summary: '',
        storyline: [],
        storypoints: [],
        characters: [],
        locations: [],
        items: [],
        rules: [],
        objectives: [],
    } as CampaignPlan,
})

export function CampaignPlanForm() {
    const form = useAppForm(campaignPlanOpts)
    return (
        <div>
            <form
                onSubmit={(e) => {
                    e.preventDefault()
                    e.stopPropagation()
                    form.handleSubmit()
                }}>
                <h1>Campaign Plan Form</h1>
                <CampaignPlanGroup
                    form={form}
                    fields={createFieldMap(campaignPlanOpts.defaultValues)}
                />
                <form.AppForm>
                    <form.SubscribeButton label="Submit Campaign Plan" />
                </form.AppForm>
            </form>
        </div>
    )
}