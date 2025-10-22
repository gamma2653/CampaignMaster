import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/planning/campaign/$id')({
  component: RouteComponent,
  loader: async ({ params }) => {
    await new Promise((resolve) => setTimeout(resolve, 1000))
    return { campaignId: params.id }
  },
  pendingComponent: () => <div>Loading campaign...</div>,
})

function RouteComponent() {
  const { campaignId } = Route.useLoaderData()
  return <div>Hello "/planning/campaign/{campaignId}"!</div>
}
