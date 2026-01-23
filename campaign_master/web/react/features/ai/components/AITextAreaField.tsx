/**
 * AITextAreaField - Multi-line textarea with AI completion support.
 *
 * Press Ctrl+Space to trigger AI completion.
 * The completion popup appears below the textarea with the suggestion.
 */

import { useState, useCallback, useRef } from 'react';
import { Field, Label, Description, Textarea } from '@headlessui/react';
import { CompletionPopup } from './CompletionPopup';
import { useAI, useAIAvailable } from '../AIContext';
import { useCompletion } from '../hooks';
import { useFieldContext } from '../../shared/components/ctx';
import type { CompletionContext } from '../types';

interface AITextAreaFieldProps {
  label: string;
  description?: string;
  /** The name of this field (used in AI context) */
  fieldName?: string;
  /** The entity type being edited (used in AI context) */
  entityType?: string;
  /** Function to get additional entity context data */
  getEntityData?: () => Record<string, unknown>;
}

export function AITextAreaField({
  label,
  description,
  fieldName,
  entityType,
  getEntityData,
}: AITextAreaFieldProps) {
  const field = useFieldContext<string>();
  const { defaultAgent } = useAI();
  const aiAvailable = useAIAvailable();
  const completion = useCompletion();

  const [showPopup, setShowPopup] = useState(false);
  const [suggestion, setSuggestion] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const labelEl = label ? (
    <Label className="p-2 font-bold">{label}:</Label>
  ) : null;
  const descriptionEl = description ? (
    <Description className="p-2 text-sm text-gray-500">
      {description}
    </Description>
  ) : null;

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      // Ctrl+Space triggers AI completion
      if (e.ctrlKey && e.code === 'Space' && aiAvailable && defaultAgent) {
        e.preventDefault();

        const context: CompletionContext = {
          field_name: fieldName || label,
          entity_type: entityType || 'unknown',
          current_text: field.state.value,
          entity_data: getEntityData?.(),
        };

        // Show loading popup
        setShowPopup(true);
        setSuggestion('');

        completion.mutate(
          {
            prompt: field.state.value,
            context,
            max_tokens: defaultAgent.max_tokens,
            temperature: defaultAgent.temperature,
            system_prompt: defaultAgent.system_prompt,
            provider_type: defaultAgent.provider_type,
            api_key: defaultAgent.api_key,
            base_url: defaultAgent.base_url,
            model: defaultAgent.model,
          },
          {
            onSuccess: (response) => {
              if (response.finish_reason !== 'error' && response.text) {
                setSuggestion(response.text);
              } else {
                setShowPopup(false);
                if (response.error_message) {
                  console.error('AI completion error:', response.error_message);
                }
              }
            },
            onError: (error) => {
              setShowPopup(false);
              console.error('AI completion error:', error);
            },
          },
        );
      }
    },
    [
      aiAvailable,
      defaultAgent,
      field.state.value,
      fieldName,
      entityType,
      getEntityData,
      label,
      completion,
    ],
  );

  const handleAccept = useCallback(() => {
    // Append the suggestion to the current text if it's not already there
    const currentText = field.state.value;
    if (suggestion && !currentText.includes(suggestion)) {
      // Add space/newline if needed
      let separator = '';
      if (currentText) {
        separator = currentText.endsWith('\n')
          ? ''
          : currentText.endsWith(' ')
            ? ''
            : ' ';
      }
      field.handleChange(currentText + separator + suggestion);
    }
    setShowPopup(false);
    setSuggestion('');
    textareaRef.current?.focus();
  }, [field, suggestion]);

  const handleReject = useCallback(() => {
    setShowPopup(false);
    setSuggestion('');
    textareaRef.current?.focus();
  }, []);

  return (
    <Field className="relative">
      {labelEl}
      {descriptionEl}
      <div className="relative">
        <Textarea
          ref={textareaRef}
          value={field.state.value}
          className="min-h-full min-w-full"
          onChange={(e) => field.handleChange(e.target.value)}
          onKeyDown={handleKeyDown}
          title={aiAvailable ? 'Press Ctrl+Space for AI completion' : undefined}
        />
        <CompletionPopup
          suggestion={suggestion}
          isVisible={showPopup}
          isLoading={completion.isPending}
          onAccept={handleAccept}
          onReject={handleReject}
        />
      </div>
    </Field>
  );
}
