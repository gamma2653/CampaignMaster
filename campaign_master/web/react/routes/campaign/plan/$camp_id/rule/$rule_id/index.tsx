import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute(
  '/campaign/plan/$camp_id/rule/$rule_id/',
)({
  component: RouteComponent,
})

function RouteComponent() {
  return <div>Hello "/campaign/plan/$camp_id/rule/$rule_id/"!</div>
}
