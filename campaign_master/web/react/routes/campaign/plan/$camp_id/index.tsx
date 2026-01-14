import { createFileRoute } from '@tanstack/react-router'
import { createFieldMap, formOptions } from '@tanstack/react-form'
import { useCampaignPlanByID, useUpdateCampaignPlan } from '../../../../query'
import { PREFIXES } from '../../../../schemas'
import type { CampaignPlan } from '../../../../schemas'
import { useAppForm } from '../../../../features/shared/components/ctx'
import { CampaignPlanGroup } from '../../../../features/shared/components/fieldgroups/CampaignPlanGroup'

// Default values to ensure all arrays are initialized
const defaultCampaignValues: CampaignPlan = {
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
}

export const Route = createFileRoute('/campaign/plan/$camp_id/')({
    component: CampaignPlanEditForm,
})

function CampaignPlanEditForm() {
    const { camp_id } = Route.useParams()
    const numericId = parseInt(camp_id, 10)

    const { data: campaign, isLoading, error } = useCampaignPlanByID({
        prefix: PREFIXES.CAMPAIGN_PLAN,
        numeric: numericId,
    })

    if (isLoading) {
        return (
            <div className="flex items-center justify-center py-12">
                <div className="text-gray-400">Loading campaign...</div>
            </div>
        )
    }

    if (error) {
        return (
            <div className="flex items-center justify-center py-12">
                <div className="text-red-400">Error loading campaign: {error.message}</div>
            </div>
        )
    }

    if (!campaign) {
        return (
            <div className="flex items-center justify-center py-12">
                <div className="text-gray-400">Campaign not found</div>
            </div>
        )
    }

    // Merge API data with defaults to ensure all arrays are initialized
    const mergedCampaign: CampaignPlan = {
        ...defaultCampaignValues,
        ...campaign,
        storyline: campaign.storyline ?? [],
        storypoints: campaign.storypoints ?? [],
        characters: campaign.characters ?? [],
        locations: campaign.locations ?? [],
        items: campaign.items ?? [],
        rules: campaign.rules ?? [],
        objectives: campaign.objectives ?? [],
    }

    return <CampaignEditFormInner campaign={mergedCampaign} />
}

function CampaignEditFormInner({ campaign }: { campaign: CampaignPlan }) {
    const updateMutation = useUpdateCampaignPlan()

    const campaignPlanOpts = formOptions({
        defaultValues: campaign,
        onSubmit: async ({ value }) => {
            updateMutation.mutate(value, {
                onSuccess: () => {
                    alert('Campaign saved successfully!')
                },
                onError: (err) => {
                    alert(`Failed to save campaign: ${err.message}`)
                },
            })
        },
    })

    const form = useAppForm(campaignPlanOpts)

    return (
        <div>
            <form
                onSubmit={(e) => {
                    e.preventDefault()
                    e.stopPropagation()
                    form.handleSubmit()
                }}
            >
                <CampaignPlanGroup
                    form={form}
                    fields={createFieldMap(defaultCampaignValues)}
                />
                <form.AppForm>
                    <div className="flex flex-col p-2 pb-8">
                        <form.SubscribeButton
                            label={updateMutation.isPending ? 'Saving...' : 'Save Campaign'}
                            className="self-center submit-button"
                        />
                    </div>
                </form.AppForm>
            </form>
        </div>
    )
}
