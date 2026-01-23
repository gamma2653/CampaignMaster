/**
 * Settings index page - redirects to agents settings.
 */

import { createFileRoute, redirect } from '@tanstack/react-router';

export const Route = createFileRoute('/settings/')({
  beforeLoad: () => {
    throw redirect({ to: '/settings/agents' });
  },
  component: () => null,
});
