import { createFileRoute } from '@tanstack/react-router'
import { CampaignPlanForm } from '../../../features/planning/components/forms'

export const Route = createFileRoute('/campaign/plan/')({
  component: CampaignPlanForm,
})

