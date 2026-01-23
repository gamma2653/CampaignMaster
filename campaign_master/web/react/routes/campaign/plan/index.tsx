import { createFileRoute, redirect } from '@tanstack/react-router';

export const Route = createFileRoute('/campaign/plan/')({
  beforeLoad: () => {
    throw redirect({ to: '/campaign/plans' });
  },
  component: () => null,
});
