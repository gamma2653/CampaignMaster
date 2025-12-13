import { withFieldGroup } from "../ctx";
import { Arc, CampaignPlan, Point, PREFIXES } from "../../../../schemas";
import { ArcGroup, defaultValues as arcDefaultValues } from "./ArcGroup";
import { CharacterGroup, defaultValues as characterDefaultValues } from "./CharacterGroup";
import { LocationGroup, defaultValues as locationDefaultValues } from "./LocationGroup";
import { ItemGroup, defaultValues as itemDefaultValues } from "./ItemGroup";
import { RuleGroup, defaultValues as ruleDefaultValues } from "./RuleGroup";
import { ObjectiveGroup, defaultValues as objectiveDefaultValues } from "./ObjectiveGroup";
import { PointGroup, defaultValues as pointDefaultValues } from "./PointGroup";

const defaultValues = {
    obj_id: { prefix: PREFIXES.CAMPAIGN_PLAN, numeric: 0 },
    title: '',
    version: '',
    setting: '',
    summary: '',
    storyline: [] as Arc[],
    storypoints: [] as Point[],
    characters: [],
    locations: [],
    items: [],
    rules: [],
    objectives: [],
} as CampaignPlan


export const CampaignPlanGroup = withFieldGroup({
    defaultValues,
    render: ({ group }) => {
        return (
            <div style={{ border: '1px solid #ccc', padding: '10px', marginBottom: '10px' }}>
                <group.AppField name="obj_id">
                    {(field) => <field.IDDisplayField />}
                </group.AppField>
                <group.AppField name="title">
                    {(field) => <field.TextField label="Campaign Plan Title" />}
                </group.AppField>
                <group.AppField name="version">
                    {(field) => <field.TextField label="Campaign Plan Version" />}
                </group.AppField>
                <group.AppField name="setting">
                    {(field) => <field.TextField label="Campaign Plan Setting" />}
                </group.AppField>
                <group.AppField name="summary">
                    {(field) => <field.TextField label="Campaign Plan Summary" />}
                </group.AppField>
                <group.AppField name="storypoints" mode="array">
                    {(field) => (
                        <div>
                            <h3>Story Points (discrete)</h3>
                            {group.state.values.storypoints.map((_, index) => (
                                <div key={index} style={{ border: '1px solid #ccc', padding: '10px', marginBottom: '10px' }}>
                                    <h4>Point {index + 1}</h4>
                                    <PointGroup
                                        form={group}
                                        fields={`storypoints[${index}]`}
                                    />
                                </div>
                            ))}
                            <button
                                type="button"
                                onClick={() => {
                                    field.pushValue(pointDefaultValues)
                                }}
                            >
                                Add Story Point
                            </button>
                        </div>
                    )}
                </group.AppField>
                <group.AppField name="storyline" mode="array">
                    {(field) => (
                        <div>
                            <h3>Storyline (continuous)</h3>
                            {group.state.values.storyline.map((_, index) => (
                                <div key={index} style={{ border: '1px solid #ccc', padding: '10px', marginBottom: '10px' }}>
                                    <h4>Storypoint {index + 1}</h4>
                                    <ArcGroup
                                        form={group}
                                        fields={`storyline[${index}]`}
                                        points={group.state.values.storypoints}
                                    />
                                </div>
                            ))}
                            <button
                                type="button"
                                onClick={() => {
                                    field.pushValue(arcDefaultValues)
                                }}
                            >
                                Add Storypoint
                            </button>
                        </div>
                    )}
                </group.AppField>
                <group.AppField name="characters" mode="array">
                    {(field) => (
                        <div>
                            <h3>Characters</h3>
                            {group.state.values.characters.map((_, index) => (
                                <div key={index} style={{ border: '1px solid #ccc', padding: '10px', marginBottom: '10px' }}>
                                    <h4>Character {index + 1}</h4>
                                    <CharacterGroup
                                        form={group}
                                        fields={`characters[${index}]`}
                                    />
                                </div>
                            ))}
                            <button
                                type="button"
                                onClick={() => {
                                    field.pushValue(characterDefaultValues)
                                }}
                            >
                                Add Character
                            </button>
                        </div>
                    )}
                </group.AppField>
                <group.AppField name="locations" mode="array">
                    {(field) => (
                        <div>
                            <h3>Locations</h3>
                            {group.state.values.locations.map((_, index) => (
                                <div key={index} style={{ border: '1px solid #ccc', padding: '10px', marginBottom: '10px' }}>
                                    <h4>Location {index + 1}</h4>
                                    <LocationGroup
                                        form={group}
                                        fields={`locations[${index}]`}
                                    />
                                </div>
                            ))}
                            <button
                                type="button"
                                onClick={() => {
                                    field.pushValue(locationDefaultValues)
                                }}
                            >
                                Add Location
                            </button>
                        </div>
                    )}
                </group.AppField>
                <group.AppField name="items" mode="array">
                    {(field) => (
                        <div>
                            <h3>Items</h3>
                            {group.state.values.items.map((_, index) => (
                                <div key={index} style={{ border: '1px solid #ccc', padding: '10px', marginBottom: '10px' }}>
                                    <h4>Item {index + 1}</h4>
                                    <ItemGroup
                                        form={group}
                                        fields={`items[${index}]`}
                                    />
                                </div>
                            ))}
                            <button type="button" onClick={() => field.pushValue(itemDefaultValues)}>
                                Add Item
                            </button>
                        </div>
                    )}
                </group.AppField>
                <group.AppField name="rules" mode="array">
                    {(field) => (
                        <div>
                            <h3>Rules</h3>
                            {group.state.values.rules.map((_, index) => (
                                <div key={index} style={{ border: '1px solid #ccc', padding: '10px', marginBottom: '10px' }}>
                                    <h4>Rule {index + 1}</h4>
                                    <RuleGroup
                                        form={group}
                                        fields={`rules[${index}]`}
                                    />
                                </div>
                            ))}
                            <button type="button" onClick={() => field.pushValue(ruleDefaultValues)}>
                                Add Rule
                            </button>
                        </div>
                    )}
                </group.AppField>
                <group.AppField name="objectives" mode="array">
                    {(field) => (
                        <div>
                            <h3>Objectives</h3>
                            {group.state.values.objectives.map((_, index) => (
                                <div key={index} style={{ border: '1px solid #ccc', padding: '10px', marginBottom: '10px' }}>
                                    <h4>Objective {index + 1}</h4>
                                    <ObjectiveGroup
                                        form={group}
                                        fields={`objectives[${index}]`}
                                    />
                                </div>
                            ))}
                            <button type="button" onClick={() => field.pushValue(objectiveDefaultValues)}>
                                Add Objective
                            </button>
                        </div>
                    )}
                </group.AppField>
            </div>
        )
    }
})