import { createFileRoute, Link } from '@tanstack/react-router'
import { usePoint } from '../../../../../query'
import { PREFIXES } from '../../../../../schemas'

export const Route = createFileRoute('/campaign/plan/$camp_id/point/')({
  component: PointListComponent,
})

function PointListComponent() {
  const { camp_id } = Route.useParams()
  const { data: points, isLoading, error } = usePoint()

  const handleDelete = async (numeric: number) => {
    if (!confirm('Are you sure you want to delete this point?')) return

    try {
      const response = await fetch(`/api/campaign/p/${numeric}`, {
        method: 'DELETE',
      })
      if (response.ok) {
        // Refresh the page or invalidate query
        window.location.reload()
      } else {
        alert('Failed to delete point')
      }
    } catch (err) {
      alert('Error deleting point')
    }
  }

  if (isLoading) return <div className="p-4">Loading points...</div>
  if (error) return <div className="p-4 text-red-500">Error loading points</div>

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Story Points</h1>
        <Link
          to="/campaign/plan/$camp_id/point/new"
          params={{ camp_id }}
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          Create New Point
        </Link>
      </div>

      {!points || points.length === 0 ? (
        <p className="text-gray-500">No points yet. Create your first one!</p>
      ) : (
        <div className="grid gap-4">
          {points.map((point) => (
            <div
              key={`${point.obj_id.prefix}-${point.obj_id.numeric}`}
              className="border rounded-lg p-4 hover:shadow-lg transition-shadow"
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <Link
                    to="/campaign/plan/$camp_id/point/$point_id"
                    params={{
                      camp_id,
                      point_id: point.obj_id.numeric.toString(),
                    }}
                    className="text-xl font-semibold hover:text-blue-500"
                  >
                    {point.name || 'Unnamed Point'}
                  </Link>
                  <p className="text-sm text-gray-500 mt-1">
                    ID: {point.obj_id.prefix}-{point.obj_id.numeric}
                  </p>
                  {point.objective && (
                    <p className="text-sm text-gray-600 mt-1">
                      Objective: {point.objective.prefix}-{point.objective.numeric}
                    </p>
                  )}
                  <p className="mt-2 text-gray-700">{point.description}</p>
                </div>
                <button
                  onClick={() => handleDelete(point.obj_id.numeric)}
                  className="ml-4 bg-red-500 hover:bg-red-700 text-white font-bold py-1 px-3 rounded"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
