import { createFileRoute } from '@tanstack/react-router';

const RouteComponent = () => {
  return <div>Hello "/execute/"!</div>;
};

export const Route = createFileRoute('/campaign/execute/')({
  component: RouteComponent,
});
