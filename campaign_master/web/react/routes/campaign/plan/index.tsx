import { createFileRoute } from '@tanstack/react-router'
import { CampaignPlanForm } from '../../../components/Forms'

export const Route = createFileRoute('/campaign/plan/')({
  component: CampaignPlanForm,
})

