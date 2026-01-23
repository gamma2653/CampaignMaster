import { createFileRoute } from '@tanstack/react-router';
import { CampaignPlansList } from '../../../features/planning/components/CampaignPlansList';

export const Route = createFileRoute('/campaign/plans/')({
  component: CampaignPlansList,
});
