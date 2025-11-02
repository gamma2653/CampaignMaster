import { useQuery } from '@tanstack/react-query'
import type {
    CampaignPlan, CampaignID, Rule, RuleID, Objective, ObjectiveID, Point, PointID, Segment, SegmentID, Arc, ArcID, Item, ItemID, Character, CharacterID, Location, LocationID,
} from './schemas'


const generateQueries = <IDType, RetType>(endpoint: string, singular_endpoint?: string) => {
    const useData = () => {
        return useQuery({
            queryKey: [singular_endpoint || endpoint],
            queryFn: async (): Promise<Array<RetType>> => {
                const response = await fetch(`/api/campaign/${endpoint}`)
                return await response.json()
            },
        })
    }
    const useDataByID = (id: IDType) => {
        return useQuery({
            queryKey: [endpoint, id],
            queryFn: async (): Promise<RetType> => {
                const response = await fetch(`/api/campaign/${endpoint}/${id}`)
                return await response.json()
            },
        })
    }
    return [ useData, useDataByID ]
}

// I <3 functional programming

const [useRule, useRuleByID] = generateQueries<RuleID, Rule>('rules', 'rule')
const [useObjective, useObjectiveByID] = generateQueries<ObjectiveID, Objective>('objective', 'objective')
const [usePoint, usePointByID] = generateQueries<PointID, Point>('point', 'point')
const [useSegment, useSegmentByID] = generateQueries<SegmentID, Segment>('segment', 'segment')
const [useArc, useArcByID] = generateQueries<ArcID, Arc>('arc', 'arc')
const [useItem, useItemByID] = generateQueries<ItemID, Item>('item', 'item')
const [useCharacter, useCharacterByID] = generateQueries<CharacterID, Character>('character', 'character')
const [useLocation, useLocationByID] = generateQueries<LocationID, Location>('location', 'location')
const [useCampaignPlan, useCampaignPlanByID] = generateQueries<CampaignID, CampaignPlan>('plan', 'plan')


export { useRuleByID, useRule, useObjective, useObjectiveByID, usePoint, usePointByID, useSegment, useSegmentByID, useArc, useArcByID, useItem, useItemByID, useCharacter, useCharacterByID, useLocation, useLocationByID, useCampaignPlanByID, useCampaignPlan }