import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/campaign/plan/$camp_id/location/')({
  component: RouteComponent,
});

function RouteComponent() {
  return <div>Hello "/campaign/plan/$camp_id/location/"!</div>;
}
