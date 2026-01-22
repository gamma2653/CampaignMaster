import { Disclosure, DisclosureButton, DisclosurePanel } from "@headlessui/react";
import { ChevronDownIcon } from '@heroicons/react/20/solid'
import clsx from "clsx";

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
            <div id="campaign-plan-group">
                <h1 className="self-center p-4 font-bold text-xl">Campaign Plan</h1>
                {/* Campaign Plan Metadata */}
                <Disclosure defaultOpen={true}>
                    {({ open }) => (
                        <>
                            <DisclosureButton className="w-full p-2 text-left font-semibold text-lg cursor-pointer border border-blue-900 bg-blue-950">
                                Campaign Plan Metadata
                                <ChevronDownIcon className={clsx('w-5 inline-block', open && 'rotate-180')} />
                            </DisclosureButton>
                            <DisclosurePanel className="flex flex-col gap-4 p-2">
                                <div className="ml-auto">
                                    <group.AppField name="obj_id">
                                        {(field) => <field.IDDisplayField />}
                                    </group.AppField>
                                </div>
                                <div className="p-2 min-w-full">
                                    <group.AppField name="title">
                                        {(field) => <field.TextField label="Campaign Plan Title" />}
                                    </group.AppField>
                                </div>
                                <div className="p-2 min-w-full">
                                    <group.AppField name="version">
                                        {(field) => <field.TextField label="Campaign Plan Version" />}
                                    </group.AppField>
                                </div>
                                <div className="p-2 min-w-full">
                                    <group.AppField name="setting">
                                        {(field) => <field.TextField label="Campaign Plan Setting" />}
                                    </group.AppField>
                                </div>
                                <div className="p-2 min-w-full">
                                    <group.AppField name="summary">
                                        {(field) => <field.TextAreaField label="Campaign Plan Summary" />}
                                    </group.AppField>
                                </div>
                            </DisclosurePanel>
                        </>
                    )}
                    
                </Disclosure>
                {/* Story Points (discrete) */}
                <Disclosure defaultOpen={true}>
                    {({ open }) => (
                        <>
                            <DisclosureButton className="w-full p-2 text-left font-semibold text-lg cursor-pointer border border-green-900 bg-green-950">
                                Story Points (discrete)
                                <ChevronDownIcon className={clsx('w-5 inline-block', open && 'rotate-180')} />
                            </DisclosureButton>
                            <DisclosurePanel className="flex flex-col gap-6">
                                <group.AppField name="storypoints" mode="array">
                                    {(field) => (
                                        <div className="p-2 min-w-full">
                                            {group.state.values.storypoints.map((_, index) => (
                                                <div key={index} className='border p-2 mb-2'>
                                                    <h4>Point {index + 1}</h4>
                                                    <PointGroup
                                                        form={group}
                                                        fields={`storypoints[${index}]`}
                                                    />
                                                </div>
                                            ))}
                                            <button
                                                type="button"
                                                className="add-button"
                                                onClick={() => {
                                                    field.pushValue(pointDefaultValues)
                                                }}
                                            >
                                                Add Story Point
                                            </button>
                                        </div>
                                    )}
                                </group.AppField>
                            </DisclosurePanel>
                        </>
                    )}
                </Disclosure>
                {/* Storyline Arcs (continuous) */}
                <Disclosure defaultOpen={true}>
                    {({ open }) => (
                        <>
                            <DisclosureButton className="w-full p-2 text-left font-semibold text-lg cursor-pointer border border-purple-900 bg-purple-950">
                                Storyline Arcs (continuous)
                                <ChevronDownIcon className={clsx('w-5 inline-block', open && 'rotate-180')} />
                            </DisclosureButton>
                            <DisclosurePanel className="flex flex-col gap-6">
                                <group.AppField name="storyline" mode="array">
                                    {(field) => (
                                        <div className="p-2 min-w-full">
                                            <h3 className='text-xl'>Storyline (continuous)</h3>
                                            {/* Subscribe to storypoints to ensure dropdowns update when points are added */}
                                            <group.Subscribe selector={(state) => state.values.storypoints}>
                                                {(storypoints) => (
                                                    <>
                                                        {group.state.values.storyline.map((_, index) => (
                                                            <div key={index} className='border p-2 mb-2'>
                                                                {/* <h4>Storypoint {index + 1}</h4> */}
                                                                <ArcGroup
                                                                    form={group}
                                                                    fields={`storyline[${index}]`}
                                                                    points={storypoints}
                                                                />
                                                            </div>
                                                        ))}
                                                    </>
                                                )}
                                            </group.Subscribe>
                                            <button
                                                type="button"
                                                className="add-button"
                                                onClick={() => {
                                                    field.pushValue(arcDefaultValues)
                                                }}
                                            >
                                                Add Storyline Arc
                                            </button>
                                        </div>
                                    )}
                                </group.AppField>
                            </DisclosurePanel>
                        </>
                    )}
                </Disclosure>
                {/* Characters */}
                <Disclosure defaultOpen={true}>
                    {({ open }) => (
                        <>
                            <DisclosureButton className="w-full p-2 text-left font-semibold text-lg cursor-pointer border border-yellow-900 bg-yellow-950">
                                Characters
                                <ChevronDownIcon className={clsx('w-5 inline-block', open && 'rotate-180')} />
                            </DisclosureButton>
                            <DisclosurePanel className="flex flex-col gap-6">
                                <group.AppField name="characters" mode="array">
                                    {(field) => (
                                        <div className="p-2 min-w-full">
                                            <h3 className='text-xl'>Characters</h3>
                                            {group.state.values.characters.map((_, index) => (
                                                <div key={index} className='border p-2 mb-2'>
                                                    {/* <h4>Character {index + 1}</h4> */}
                                                    <CharacterGroup
                                                        form={group}
                                                        fields={`characters[${index}]`}
                                                    />
                                                </div>
                                            ))}
                                            <button
                                                type="button"
                                                className="add-button"
                                                onClick={() => {
                                                    field.pushValue(characterDefaultValues)
                                                }}
                                            >
                                                Add Character
                                            </button>
                                        </div>
                                    )}
                                </group.AppField>
                            </DisclosurePanel>
                        </>
                    )}
                </Disclosure>
                {/* Locations */}
                <Disclosure defaultOpen={true}>
                    {({ open }) => (
                        <>
                            <DisclosureButton className="w-full p-2 text-left font-semibold text-lg cursor-pointer border border-green-900 bg-green-950">
                                Locations
                                <ChevronDownIcon className={clsx('w-5 inline-block', open && 'rotate-180')} />
                            </DisclosureButton>
                            <DisclosurePanel className="flex flex-col gap-6">
                                <group.AppField name="locations" mode="array">
                                    {(field) => (
                                        <div className="p-2 min-w-full">
                                            <h3 className='text-xl'>Locations</h3>
                                            {group.state.values.locations.map((_, index) => (
                                                <div key={index} className='border p-2 mb-2'>
                                                    {/* <h4>Location {index + 1}</h4> */}
                                                    <LocationGroup
                                                        form={group}
                                                        fields={`locations[${index}]`}
                                                    />
                                                </div>
                                            ))}
                                            <button
                                                type="button"
                                                className="add-button"
                                                onClick={() => {
                                                    field.pushValue(locationDefaultValues)
                                                }}
                                            >
                                                Add Location
                                            </button>
                                        </div>
                                    )}
                                </group.AppField>
                            </DisclosurePanel>
                        </>
                    )}
                </Disclosure>
                {/* Items */}
                <Disclosure defaultOpen={true}>
                    {({ open }) => (
                        <>
                            <DisclosureButton className="w-full p-2 text-left font-semibold text-lg cursor-pointer border border-blue-900 bg-blue-950">
                                Items
                                <ChevronDownIcon className={clsx('w-5 inline-block', open && 'rotate-180')} />
                            </DisclosureButton>
                            <DisclosurePanel className="flex flex-col gap-6">
                                <group.AppField name="items" mode="array">
                                    {(field) => (
                                        <div className="p-2 min-w-full">
                                            <h3 className='text-xl'>Items</h3>
                                            {group.state.values.items.map((_, index) => (
                                                <div key={index} className='border p-2 mb-2'>
                                                    {/* <h4>Item {index + 1}</h4> */}
                                                    <ItemGroup
                                                        form={group}
                                                        fields={`items[${index}]`}
                                                    />
                                                </div>
                                            ))}
                                            <button type="button" className="add-button" onClick={() => field.pushValue(itemDefaultValues)}>
                                                Add Item
                                            </button>
                                        </div>
                                    )}
                                </group.AppField>
                            </DisclosurePanel>
                        </>
                    )}
                </Disclosure>
                {/* Rules */}
                <Disclosure defaultOpen={true}>
                    {({ open }) => (
                        <>
                            <DisclosureButton className="w-full p-2 text-left font-semibold text-lg cursor-pointer border border-red-900 bg-red-950">
                                Rules
                                <ChevronDownIcon className={clsx('w-5 inline-block', open && 'rotate-180')} />
                            </DisclosureButton>
                            <DisclosurePanel className="flex flex-col gap-6">
                                <group.AppField name="rules" mode="array">
                                    {(field) => (
                                        <div className="p-2 min-w-full">
                                            <h3 className='text-xl'>Rules</h3>
                                            {group.state.values.rules.map((_, index) => (
                                                <div key={index} className='border p-2 mb-2'>
                                                    {/* <h4>Rule {index + 1}</h4> */}
                                                    <RuleGroup
                                                        form={group}
                                                        fields={`rules[${index}]`}
                                                    />
                                                </div>
                                            ))}
                                            <button type="button" className="add-button" onClick={() => field.pushValue(ruleDefaultValues)}>
                                                Add Rule
                                            </button>
                                        </div>
                                    )}
                                </group.AppField>
                            </DisclosurePanel>
                        </>
                    )}
                </Disclosure>
                {/* Objectives */}
                <Disclosure defaultOpen={true}>
                    {({ open }) => (
                        <>
                            <DisclosureButton className="w-full p-2 text-left font-semibold text-lg cursor-pointer border border-purple-900 bg-purple-950">
                                Objectives
                                <ChevronDownIcon className={clsx('w-5 inline-block', open && 'rotate-180')} />
                            </DisclosureButton>
                            <DisclosurePanel className="flex flex-col gap-6">
                                <group.AppField name="objectives" mode="array">
                                    {(field) => (
                                        <div className="p-2 min-w-full">
                                            <h3 className='text-xl'>Objectives</h3>
                                            {group.state.values.objectives.map((_, index) => (
                                                <div key={index} className='border p-2 mb-2'>
                                                    {/* <h4>Objective {index + 1}</h4> */}
                                                    <ObjectiveGroup
                                                        form={group}
                                                        fields={`objectives[${index}]`}
                                                    />
                                                </div>
                                            ))}
                                            <button type="button" className="add-button" onClick={() => field.pushValue(objectiveDefaultValues)}>
                                                Add Objective
                                            </button>
                                        </div>
                                    )}
                                </group.AppField>
                            </DisclosurePanel>
                        </>
                    )}
                </Disclosure>
            </div>
        )
    }
})