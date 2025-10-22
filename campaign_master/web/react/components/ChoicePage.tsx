// import { TextField, NumberField, SubmitButton } from './TextField'
import { createFormHookContexts, createFormHook } from '@tanstack/react-form'
import { z } from 'zod'

export const { fieldContext, formContext, useFieldContext } =
  createFormHookContexts()


const { useAppForm } = createFormHook({
  fieldContext,
  formContext,
  // We'll learn more about these options later
  fieldComponents: {
    TextField: ({ field, label }: { field: any; label: string }) => (
      <label>
        <span>{label}</span>
        <input {...field} />
      </label>
    ),
    NumberField: ({ field, label }: { field: any; label: string }) => (
      <label>
        <span>{label}</span>
        <input type="number" {...field} />
      </label>
    ),
  },
  formComponents: { SubmitButton: () => <button type="submit">Submit</button> },
})


export interface ChoicePageProps {
  title: string;
  description?: string;
  choices: { label: string; value: string }[];
  onChoose: (value: string) => void;
}

export const App = () => {
  const form = useAppForm({
    // Supports all useForm options
    defaultValues: {
      title: ' ',
      description: ' ',
      choices: [{ label: ' ', value: ' ' }],
    },
    validators: {
      onChange: z.object({
        title: z.string().min(1, 'Title is required'),
        description: z.string().min(1, 'Description is required'),
        choices: z.array(z.object({
          label: z.string().min(1, 'Label is required'),
          value: z.string().min(1, 'Value is required'),
        })).min(1, 'At least one choice is required'),
      })
    }
  })

  return <form.Field />
}

export const ChoicePage: React.FC<ChoicePageProps> = ({ title, description, choices, onChoose }) => {
  return (
    <div className="ChoicePage">
      <h2>{title}</h2>
      {description && <p>{description}</p>}
      <div className="choices">
        {choices.map(choice => (
          <button key={choice.value} onClick={() => onChoose(choice.value)}>
            {choice.label}
          </button>
        ))}
      </div>
    </div>
  );
}