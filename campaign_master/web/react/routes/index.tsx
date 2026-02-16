import { createFileRoute, Link, useNavigate } from '@tanstack/react-router';
import {
  BookOpenIcon,
  UserGroupIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline';
import { useCreateCampaignPlan } from '../query';
import { useRouter } from '@tanstack/react-router';
import book_closed from '../../../assets/images/icons/book2.png';

const features = [
  {
    icon: BookOpenIcon,
    title: 'Campaign Planning',
    description:
      'Organize your campaigns with arcs, segments, and story points',
    to: '/campaign/plans',
  },
  {
    icon: UserGroupIcon,
    title: 'Characters & Locations',
    description: 'Build rich NPCs, track inventory, and map your world',
    to: '/campaign/plans',
  },
  {
    icon: SparklesIcon,
    title: 'AI-Powered',
    description: 'Get AI-assisted completions to speed up your worldbuilding',
    to: '/campaign/plans',
  },
] as const;

const HomeComponent = () => {
  const navigate = useNavigate();
  const router = useRouter();
  const createMutation = useCreateCampaignPlan();

  const handleCreateNew = () => {
    createMutation.mutate(
      {
        title: 'New Campaign',
        version: '0.0.1',
        setting: '',
        summary: '',
        storyline: [],
        storypoints: [],
        characters: [],
        locations: [],
        items: [],
        rules: [],
        objectives: [],
      },
      {
        onSuccess: (newCampaign) => {
          navigate({ to: `/campaign/plan/${newCampaign.obj_id.numeric}` });
        },
        onError: (error) => {
          alert(`Failed to create campaign: ${error.message}`);
          router.invalidate();
        },
      },
    );
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex flex-col items-center justify-center px-4 py-16">
      {/* Hero Section */}
      <div className="text-center mb-8">
        <img
          alt=""
          src={book_closed}
          className="h-56 w-auto mx-auto mb-6 opacity-80 p-0"
        />
        <h1 className="text-5xl font-bold text-white mb-4">Campaign Master</h1>
        <p className="text-lg text-gray-400 mb-4 max-w-md mx-auto">
          Your companion for tabletop RPG campaign planning
        </p>
        <Link
          to="/campaign/plans"
          className="inline-block rounded-lg bg-[#4caf50] px-6 py-3 text-base font-semibold text-white hover:bg-[#43a047] transition-colors"
        >
          Get Started
        </Link>
      </div>

      {/* Feature Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl w-full mb-16">
        {features.map((feature) => (
          <Link
            key={feature.title}
            to={feature.to}
            className="group rounded-lg border border-white/10 bg-gray-800/50 p-6 transition-colors hover:border-white/20 hover:bg-gray-800/70"
          >
            <feature.icon className="h-8 w-8 text-gray-400 mb-4 group-hover:text-white transition-colors" />
            <h2 className="text-lg font-semibold text-white mb-2">
              {feature.title}
            </h2>
            <p className="text-sm text-gray-400">{feature.description}</p>
          </Link>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="flex flex-col sm:flex-row gap-4">
        <Link
          to="/campaign/plans"
          className="rounded-lg border border-white/10 bg-gray-800/50 px-6 py-3 text-sm font-medium text-gray-300 hover:bg-white/5 hover:text-white transition-colors"
        >
          Browse Campaigns
        </Link>
        <button
          onClick={handleCreateNew}
          disabled={createMutation.isPending}
          className="rounded-lg bg-[#4caf50] px-6 py-3 text-sm font-medium text-white hover:bg-[#43a047] disabled:cursor-wait disabled:opacity-60 transition-colors"
        >
          {createMutation.isPending ? 'Creating...' : 'Create New Campaign'}
        </button>
      </div>
    </div>
  );
};

export const Route = createFileRoute('/')({
  component: HomeComponent,
});
