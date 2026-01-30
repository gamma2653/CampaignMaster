import {
  Outlet,
  createRootRoute,
  useNavigate,
  useRouterState,
} from '@tanstack/react-router';
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools';
import Navbar from '../features/shared/components/nav';
import { getAuthToken } from '../auth';
import { useEffect } from 'react';
import '../styles.css';

export const Route = createRootRoute({
  component: RootComponent,
});

function RootComponent() {
  const navigate = useNavigate();
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  const isLoginPage = pathname === '/login';
  const hasToken = !!getAuthToken();

  useEffect(() => {
    if (!hasToken && !isLoginPage) {
      navigate({ to: '/login' });
    }
  }, [hasToken, isLoginPage, navigate]);

  if (!hasToken && !isLoginPage) {
    return null;
  }

  return (
    <>
      <link rel="stylesheet" href="/styles.css" />
      {!isLoginPage && <Navbar />}
      <Outlet />
      <TanStackRouterDevtools position="bottom-right" />
    </>
  );
}
