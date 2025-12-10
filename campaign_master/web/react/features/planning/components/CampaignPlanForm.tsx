import { useAppForm } from '../../shared/components/ctx'
import { createFieldMap } from '@tanstack/react-form'
import { campaignPlanOpts } from '../formOpts'
import { CampaignPlanGroup } from '../../shared/components/fieldgroups/CampaignPlanGroup'


export function CampaignPlanForm() {
    const form = useAppForm(campaignPlanOpts)
    return (
        <div>
            <h1>Campaign Plan Form</h1>
            <CampaignPlanGroup
                form={form}
                fields={createFieldMap(campaignPlanOpts.defaultValues)}
            />
        </div>
    )
}