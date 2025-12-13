import { createFileRoute, Link } from '@tanstack/react-router'


const RouteComponent = () => {

  return (
    <div>
      <h1>Campaign Master</h1>
      <Link to="/campaign/plan">Go to Campaign Plan Form</Link>
      <br />
      <Link to="/campaign/execute">Go to Campaign Execute</Link>
    </div>
  )
}

export const Route = createFileRoute('/campaign/')({
  component: RouteComponent,
})