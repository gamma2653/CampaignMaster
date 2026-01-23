import { useCampaignPlan, useDeleteCampaignPlan } from '../../../query';
import type { CampaignID } from '../../../schemas';
import { CampaignCard } from './CampaignCard';

export function CampaignPlansList() {
  const { data: campaigns, isLoading, error } = useCampaignPlan();
  const deleteMutation = useDeleteCampaignPlan();

  const handleDelete = (id: CampaignID) => {
    deleteMutation.mutate(id);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-gray-400">Loading campaigns...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-red-400">
          Error loading campaigns: {error.message}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white">My Campaign Plans</h1>

      {!campaigns || campaigns.length === 0 ? (
        <div className="text-center py-12 bg-gray-800/30 rounded-lg border border-white/10">
          <p className="text-gray-400">
            You don't have any campaigns yet. Click "New Campaign" in the navbar
            to create one.
          </p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {campaigns.map((campaign) => (
            <CampaignCard
              key={campaign.obj_id.numeric}
              campaign={campaign}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}

      {deleteMutation.isPending && (
        <div className="fixed bottom-4 right-4 bg-gray-800 text-white px-4 py-2 rounded-lg shadow-lg">
          Deleting campaign...
        </div>
      )}
    </div>
  );
}
