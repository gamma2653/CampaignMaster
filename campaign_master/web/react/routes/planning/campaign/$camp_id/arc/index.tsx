import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/planning/campaign/$camp_id/arc/')({
  component: RouteComponent,
})

function RouteComponent() {
  return <div>Hello "/planning/campaign/$camp_id/arc/"!</div>
}
