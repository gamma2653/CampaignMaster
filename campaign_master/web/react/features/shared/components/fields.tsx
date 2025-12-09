import { useStore, formOptions } from '@tanstack/react-form'
import { fieldContext, useFieldContext, formContext, useFormContext } from './ctx'
import type { AnyID, Arc, CampaignPlan, Character, Item, Objective, Point, Rule, Segment, PREFIXES_T } from '../../../schemas'
import { PREFIXES } from '../../../schemas'
import type { useAppForm_RT } from './forms'
// import type { UpdateMetaOptions } from '@tanstack/react-form'




const FIELD_PREFIX_SEP = '.'

const gen_prefix = ({prior_prefix: exisitng_prefix, parts}: {prior_prefix?: string, parts: string[]}) => {
    return [...(exisitng_prefix?.split(FIELD_PREFIX_SEP) || []), ...parts].filter(Boolean).join(FIELD_PREFIX_SEP)
}

export const campaignPlanOpts = formOptions({
    defaultValues: {
        obj_id: {
            prefix: PREFIXES.CAMPAIGN,
            numeric: 0,
        },
        title: '',
        version: '',
        setting: '',
        summary: '',
        storypoints: [],
        characters: [],
        locations: [],
        items: [],
        rules: [],
        objectives: [],
    } as CampaignPlan
})

export const arcOpts = formOptions({
    defaultValues: {
        obj_id: {
            prefix: PREFIXES.ARC,
            numeric: 0,
        },
        name: '',
        description: '',
        segments: [],
    } as Arc
})


export const segmentOpts = formOptions({
    defaultValues: {
        obj_id: {
            prefix: PREFIXES.SEGMENT,
            numeric: 0,
        },
        name: '',
        description: '',
        start: null,
        end: null,
    } as Segment
})

export const pointOpts = formOptions({
    defaultValues: {
        obj_id: {
            prefix: PREFIXES.POINT,
            numeric: 0,
        },
        name: '',
        description: '',
        objective: null,
    } as Point
})


export const ruleOpts = formOptions({
    defaultValues: {
        obj_id: {
            prefix: PREFIXES.RULE,
            numeric: 0,
        },
        name: '',
        description: '',
        effect: '',
        components: [],
    } as Rule
})


export const campaignOpts = formOptions({
    defaultValues: {
        campaign_plan: campaignPlanOpts.defaultValues,
    } as { campaign_plan: CampaignPlan }
})

export const itemsOpts = formOptions({
    defaultValues: {
        obj_id: {
            prefix: PREFIXES.ITEM,
            numeric: 0,
        },
        name: '',
        type_: '',
        description: '',
        properties: {},
    } as Item
})

export function TextField({ label, prior_prefix }: { label: string; prior_prefix?: string }) {
    const field = useFieldContext<string>()
    const errors = useStore(
        field.store,
        (state) => state.meta.errors
    )

    // const style = useFormContext()?.formProps?.errorMessageStyle

    return (
        <div>
            <label>
                <div>{label}</div>
                <input
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                    onBlur={field.handleBlur}
                />
            </label>
            {errors.map((error: string) => (
                <div key={error} style={{ color: 'red' }}>
                    {error}
                </div>
            ))}
        </div>
    )
}

export function SubscribeButton({ label }: { label: string }) {
    const form = useFormContext()
    return (
        <form.Subscribe selector={(state) => state.isSubmitting}>
            {(isSubmitting) => <button disabled={isSubmitting}>{label}</button>}
        </form.Subscribe>
    )
}

export function IDField({ label, prefix, prior_prefix }: { label: string; prefix: PREFIXES_T; prior_prefix?: string }) {
    // Prefix is passed as a prop, user only has access to edit numeric part
    // const field = useFieldContext<{ numeric: number }>()
    const field = useFieldContext<AnyID>()
    // const form = field.form as useAppForm_RT
    return (
        <div>
            <label>
                <div>{label}</div>
                <input
                    value={`${prefix}-${field.state.value?.numeric}`}
                    onChange={(e) => {
                        const [, numeric] = e.target.value.split('-')
                        field.handleChange({ prefix, numeric: parseInt(numeric) })
                    }}
                />
            </label>
        </div>
    )
}


export const PointField = ({prior_prefix, label}: {prior_prefix?: string, label?: string}) => {
    const point_label = label || 'Point'
    const field = useFieldContext<Point>()
    const form = field.form as useAppForm_RT
    return (
        <div>
            <h1>{point_label}</h1>
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'obj_id']})}
                children={(field) => <field.IDField label="Point ID" prefix={PREFIXES.POINT} />}
            />
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'name']})}
                children={(field) => <field.TextField label="Point Name" />}
            />
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'description']})}
                children={(field) => <field.TextField label="Point Description" />}
            />
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'objective']})}
                children={(field) => <field.IDField label="Objective" prefix={PREFIXES.OBJECTIVE} />}
            />
        </div>
    )
}

export const SegmentField = ({prior_prefix}: {prior_prefix?: string}) => {
    const field = useFieldContext<Segment>()
    const form = field.form as useAppForm_RT
    console.log(`Segment constructor called!`)
    console.log(`field.state.value=`, field.state.value)
    return (
        <div>
            <h1>Segment</h1>
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'obj_id']})}
                children={(field) => <field.IDField label="Segment ID" prefix={PREFIXES.SEGMENT} />}
            />
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'name']})}
                children={(field) => <field.TextField label="Segment Name" />}
            />
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'description']})}
                children={(field) => <field.TextField label="Segment Description" />}
            />
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'start']})}
                children={(field) => <field.PointField label="Start Point" />}
            />
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'end']})}
                children={(field) => <field.PointField label="End Point" />}
            />
        </div>
    )
}

export const ArcField = ({prior_prefix}: {prior_prefix?: string}) => {
    const field = useFieldContext<Arc>()
    const form = field.form as useAppForm_RT
    console.log(`Arc constructor called!`)
    console.log(`field.state.value=`, field.state.value)
    // console.log(`field.state.value type=`, typeof field.state.value)
    // console.log(`fiels.state.value keys=`, Object.keys(field.state.value))
    // console.log(`field.state.value values=`, Object.values(field.state.value))
    return (
        <div>
            <h1>Arc</h1>
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'obj_id']})}
                children={(field) => <field.IDField label="Arc ID" prefix={PREFIXES.ARC} />}
            />
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'name']})}
                children={(field) => <field.TextField label="Arc Name" />}
            />
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'description']})}
                children={(field) => <field.TextField label="Arc Description" />}
            />
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'segments']})}
                mode="array"
                children={(field) => (
                    <div className={`segment-array-field`}>
                        {(field.state.value as Segment[])?.map((_, i) => {
                            return (
                                <div key={i} style={{ border: '1px solid black', margin: '10px' }}>
                                    <SegmentField prior_prefix={gen_prefix({prior_prefix, parts: [field.name, 'segments', i.toString()]})} />
                                </div>
                            )
                        })}
                        <button type="button" onClick={
                            () => {
                                console.log(`Previous field value: `, field.state.value)
                                console.log(`Appending: `, segmentOpts.defaultValues)
                                //@ts-ignore  <- Due to needing useAppForm_RT, TS cannot infer properly
                                field.pushValue(segmentOpts.defaultValues)
                                // object is always first value
                                // const editing_val = field.state.value as Segment[] || []
                                // editing_val.push(segmentOpts.defaultValues)
                                // field.updateValue(editing_val)
                                console.log(`New field value: `, field.state.value)
                        }
                        }>
                            Add Segment
                        </button>
                    </div>
                )}
            />
        </div>
    )
}

export const RuleField = ({prior_prefix}: {prior_prefix?: string}) => {
    const field = useFieldContext<Rule>()
    const form = field.form as useAppForm_RT
    return (
        <div>
            <h1>Rule</h1>
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'obj_id']})}
                children={(field) => <field.IDField label="Rule ID" prefix={PREFIXES.RULE} />}
            />
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'description']})}
                children={(field) => <field.TextField label="Rule Description" />}
            />
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'effect']})}
                children={(field) => <field.TextField label="Rule Effect" />}
            />
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'components']})}
                mode="array"
                children={(field) => (
                    <div>
                        {(field.state.value as string[])?.map((_, i) => (
                            <div key={i}>
                                <h2>Component {i + 1}</h2>
                                <field.TextField label={`Component ${i + 1}`} />
                            </div>
                        ))}
                        <button type="button" onClick={ //@ts-ignore  <- see above
                            () => field.pushValue('')
                        }> 
                            Add Rule Component
                        </button>
                    </div>
                )}
            />
        </div>
    )
}


export const ObjectiveField = ({prior_prefix}: {prior_prefix?: string}) => {
    const field = useFieldContext<Objective>()
    const form = field.form as useAppForm_RT
    return (
        <div>
            <h1>Objective</h1>
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'obj_id']})}
                children={(field) => <field.IDField label="Objective ID" prefix={PREFIXES.OBJECTIVE} />}
            />
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'description']})}
                children={(field) => <field.TextField label="Objective Description" />}
            />
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'components']})}
                mode="array"
                children={(field) => (
                    <div>
                        {(field.state.value as string[])?.map((_, i) => (
                            <div key={i}>
                                <h2>Component {i + 1}</h2>
                                <field.TextField label={`Component ${i + 1}`} />
                            </div>
                        ))}
                        <button type="button" onClick={ //@ts-ignore  <- see above
                            () => field.pushValue('')
                        }>
                            Add Objective Component
                        </button>
                    </div>
                )}
            />
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'prerequisites']})}
                mode="array"
                children={(field) => (
                    <div>
                        {(field.state.value as string[])?.map((_, i) => (
                            <div key={i}>
                                <h2>Prerequisite {i + 1}</h2>
                                <field.TextField label={`Prerequisite ${i + 1}`} />
                            </div>
                        ))}
                        <button type="button" onClick={ //@ts-ignore  <- see above
                            () => field.pushValue('')
                        }>
                            Add Prerequisite
                        </button>
                    </div>
                )}
            />
        </div>
    )
}


export const ItemField = ({prior_prefix}: {prior_prefix?: string}) => {
    const field = useFieldContext<Item>()
    const form = field.form as useAppForm_RT
    return (
        <div>
            <h1>Item</h1>
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'obj_id']})}
                children={(field) => <field.IDField label="Item ID" prefix={PREFIXES.ITEM} />}
            />
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'name']})}
                children={(field) => <field.TextField label="Item Name" />}
            />
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'type_']})}
                children={(field) => <field.TextField label="Item Type" />}
            />
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'description']})}
                children={(field) => <field.TextField label="Item Description" />}
            />
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'properties']})}
                mode="array"
                children={(field) => (
                    <div>
                        {(field.state.value as [string, string][])?.map((_, i) => (
                            <div key={i}>
                                <h2>Property {i + 1}</h2>
                                <field.TextField label={`Property ${i + 1} Key`} />
                                <field.TextField label={`Property ${i + 1} Value`} />
                            </div>
                        ))}
                        <button type="button" onClick={ //@ts-ignore  <- see above
                            () => field.pushValue(['', ''])
                        }>
                            Add Property
                        </button>
                    </div>
                )}
            />
        </div>
    )
}

export const CharacterField = ({prior_prefix}: {prior_prefix?: string}) => {
    const field = useFieldContext<Character>()
    const form = field.form as useAppForm_RT
    return (
        <div>
            <h1>Character</h1>
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'obj_id']})}
                children={(field) => <field.IDField label="Character ID" prefix={PREFIXES.CHARACTER} />}
            />
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'name']})}
                children={(field) => <field.TextField label="Character Name" />}
            />
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'role']})}
                children={(field) => <field.TextField label="Character Role" />}
            />
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'backstory']})}
                children={(field) => <field.TextField label="Character Backstory" />}
            />
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'attributes']})}
                mode="array"
                children={(field) => (
                    <div>
                        {(field.state.value as [string, string][])?.map((_, i) => (
                            <div key={i}>
                                <h2>Attribute {i + 1}</h2>
                                <field.TextField label={`Attribute ${i + 1} Key`} />
                                <field.TextField label={`Attribute ${i + 1} Value`} />
                            </div>
                        ))}
                        <button type="button" onClick={ //@ts-ignore  <- see above
                            () => field.pushValue(['', ''])
                        }>
                            Add Attribute
                        </button>
                    </div>
                )}
            />
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'skills']})}
                mode="array"
                children={(field) => (
                    <div>
                        {(field.state.value as [string, string][])?.map((_, i) => (
                            <div key={i}>
                                <h2>Skill {i + 1}</h2>
                                <field.TextField label={`Skill ${i + 1} Name`} />
                                <field.TextField label={`Skill ${i + 1} Level`} />
                            </div>
                        ))}
                        <button type="button" onClick={ //@ts-ignore  <- see above
                            () => field.pushValue(['', ''])
                        }>
                            Add Skill
                        </button>
                    </div>
                )}
            />
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'inventory']})}
                mode="array"
                children={(field) => (
                    <div>
                        {(field.state.value as string[])?.map((_, i) => (
                            <div key={i}>
                                <h2>Item {i + 1}</h2>
                                <field.IDField label={`Item ${i + 1} ID`} prefix={PREFIXES.ITEM} />
                            </div>
                        ))}
                        <button type="button" onClick={ //@ts-ignore  <- see above
                            // () => field.pushValue([''])  // TODO
                            () => null
                        }>
                            Add Item
                        </button>
                    </div>
                )}
            />
        </div>

    )
}

export const LocationField = ({prior_prefix}: {prior_prefix?: string}) => {
    const field = useFieldContext<Location>()
    const form = field.form as useAppForm_RT
    return (
        <div>
            <h1>Location</h1>
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'obj_id']})}
                children={(field) => <field.IDField label="Location ID" prefix={PREFIXES.LOCATION} />}
            />
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'name']})}
                children={(field) => <field.TextField label="Location Name" />}
            />
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'description']})}
                children={(field) => <field.TextField label="Location Description" />}
            />
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'neighboring_locations']})}
                mode="array"
                children={(field) => (
                    <div>
                        {(field.state.value as string[])?.map((_, i) => (
                            <div key={i}>
                                <h2>Neighboring Location {i + 1}</h2>
                                <field.IDField label={`Neighboring Location ${i + 1} ID`} prefix={PREFIXES.LOCATION} />
                            </div>
                        ))}
                        <button type="button" onClick={ //@ts-ignore  <- see above
                            // () => field.pushValue(itemsOpts.defaultValues) // TODO
                            () => null
                        }>
                            Add Neighboring Location
                        </button>
                    </div>
                )}
            />
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'coords']})}
                // Give three inputs for x, y, z, z is optional
                children={(field) => (
                    <div>
                        <h2>Coordinates</h2>
                        <field.TextField label="X" />
                        <field.TextField label="Y" />
                        <field.TextField label="Z (optional)" />
                    </div>
                )}
            />
        </div>
    )
}

export const CampaignPlanField = ({prior_prefix}: {prior_prefix?: string}) => {
    const field = useFieldContext<CampaignPlan>()
    const form = field.form as useAppForm_RT
    return (
        <div>
            <h1>Campaign Plan</h1>
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'obj_id']})}
                children={(field) => <field.IDField label="Campaign ID" prefix={PREFIXES.CAMPAIGN} />}
            />
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'title']})}
                children={(field) => <field.TextField label="Campaign Title" />}
            />
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'version']})}
                children={(field) => <field.TextField label="Campaign Version" />}
            />
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'setting']})}
                children={(field) => <field.TextField label="Campaign Setting" />}
            />
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'summary']})}
                children={(field) => <field.TextField label="Campaign Summary" />}
            />
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'storypoints']})}
                mode="array"
                children={(field) => (
                    <div>
                        {Object.values(field.state.value as Arc[])?.map((_, i) => {
                            console.log(`Rendering Storypoint Arc at index ${i}: `, field.state.value[i])
                            return (
                                <div key={i} style={{ border: '1px solid black', margin: '10px' }}>
                                    <ArcField prior_prefix={gen_prefix({prior_prefix, parts: [field.name, 'storypoints', i.toString()]})} />
                                </div>
                            )
                        })}
                        <button type="button" onClick={
                            () => {
                                //@ts-ignore  <- see above
                                field.pushValue(arcOpts.defaultValues)
                                console.log(`Appending to storypoints: `, arcOpts.defaultValues)
                            }
                        }>
                            Add Arc
                        </button>
                    </div>
                )}
            />

            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'characters']})}
                mode="array"
                children={(field) => (
                    <div>
                        {(field.state.value as Arc[])?.map((_, i) => (
                            <div key={i} style={{ border: '1px solid black', margin: '10px' }}>
                                <CharacterField prior_prefix={gen_prefix({prior_prefix, parts: [field.name, 'characters', i.toString()]})} />
                            </div>
                        ))}
                        <button type="button" onClick={ //@ts-ignore  <- see above
                            () => field.pushValue(characterOpts.defaultValues)
                        }>
                            Add Character
                        </button>
                    </div>
                )}
            />
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'locations']})}
                mode="array"
                children={(field) => (
                    <div>
                        {(field.state.value as Arc[])?.map((_, i) => (
                            <div key={i} style={{ border: '1px solid black', margin: '10px' }}>
                                <LocationField prior_prefix={gen_prefix({prior_prefix, parts: [field.name, 'locations', i.toString()]})} />
                            </div>
                        ))}
                        <button type="button" onClick={ //@ts-ignore  <- see above
                            () => field.pushValue(locationOpts.defaultValues)
                        }>
                            Add Location
                        </button>
                    </div>
                )}
            />
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'items']})}
                mode="array"
                children={(field) => (
                    <div>
                        {(field.state.value as Item[])?.map((_, i) => (
                            <div key={i} style={{ border: '1px solid black', margin: '10px' }}>
                                <ItemField prior_prefix={gen_prefix({prior_prefix, parts: [field.name, 'items', i.toString()]})} />
                            </div>
                        ))}
                        <button type="button" onClick={ //@ts-ignore  <- see above
                            () => field.pushValue(itemsOpts.defaultValues)
                        }>
                            Add Item
                        </button>
                    </div>
                )}
            />
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'rules']})}
                mode="array"
                children={(field) => (
                    <div>
                        {(field.state.value as Rule[])?.map((_, i) => (
                            <div key={i} style={{ border: '1px solid black', margin: '10px' }}>
                                <RuleField prior_prefix={gen_prefix({prior_prefix, parts: [field.name, 'rules', i.toString()]})} />
                            </div>
                        ))}
                        <button type="button" onClick={ //@ts-ignore  <- see above
                            () => field.pushValue(ruleOpts.defaultValues)
                        }>
                            Add Rule
                        </button>
                    </div>
                )}
            />
            <form.AppField
                name={gen_prefix({prior_prefix, parts: [field.name, 'objectives']})}
                mode="array"
                children={(field) => (
                    <div>
                        {(field.state.value as Objective[])?.map((_, i) => (
                            <div key={i} style={{ border: '1px solid black', margin: '10px' }}>
                                <ObjectiveField prior_prefix={gen_prefix({prior_prefix, parts: [field.name, 'objectives', i.toString()]})} />
                            </div>
                        ))}
                        <button type="button" onClick={ //@ts-ignore  <- see above
                            () => field.pushValue(objectiveOpts.defaultValues)
                        }>
                            Add Objective
                        </button>
                    </div>
                )}
            />
        </div>
    )
}


