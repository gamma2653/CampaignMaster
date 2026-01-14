import { Link } from '@tanstack/react-router'
import type { CampaignPlan, CampaignID } from '../../../schemas'

interface CampaignCardProps {
    campaign: CampaignPlan
    onDelete: (id: CampaignID) => void
}

export function CampaignCard({ campaign, onDelete }: CampaignCardProps) {
    const { obj_id, title, summary, version, characters, locations, items, rules, objectives, storyline, storypoints } = campaign

    const truncatedSummary = summary.length > 120 ? `${summary.slice(0, 120)}...` : summary

    const handleDelete = () => {
        if (window.confirm(`Are you sure you want to delete "${title}"?`)) {
            onDelete(obj_id)
        }
    }

    return (
        <div className="bg-gray-800/50 rounded-lg p-4 border border-white/10 hover:border-white/20 transition-colors">
            <div className="flex justify-between items-start mb-2">
                <h3 className="text-lg font-semibold text-white">{title || 'Untitled Campaign'}</h3>
                <span className="text-xs text-gray-400 bg-gray-700/50 px-2 py-1 rounded">v{version}</span>
            </div>

            <p className="text-sm text-gray-300 mb-4 min-h-[2.5rem]">
                {truncatedSummary || 'No summary provided'}
            </p>

            <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs text-gray-400 mb-4">
                <span>Characters: {characters.length}</span>
                <span>Locations: {locations.length}</span>
                <span>Items: {items.length}</span>
                <span>Rules: {rules.length}</span>
                <span>Objectives: {objectives.length}</span>
                <span>Arcs: {storyline.length}</span>
                <span>Points: {storypoints.length}</span>
            </div>

            <div className="flex gap-2 pt-2 border-t border-white/10">
                <Link
                    to="/campaign/plan/$camp_id"
                    params={{ camp_id: String(obj_id.numeric) }}
                    className="flex-1 text-center px-3 py-1.5 text-sm bg-blue-600/80 hover:bg-blue-600 text-white rounded transition-colors"
                >
                    Edit
                </Link>
                <button
                    onClick={handleDelete}
                    className="flex-1 px-3 py-1.5 text-sm bg-red-600/80 hover:bg-red-600 text-white rounded transition-colors"
                >
                    Delete
                </button>
            </div>
        </div>
    )
}
