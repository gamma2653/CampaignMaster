import { createFileRoute } from '@tanstack/react-router'
// import { TanStackDevtools } from '@tanstack/react-devtools'
// import { FormDevtoolsPlugin } from '@tanstack/react-form-devtools'
import { useForm } from '@tanstack/react-form'
import type { CampaignPlan } from '../../schemas'
import { CampaignPlanForm } from '../../components/Forms'


// Deliberations:
// I was stuck considering how I should structure this top-level form component
// because a Campaign Plan contains arrays of other complex objects (characters, locations, items, etc)
// Each of those objects could be complex enough to warrant their own sub-forms/components
// However, for this initial implementation, I'll keep it simple and just create a single form component
// that captures the basic fields of a Campaign Plan. Later, I can refactor to break out sub-forms as needed.

const RouteComponent = () => {
  return (
    <div>
      <h1>Campaign Master</h1>
      <CampaignPlanForm />
    </div>
  )
}

export const Route = createFileRoute('/campaign/')({
  component: RouteComponent,
})