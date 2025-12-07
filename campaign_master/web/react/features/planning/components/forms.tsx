import { CampaignPlanForm } from '../../shared/components/forms'

export { CampaignPlanForm }
// import type { AnyFieldApi } from '@tanstack/react-form'
// // import { useForm } from '@tanstack/react-form'
// import { useAppForm } from '../../shared/components/ctx'

// import type { CampaignPlan } from '../../../schemas'

// function FieldInfo({ field }: { field: AnyFieldApi }) {
//     return (
//         <>
//             {field.state.meta.isTouched && !field.state.meta.isValid ? (
//                 <em className="text-red-500">{field.state.meta.errors.join(',')}</em>
//             ) : null}
//             {field.state.meta.isValidating ? 'Validating...' : null}
//         </>
//     )
// }

// const defaultCampaignPlan = (): CampaignPlan => {
//     // fetch obj_id using api call
//     return {
//         obj_id: {
//             prefix: 'CampPlan',
//             numeric: 0,
//         },
//         title: '',
//         version: '',
//         setting: '',
//         summary: '',
//         storypoints: [],
//         characters: [],
//         locations: [],
//         items: [],
//         rules: [],
//         objectives: [],
//     }
// }

// const CampaignPlanForm = () => {
//     const form = useAppForm({
//         defaultValues: defaultCampaignPlan(),
//         onSubmit: (values) => {
//             console.log('Submitted Campaign Plan:', values)
//         },
//     })
//     return (
//         <div>
//             <h1>Campaign Plan</h1>
//             <form onSubmit={(e) => {
//                 e.preventDefault()
//                 e.stopPropagation()
//                 form.handleSubmit()
//             }}
//             >
//                 {/* TITLE */}
//                 <div>
//                 <form.AppField
//                     name="title"
//                     // validators={{
//                     //     onChange: ({ value }) => {
//                     //         const errors: string[] = []
//                     //         if (value.length < 1) {
//                     //             errors.push('Title must be at least 1 character long')
//                     //         }
//                     //         return errors
//                     //     },
//                     // }}
//                     children={(field) => <field.TextField label="" />//{
                        
//                         // return (
//                         //     <div className="flex">
//                         //         <label htmlFor={field.name}>Title:</label>
//                         //         <input
//                         //             id={field.name}
//                         //             name={field.name}
//                         //             value={field.state.value}
//                         //             onBlur={field.handleBlur}
//                         //             onChange={(e) => field.handleChange(e.target.value)}
//                         //         />
//                         //         <FieldInfo field={field} />
//                         //     </div>
//                         // )
//                     // }
//                     }
//                 />
//                 {/* VERSION */}
//                 <form.Field
//                     name="version"
//                     validators={{
//                         onChange: ({ value }) => {
//                             // const errors: string[] = []
//                             // if (value.length < 1) {
//                             //     errors.push('Version must be at least 1 character long')
//                             // }
//                             // return errors
//                         },
//                     }}
//                     children={(field) => {
//                         return (
//                             <div className="flex justify-center">
//                                 <label htmlFor={field.name}>Version:</label>
//                                 <textarea
//                                     id={field.name}
//                                     name={field.name}
//                                     value={field.state.value}
//                                     onBlur={field.handleBlur}
//                                     onChange={(e) => field.handleChange(e.target.value)}
//                                 />
//                                 <FieldInfo field={field} />
//                             </div>
//                         )
//                     }}
//                 />
//                 {/* SETTING */}
//                 <form.Field
//                     name="setting"
//                     validators={{
//                         onChange: ({ value }) => {
//                             // const errors: string[] = []
//                             // if (value.length < 1) {
//                             //     errors.push('Setting must be at least 1 character long')
//                             // }
//                             // return errors
//                         },
//                     }}
//                     children={(field) => {
//                         return (
//                             <div className="flex justify-center">
//                                 <label htmlFor={field.name}>Setting:</label>
//                                 <textarea
//                                     id={field.name}
//                                     name={field.name}
//                                     value={field.state.value}
//                                     onBlur={field.handleBlur}
//                                     onChange={(e) => field.handleChange(e.target.value)}
//                                 />
//                                 <FieldInfo field={field} />
//                             </div>
//                         )
//                     }}
//                 />
//                 {/* SUMMARY */}
//                 <form.Field
//                     name="summary"
//                     validators={{
//                         onChange: ({ value }) => {
//                             // const errors: string[] = []
//                             // if (value.length < 1) {
//                             //     errors.push('Summary must be at least 1 character long')
//                             // }
//                             // return errors
//                         },
//                     }}
//                     children={(field) => {
//                         return (
//                             <div className="flex justify-center">
//                                 <label htmlFor={field.name}>Summary:</label>
//                                 <textarea
//                                     id={field.name}
//                                     name={field.name}
//                                     value={field.state.value}
//                                     onBlur={field.handleBlur}
//                                     onChange={(e) => field.handleChange(e.target.value)}
//                                 />
//                                 <FieldInfo field={field} />
//                             </div>
//                         )
//                     }}
//                 />
//                 {/* Handle complex fields later */}
//                 </div>
                
//             </form>
//         </div>
//     )
// }

// export { CampaignPlanForm }
