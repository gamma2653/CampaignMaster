import { createFormHook, formOptions } from '@tanstack/react-form'
import type { CampaignPlan } from '../../../schemas'
import { PREFIXES } from '../../../schemas'
import { TextField, SubscribeButton, IDField } from './fields'
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


const campaignOpts = formOptions({
    defaultValues: {
        obj_id: {
            prefix: 'CampPlan',
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
    }
})




// export const CampaignPlanForm = withForm({
//     ...campaignOpts,
//     // props: {

//     // }
//     render: ({ form }) => {
//         return (
//             <div>
//                 <form.AppField
//                     name="title"
//                     children={(field) => <field.TextField label="Campaign Title" />}
//                 />
//                 <form.AppForm>
//                     <form.SubscribeButton label="Subscribe" />
//                 </form.AppForm>
//             </div>
//         )
//     }
// })


export const CampaignPlanForm = () => {
  const form = useAppForm({
    ...campaignOpts,
  })

  return (
    <div>
        <h1>Campaign Plan</h1>
        <form.AppField
            name="obj_id"
            children={(field) => <field.IDField label="Campaign ID" prefix={PREFIXES.CAMPAIGN} />}
        />
        <form.AppField
            name="title"
            children={(field) => <field.TextField label="Campaign Title" />}
        />
        <form.AppForm>
            <form.SubscribeButton label="Submit" />
        </form.AppForm>
    </div>
  )
}

