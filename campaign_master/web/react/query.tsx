import { useQuery } from '@tanstack/react-query'
import type {
    CampaignPlan, CampaignID, Rule, RuleID, Objective, ObjectiveID, Point, PointID, Segment, SegmentID, Arc, ArcID, Item, ItemID, Character, CharacterID, Location, LocationID, Object, AnyID,
} from './schemas'
import { PREFIXES, getUrlSegment } from './schemas'

const BASE_API_URL = '/api/campaign/'

const generateShallowQueries = <IDType extends AnyID, RetType extends Object>(prefixes: string[]) => {
    const useData = () => {
        return useQuery({
            queryKey: [prefixes],
            queryFn: async (): Promise<Array<RetType>> => {
                const response = await fetch(`${BASE_API_URL}${prefixes.map(p => p.toLowerCase()).join('/')}`)
                return await response.json()
            },
        })
    }
    const useDataByID = (id: IDType) => {
        return useQuery({
            queryKey: [prefixes, id],
            queryFn: async (): Promise<RetType> => {
                const response = await fetch(`${BASE_API_URL}${getUrlSegment(id)}`)
                return await response.json()
            },
        })
    }
    return [useData, useDataByID]
}

// Endpoints follow the form: /api/campaign/{foo_prefix}/{foo_numeric}/{bar_prefix}/{bar_numeric}/...

// Some queries may need to be nested, e.g., get a specific point for a given campaign plan.

const generateNestedQuery = <IDType extends AnyID, RetType extends Object, ParentIDType extends AnyID = IDType>(baseEndpoint: string) => {
    return (parentIDs: ParentIDType[], id: IDType) => {
        const prefixes = [...parentIDs.map(parentID => parentID.prefix), id.prefix]
        return useQuery({
            queryKey: [baseEndpoint, ...parentIDs, id],
            queryFn: async (): Promise<RetType> => {
                const response = await fetch(`${BASE_API_URL}${[...parentIDs, id].map(id => getUrlSegment(id)).join('/')}`)
                return await response.json()
            },
        })
    }
}

// I <3 functional programming

const [useRule, useRuleByID] = generateShallowQueries<RuleID, Rule>([PREFIXES.RULE])
const [useObjective, useObjectiveByID] = generateShallowQueries<ObjectiveID, Objective>([PREFIXES.OBJECTIVE])
const [usePoint, usePointByID] = generateShallowQueries<PointID, Point>([PREFIXES.POINT])
const [useSegment, useSegmentByID] = generateShallowQueries<SegmentID, Segment>([PREFIXES.SEGMENT])
const [useArc, useArcByID] = generateShallowQueries<ArcID, Arc>([PREFIXES.ARC])
const [useItem, useItemByID] = generateShallowQueries<ItemID, Item>([PREFIXES.ITEM])
const [useCharacter, useCharacterByID] = generateShallowQueries<CharacterID, Character>([PREFIXES.CHARACTER])
const [useLocation, useLocationByID] = generateShallowQueries<LocationID, Location>([PREFIXES.LOCATION])
const [useCampaignPlan, useCampaignPlanByID] = generateShallowQueries<CampaignID, CampaignPlan>([PREFIXES.CAMPAIGN])
const usePointByCampaignAndID = generateNestedQuery<CampaignID, Point, PointID>('campaign_points')  // endpoint: /api/campaign/campaign_points/campplan/{campaign_numeric}/p/{point_numeric}
// TODO: Find better endpoint names for nested queries

// Example of unrolled version for clarity:
// const useRules = () => {
//     return useQuery({
//         queryKey: ['r'],
//         queryFn: async (): Promise<Array<Rule>> => {
//             const response = await fetch('/api/campaign/r')
//             return await response.json()
//         },
//     })
// }
//
// const useRuleByID = (id: RuleID) => {
//     return useQuery({
//         queryKey: ['r', id],
//         queryFn: async (): Promise<Rule> => {
//             const response = await fetch(`/api/campaign/r/${id}`)
//             return await response.json()
//         },
//     })
// }

export { useRule, useRuleByID, useObjective, useObjectiveByID, usePoint, usePointByID, useSegment, useSegmentByID, useArc, useArcByID, useItem, useItemByID, useCharacter, useCharacterByID, useLocation, useLocationByID, useCampaignPlan, useCampaignPlanByID }