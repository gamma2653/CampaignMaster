import { formOptions, createFieldMap } from '@tanstack/react-form'
import { useAppForm, withForm } from './new_ctx'
import { CampaignPlanFieldGroup } from './fieldgroups'
import { defaultCampaignPlanValues } from './new_fields'


// export const campaignPlanOpts = formOptions(campaignPlanOpts)

const fieldMap = createFieldMap(defaultCampaignPlanValues)

export const CampaignPlanForm = () => {
    const form = useAppForm({
        defaultValues: defaultCampaignPlanValues,
        onSubmit: ({ value }) => console.log(value)
    })
    console.log('CampaignForm defaultValues:', defaultCampaignPlanValues)
    return (
        <form.AppForm>
            <CampaignPlanFieldGroup
                form={form}
                label="Campaign Plan"
                fields={fieldMap}
            />
        </form.AppForm>
    )
}


// export const CampaignPlanForm = () => {
//     const form = useAppForm({
//         defaultValues: campaignPlanOpts.defaultValues,
//         onSubmit: ({ value }) => console.log(value)
//     })

//     return (
//         <form
//             className="flex flex-col gap-2 w-[400px]"
//             onSubmit={(e) => {
//                 e.preventDefault()
//                 form.handleSubmit()
//             }}
//         >
//             <form.AppField
//                 name="obj_id"
//                 children={
//                     (field) => <field.IDField prefix={PREFIXES.CAMPAIGN} />
//                 }
//             />
//             <form.AppField
//                 name="title"
//                 children={
//                     (field) => <field.TextField label="Title" />
//                 }
//             />
//             <form.AppField
//                 name="version"
//                 children={
//                     (field) => <field.TextField label="Version" />
//                 }
//             />
//             <form.AppField
//                 name="setting"
//                 children={
//                     (field) => <field.TextField label="Setting" />
//                 }
//             />
//             <form.AppField
//                 name="summary"
//                 children={
//                     (field) => <field.TextField label="Summary" />
//                 }
//             />
//             <form.AppField
//                 name="storypoints"
//                 mode="array"
//                 children={(arcField) => (
//                     // arcField ~= Arc[]
//                     <div>
//                         {arcField.state.value.map((_, i) => (
//                             <div>
//                                 <form.AppField
//                                     key={i}
//                                     name={`storypoints[${i}].name`}
//                                     children={(
//                                         (arcNameField) => (
//                                             // arcNameField ~= Arc[i].name
//                                             <div>
//                                                 <label>
//                                                     <div>Story Arc</div>
//                                                     <input
//                                                         value={arcNameField.state.value}
//                                                         onChange={(e) =>
//                                                             arcNameField.handleChange(e.target.value)
//                                                         }
//                                                     />
//                                                 </label>
//                                             </div>
//                                         )
//                                     )}
//                                 />
//                                 <form.AppField key={i} name={`storypoints[${i}].description`}>
//                                     {(arcDescriptionField) => (
//                                         // arcDescriptionField ~= Arc[i].description
//                                         <div>
//                                             <label>
//                                                 <div>Story Arc</div>
//                                                 <input
//                                                     value={arcDescriptionField.state.value}
//                                                     onChange={(e) =>
//                                                         arcDescriptionField.handleChange(e.target.value)
//                                                     }
//                                                 />
//                                             </label>
//                                         </div>
//                                     )}
//                                 </form.AppField>
//                                 <form.AppField
//                                     key={i}
//                                     name={`storypoints[${i}].segments`}
//                                     mode="array"
//                                     children={()}
//                                 >
//                                     {(subField) => (
//                                         // Arc
//                                         <div>
//                                             <label>
//                                                 <div>Story Arc</div>
//                                                 <input
//                                                     value={subField.state.value}
//                                                     onChange={(e) =>
//                                                         subField.handleChange(e.target.value)
//                                                     }
//                                                 />
//                                             </label>
//                                         </div>
//                                     )}
//                                 </form.AppField>
//                             </div>
//                         )
//                         )}
//                     </div>
//                 )}
//             />
//         </form>
//     )

// }