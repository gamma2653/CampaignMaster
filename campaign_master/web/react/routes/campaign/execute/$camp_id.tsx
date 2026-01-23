import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/campaign/execute/$camp_id')({
  component: RouteComponent,
});

function RouteComponent() {
  return <div>Hello "/execute/$camp_id"!</div>;
}
