import { formOptions, createFieldMap } from '@tanstack/react-form'
import { useAppForm, withForm } from './ctx'
import { defaultCampaignPlanValues } from './fields'


// export const campaignPlanOpts = formOptions(campaignPlanOpts)

export const CampaignPlanForm = () => {
    const form = useAppForm({
        defaultValues: {campaign_plan: defaultCampaignPlanValues},
        onSubmit: ({ value }) => console.log(`Submitting: '${value}'`)
    })
    console.log('CampaignForm defaultValues:', defaultCampaignPlanValues)

    return (
        <form.AppField
            name="campaign_plan"
            children={(field) => <field.CampaignPlanField label="Campaign Plan" />}
        >

        </form.AppField>
    )
}
