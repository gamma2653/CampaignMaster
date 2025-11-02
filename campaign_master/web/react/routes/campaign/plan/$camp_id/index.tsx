import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/campaign/plan/$camp_id/')({
  component: RouteComponent,
  loader: async ({ params }) => {
    // await new Promise((resolve) => setTimeout(resolve, 1000))
    return { campaignId: params.camp_id }
  },
  pendingComponent: () => <div>Loading campaign...</div>,
})

function RouteComponent() {
  const { campaignId } = Route.useLoaderData()
  return <div>Hello "/campaign/plan/{campaignId}"!</div>
}
