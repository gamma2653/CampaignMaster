import { createFormHookContexts, createFormHook } from '@tanstack/react-form';
import {
  TextField,
  SubscribeButton,
  NumberField,
  IDDisplayField,
  PointSelectField,
  NameValueCombo,
  TextAreaField,
} from './fields';
import { AITextField, AITextAreaField } from '../../ai/components';

export const { fieldContext, useFieldContext, formContext, useFormContext } =
  createFormHookContexts();

export const { useAppForm, withForm, withFieldGroup } = createFormHook({
  fieldComponents: {
    /**
     * A text input field component with label and error display.
     * @param param0  Object containing the label for the field.
     * @returns A JSX element representing the text field.
     */
    TextField,
    /**
     * A field component for editing ID objects with prefix and numeric parts.
     * @param param0  Object containing the label for the field.
     * @returns A JSX element representing the ID field.
     */
    TextAreaField,
    NumberField,
    IDDisplayField,
    PointSelectField,
    NameValueCombo,
    /**
     * AI-enhanced text input with Ctrl+Space completion.
     */
    AITextField,
    /**
     * AI-enhanced textarea with Ctrl+Space completion.
     */
    AITextAreaField,
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
});

export type useAppForm_RT = ReturnType<typeof useAppForm>;
