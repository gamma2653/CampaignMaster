import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/planning/campaign/')({
  component: RouteComponent,
})

function RouteComponent() {
  return <div>Hello "/planning/campaign/"!</div>
}
