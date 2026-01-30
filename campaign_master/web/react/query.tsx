import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import type {
  CampaignPlan,
  CampaignID,
  Rule,
  RuleID,
  Objective,
  ObjectiveID,
  Point,
  PointID,
  Segment,
  SegmentID,
  Arc,
  ArcID,
  Item,
  ItemID,
  Character,
  CharacterID,
  Location,
  LocationID,
  Object,
  AnyID,
  AgentConfig,
  AgentConfigID,
  RuleCreate,
  RuleUpdate,
  ObjectiveCreate,
  ObjectiveUpdate,
  PointCreate,
  PointUpdate,
  SegmentCreate,
  SegmentUpdate,
  ArcCreate,
  ArcUpdate,
  ItemCreate,
  ItemUpdate,
  CharacterCreate,
  CharacterUpdate,
  LocationCreate,
  LocationUpdate,
  CampaignPlanCreate,
  CampaignPlanUpdate,
  AgentConfigCreate,
  AgentConfigUpdate,
} from './schemas';
import { PREFIXES, getUrlSegment } from './schemas';
import { getAuthToken } from './auth';

const BASE_API_URL = '/api/campaign/';

function authHeaders(extra?: Record<string, string>): Record<string, string> {
  const headers: Record<string, string> = { ...extra };
  const token = getAuthToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

const generateShallowQueries = <IDType extends AnyID, RetType extends Object>(
  prefixes: string[],
) => {
  const useData = () => {
    return useQuery({
      queryKey: [prefixes],
      queryFn: async (): Promise<Array<RetType>> => {
        const response = await fetch(
          `${BASE_API_URL}${prefixes.map((p) => p.toLowerCase()).join('/')}`,
          { headers: authHeaders() },
        );
        if (!response.ok) throw new Error(`Fetch failed: ${response.status}`);
        return await response.json();
      },
    });
  };
  const useDataByID = (id: IDType) => {
    return useQuery({
      queryKey: [prefixes, id],
      queryFn: async (): Promise<RetType> => {
        const response = await fetch(`${BASE_API_URL}${getUrlSegment(id)}`, {
          headers: authHeaders(),
        });
        if (!response.ok) throw new Error(`Fetch failed: ${response.status}`);
        return await response.json();
      },
    });
  };
  return [useData, useDataByID];
};

// Endpoints follow the form: /api/campaign/{foo_prefix}/{foo_numeric}/{bar_prefix}/{bar_numeric}/...

// Some queries may need to be nested, e.g., get a specific point for a given campaign plan.

const generateNestedQuery = <
  IDType extends AnyID,
  RetType extends Object,
  ParentIDType extends AnyID = IDType,
>(
  baseEndpoint: string,
) => {
  return (parentIDs: ParentIDType[], id: IDType) => {
    const prefixes = [
      ...parentIDs.map((parentID) => parentID.prefix),
      id.prefix,
    ];
    const numerics = [
      ...parentIDs.map((parentID) => parentID.numeric),
      id.numeric,
    ];
    return useQuery({
      // NOTE: Look into later whether numerics should be first, for cache efficiency
      queryKey: [baseEndpoint, ...prefixes, ...numerics],
      queryFn: async (): Promise<RetType> => {
        const response = await fetch(
          `${BASE_API_URL}/${baseEndpoint}/${[...parentIDs, id].map((id) => getUrlSegment(id)).join('/')}`,
          { headers: authHeaders() },
        );
        if (!response.ok) throw new Error(`Fetch failed: ${response.status}`);
        return await response.json();
      },
    });
  };
};

// I <3 functional programming

const [useRule, useRuleByID] = generateShallowQueries<RuleID, Rule>([
  PREFIXES.RULE,
]);
const [useObjective, useObjectiveByID] = generateShallowQueries<
  ObjectiveID,
  Objective
>([PREFIXES.OBJECTIVE]);
const [usePoint, usePointByID] = generateShallowQueries<PointID, Point>([
  PREFIXES.POINT,
]);
const [useSegment, useSegmentByID] = generateShallowQueries<SegmentID, Segment>(
  [PREFIXES.SEGMENT],
);
const [useArc, useArcByID] = generateShallowQueries<ArcID, Arc>([PREFIXES.ARC]);
const [useItem, useItemByID] = generateShallowQueries<ItemID, Item>([
  PREFIXES.ITEM,
]);
const [useCharacter, useCharacterByID] = generateShallowQueries<
  CharacterID,
  Character
>([PREFIXES.CHARACTER]);
const [useLocation, useLocationByID] = generateShallowQueries<
  LocationID,
  Location
>([PREFIXES.LOCATION]);
const [useCampaignPlan, useCampaignPlanByID] = generateShallowQueries<
  CampaignID,
  CampaignPlan
>([PREFIXES.CAMPAIGN_PLAN]);
const [useAgentConfig, useAgentConfigByID] = generateShallowQueries<
  AgentConfigID,
  AgentConfig
>([PREFIXES.AGENT_CONFIG]);
const usePointByCampaignAndID = generateNestedQuery<CampaignID, Point, PointID>(
  'campaign_points',
); // endpoint: /api/campaign/campaign_points/campplan/{campaign_numeric}/p/{point_numeric}
// const useObjectiveByCampaignAndID = generateNestedQuery<CampaignID, Objective, ObjectiveID>('campaign_objectives') // TODO: Implement when needed
// TODO: Find better endpoint names for nested queries

// Mutation factories
const generateCreateMutation = <CreateType, RetType extends Object>(
  prefix: string,
) => {
  return () => {
    const queryClient = useQueryClient();
    return useMutation({
      mutationFn: async (data: CreateType): Promise<RetType> => {
        const response = await fetch(`${BASE_API_URL}${prefix.toLowerCase()}`, {
          method: 'POST',
          headers: authHeaders({ 'Content-Type': 'application/json' }),
          body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error('Create failed');
        return await response.json();
      },
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: [[prefix]] });
      },
    });
  };
};

const generateUpdateMutation = <
  UpdateType extends Object,
  RetType extends Object,
>(
  prefix: string,
) => {
  return () => {
    const queryClient = useQueryClient();
    return useMutation({
      mutationFn: async (data: UpdateType): Promise<RetType> => {
        const id = (data as { obj_id: AnyID }).obj_id;
        const response = await fetch(
          `${BASE_API_URL}${prefix.toLowerCase()}/${id.numeric}`,
          {
            method: 'PUT',
            headers: authHeaders({ 'Content-Type': 'application/json' }),
            body: JSON.stringify(data),
          },
        );
        if (!response.ok) throw new Error('Update failed');
        return await response.json();
      },
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: [[prefix]] });
      },
    });
  };
};

const generateDeleteMutation = (prefix: string) => {
  return () => {
    const queryClient = useQueryClient();
    return useMutation({
      mutationFn: async (id: AnyID): Promise<{ success: boolean }> => {
        const response = await fetch(
          `${BASE_API_URL}${prefix.toLowerCase()}/${id.numeric}`,
          {
            method: 'DELETE',
            headers: authHeaders(),
          },
        );
        if (!response.ok) throw new Error('Delete failed');
        return await response.json();
      },
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: [[prefix]] });
      },
    });
  };
};

// Create mutations
const useCreateRule = generateCreateMutation<RuleCreate, Rule>(PREFIXES.RULE);
const useCreateObjective = generateCreateMutation<ObjectiveCreate, Objective>(
  PREFIXES.OBJECTIVE,
);
const useCreatePoint = generateCreateMutation<PointCreate, Point>(
  PREFIXES.POINT,
);
const useCreateSegment = generateCreateMutation<SegmentCreate, Segment>(
  PREFIXES.SEGMENT,
);
const useCreateArc = generateCreateMutation<ArcCreate, Arc>(PREFIXES.ARC);
const useCreateItem = generateCreateMutation<ItemCreate, Item>(PREFIXES.ITEM);
const useCreateCharacter = generateCreateMutation<CharacterCreate, Character>(
  PREFIXES.CHARACTER,
);
const useCreateLocation = generateCreateMutation<LocationCreate, Location>(
  PREFIXES.LOCATION,
);
const useCreateCampaignPlan = generateCreateMutation<
  CampaignPlanCreate,
  CampaignPlan
>(PREFIXES.CAMPAIGN_PLAN);
const useCreateAgentConfig = generateCreateMutation<
  AgentConfigCreate,
  AgentConfig
>(PREFIXES.AGENT_CONFIG);

// Update mutations
const useUpdateRule = generateUpdateMutation<RuleUpdate, Rule>(PREFIXES.RULE);
const useUpdateObjective = generateUpdateMutation<ObjectiveUpdate, Objective>(
  PREFIXES.OBJECTIVE,
);
const useUpdatePoint = generateUpdateMutation<PointUpdate, Point>(
  PREFIXES.POINT,
);
const useUpdateSegment = generateUpdateMutation<SegmentUpdate, Segment>(
  PREFIXES.SEGMENT,
);
const useUpdateArc = generateUpdateMutation<ArcUpdate, Arc>(PREFIXES.ARC);
const useUpdateItem = generateUpdateMutation<ItemUpdate, Item>(PREFIXES.ITEM);
const useUpdateCharacter = generateUpdateMutation<CharacterUpdate, Character>(
  PREFIXES.CHARACTER,
);
const useUpdateLocation = generateUpdateMutation<LocationUpdate, Location>(
  PREFIXES.LOCATION,
);
const useUpdateCampaignPlan = generateUpdateMutation<
  CampaignPlanUpdate,
  CampaignPlan
>(PREFIXES.CAMPAIGN_PLAN);
const useUpdateAgentConfig = generateUpdateMutation<
  AgentConfigUpdate,
  AgentConfig
>(PREFIXES.AGENT_CONFIG);

// Delete mutations
const useDeleteRule = generateDeleteMutation(PREFIXES.RULE);
const useDeleteObjective = generateDeleteMutation(PREFIXES.OBJECTIVE);
const useDeletePoint = generateDeleteMutation(PREFIXES.POINT);
const useDeleteSegment = generateDeleteMutation(PREFIXES.SEGMENT);
const useDeleteArc = generateDeleteMutation(PREFIXES.ARC);
const useDeleteItem = generateDeleteMutation(PREFIXES.ITEM);
const useDeleteCharacter = generateDeleteMutation(PREFIXES.CHARACTER);
const useDeleteLocation = generateDeleteMutation(PREFIXES.LOCATION);
const useDeleteCampaignPlan = generateDeleteMutation(PREFIXES.CAMPAIGN_PLAN);
const useDeleteAgentConfig = generateDeleteMutation(PREFIXES.AGENT_CONFIG);

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

export {
  // Query hooks
  useRule,
  useRuleByID,
  useObjective,
  useObjectiveByID,
  usePoint,
  usePointByID,
  useSegment,
  useSegmentByID,
  useArc,
  useArcByID,
  useItem,
  useItemByID,
  useCharacter,
  useCharacterByID,
  useLocation,
  useLocationByID,
  useCampaignPlan,
  useCampaignPlanByID,
  useAgentConfig,
  useAgentConfigByID,
  usePointByCampaignAndID,
  // Create mutations
  useCreateRule,
  useCreateObjective,
  useCreatePoint,
  useCreateSegment,
  useCreateArc,
  useCreateItem,
  useCreateCharacter,
  useCreateLocation,
  useCreateCampaignPlan,
  useCreateAgentConfig,
  // Update mutations
  useUpdateRule,
  useUpdateObjective,
  useUpdatePoint,
  useUpdateSegment,
  useUpdateArc,
  useUpdateItem,
  useUpdateCharacter,
  useUpdateLocation,
  useUpdateCampaignPlan,
  useUpdateAgentConfig,
  // Delete mutations
  useDeleteRule,
  useDeleteObjective,
  useDeletePoint,
  useDeleteSegment,
  useDeleteArc,
  useDeleteItem,
  useDeleteCharacter,
  useDeleteLocation,
  useDeleteCampaignPlan,
  useDeleteAgentConfig,
};
