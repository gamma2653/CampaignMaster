import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute(
  '/planning/campaign/$camp_id/arc/$arc_id/segment/$seg_id/point/$point_id/',
)({
  component: RouteComponent,
})

function RouteComponent() {
  return (
    <div>
      Hello
      "/planning/campaign/$camp_id/arc/$arc_id/segment/$seg_id/point/$point_id/"!
    </div>
  )
}
