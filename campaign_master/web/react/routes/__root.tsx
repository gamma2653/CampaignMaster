import { Link, Outlet, createRootRoute } from '@tanstack/react-router'
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools'
import '../styles.css'

export const Route = createRootRoute({
  component: RootComponent,
})

function RootComponent() {
  return (
    <>
      <link rel="stylesheet" href="/styles.css" />
      <nav>
        <ul>
          <li>
            <Link to="/campaign/plan">Plan</Link>
          </li>
          <li>
            <Link to="/campaign/execute">Execute</Link>
          </li>
        </ul>
      </nav>
      <Outlet />
      <TanStackRouterDevtools position="bottom-right" />
    </>
  )
}