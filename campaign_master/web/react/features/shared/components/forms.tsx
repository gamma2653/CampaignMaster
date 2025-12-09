import { createFormHook, formOptions } from '@tanstack/react-form'
import type { Arc, CampaignPlan, Point, Rule, Segment } from '../../../schemas'
import { PREFIXES } from '../../../schemas'
import { TextField, SubscribeButton, IDField, PointField, CampaignPlanField, arcOpts, campaignOpts } from './fields'
import { fieldContext, formContext } from './ctx'


const { useAppForm, withForm } = createFormHook({
    fieldComponents: {
        /**
         * A text input field component with label and error display.
         * @param param0  Object containing the label for the field.
         * @returns A JSX element representing the text field.
         */
        TextField,/**
        * A field component for editing ID objects with prefix and numeric parts.
        * @param param0  Object containing the label for the field.
        * @returns A JSX element representing the ID field.
        */
        IDField,
        PointField,
        CampaignPlanField,
    },
    formComponents: {
        /**
         * A button component that subscribes to the form's submitting state.
         * @param param0  Object containing the label for the button.
         * @returns A JSX element representing the subscribe button.
         */
        SubscribeButton,
    },
    fieldContext,
    formContext,
})

export type useAppForm_RT = ReturnType<typeof useAppForm>





export const ArcForm = () => {
    const form = useAppForm({
        ...arcOpts,
    })
    return (
        <div>
            <h1>Arc</h1>
            <form.AppField
                name="obj_id"
                children={(field) => <field.IDField label="Arc ID" prefix={PREFIXES.ARC} />}
            />
            <form.AppField
                name="name"
                children={(field) => <field.TextField label="Arc Name" />}
            />
            <form.AppField
                name="description"
                children={(field) => <field.TextField label="Arc Description" />}
            />
            <form.AppField
                name="segments"
                mode="array"
                children={(field) => (
                    <div>
                        {field.state.value.map((_, i) => (
                            <div key={i}>
                                <h2>Segment {i + 1}</h2>
                                {/* <SegmentFormFields /> */}
                            </div>
                        ))}
                    </div>
                )}
            />
        </div>
    )
}

export const CampaignPlanForm = () => {
    const form = useAppForm({
        ...campaignOpts,
    })

    return (
        <div>
            <h1>Campaign Plan</h1>
            {/* Add CampaignPlanField */}
            <form.AppField
                name="campaign_plan"
                children={(field) => <field.CampaignPlanField />}
            />
            <form.AppForm>
                <form.SubscribeButton label="Submit" />
            </form.AppForm>
        </div>
    )
}

