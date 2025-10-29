import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/planning/campaign/$camp_id/location/')({
  component: RouteComponent,
})

function RouteComponent() {
  return <div>Hello "/planning/campaign/$camp_id/location/"!</div>
}
