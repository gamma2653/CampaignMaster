import { withFieldGroup } from "../ctx";
import { Arc, CampaignPlan, PREFIXES } from "../../../../schemas";
import { ObjectIDGroup } from "./ObjectIDGroup";
import { ArcGroup, defaultValues as arcDefaultValues } from "./ArcGroup";
import { CharacterGroup, defaultValues as characterDefaultValues } from "./CharacterGroup";

const defaultValues = {
    obj_id: { prefix: PREFIXES.CAMPAIGN_PLAN, numeric: 0 },
    title: '',
    version: '',
    setting: '',
    summary: '',
    storypoints: [] as Arc[],
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
                <ObjectIDGroup
                    form={group}
                    fields="obj_id"
                />
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
                            <h3>Storypoints</h3>
                            {group.state.values.storypoints.map((_, index) => (
                                <div key={index} style={{ border: '1px solid #ccc', padding: '10px', marginBottom: '10px' }}>
                                    <h4>Storypoint {index + 1}</h4>
                                    <ArcGroup
                                        form={group}
                                        fields={`storypoints[${index}]`}
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
            </div>
        )
    }
})