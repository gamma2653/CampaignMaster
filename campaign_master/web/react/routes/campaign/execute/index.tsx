import { createFileRoute, useNavigate } from '@tanstack/react-router';
import {
  useCampaignExecution,
  useCreateCampaignExecution,
  useDeleteCampaignExecution,
} from '../../../query';
import { PREFIXES, PREFIX_TO_NAME } from '../../../schemas';
import type { CampaignExecution, AnyID } from '../../../schemas';

const RouteComponent = () => {
  const { data: executions, isLoading, error } = useCampaignExecution();
  const createMutation = useCreateCampaignExecution();
  const deleteMutation = useDeleteCampaignExecution();
  const navigate = useNavigate();

  const handleCreate = () => {
    createMutation.mutate(
      {
        campaign_plan_id: { prefix: PREFIXES.CAMPAIGN_PLAN, numeric: 0 },
        title: 'New Session',
        session_date: new Date().toISOString().split('T')[0],
        raw_session_notes: '',
        refined_session_notes: '',
        refinement_mode: 'narrative',
        entries: [],
      },
      {
        onSuccess: (created: CampaignExecution) => {
          navigate({
            to: '/campaign/execute/$camp_id',
            params: { camp_id: String(created.obj_id.numeric) },
          });
        },
      },
    );
  };

  const handleDelete = (id: AnyID, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm('Delete this execution?')) {
      deleteMutation.mutate(id);
    }
  };

  if (isLoading) return <div className="p-8">Loading executions...</div>;
  if (error)
    return <div className="p-8 text-red-400">Error: {error.message}</div>;

  const items = (executions ?? []) as CampaignExecution[];

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Campaign Executions</h1>
        <button
          type="button"
          onClick={handleCreate}
          disabled={createMutation.isPending}
          className="bg-green-700 hover:bg-green-600 text-white px-4 py-2 rounded disabled:opacity-50"
        >
          {createMutation.isPending ? 'Creating...' : 'New Execution'}
        </button>
      </div>

      {items.length === 0 ? (
        <p className="text-gray-400">
          No executions yet. Create one to start tracking a session.
        </p>
      ) : (
        <div className="space-y-3">
          {items.map((ex) => (
            <div
              key={`${ex.obj_id.prefix}-${ex.obj_id.numeric}`}
              onClick={() =>
                navigate({
                  to: '/campaign/execute/$camp_id',
                  params: { camp_id: String(ex.obj_id.numeric) },
                })
              }
              className="border border-gray-600 rounded p-4 hover:bg-gray-800 cursor-pointer flex justify-between items-start"
            >
              <div>
                <h2 className="font-semibold text-lg">
                  {ex.title || 'Untitled Session'}
                </h2>
                <div className="text-sm text-gray-400 mt-1">
                  {ex.session_date && <span>Date: {ex.session_date}</span>}
                  {ex.campaign_plan_id.numeric > 0 && (
                    <span className="ml-4">
                      Plan: {ex.campaign_plan_id.prefix}-
                      {ex.campaign_plan_id.numeric}
                    </span>
                  )}
                  <span className="ml-4">
                    {ex.entries.length} entit
                    {ex.entries.length === 1 ? 'y' : 'ies'}
                  </span>
                </div>
              </div>
              <button
                type="button"
                onClick={(e) => handleDelete(ex.obj_id, e)}
                className="text-red-400 hover:text-red-300 text-sm px-2 py-1"
              >
                Delete
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export const Route = createFileRoute('/campaign/execute/')({
  component: RouteComponent,
});
