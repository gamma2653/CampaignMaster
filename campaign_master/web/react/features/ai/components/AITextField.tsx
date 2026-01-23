/**
 * AITextField - Single-line text input with AI completion support.
 *
 * Press Ctrl+Space to trigger AI completion.
 * The completion popup appears below the input with the suggestion.
 */

import { useState, useCallback, useRef } from 'react';
import { Field, Label, Input } from '@headlessui/react';
import { CompletionPopup } from './CompletionPopup';
import { useAI, useAIAvailable } from '../AIContext';
import { useCompletion } from '../hooks';
import { useFieldContext } from '../../shared/components/ctx';
import type { CompletionContext } from '../types';

interface AITextFieldProps {
  label: string;
  /** The name of this field (used in AI context) */
  fieldName?: string;
  /** The entity type being edited (used in AI context) */
  entityType?: string;
  /** Function to get additional entity context data */
  getEntityData?: () => Record<string, unknown>;
}

export function AITextField({
  label,
  fieldName,
  entityType,
  getEntityData,
}: AITextFieldProps) {
  const field = useFieldContext<string>();
  const { defaultAgent } = useAI();
  const aiAvailable = useAIAvailable();
  const completion = useCompletion();

  const [showPopup, setShowPopup] = useState(false);
  const [suggestion, setSuggestion] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  const textId = `text-${label.replace(/\s+/g, '-').toLowerCase()}`;
  const labelEl = label ? (
    <Label className="p-2 font-bold">{label}:</Label>
  ) : null;

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLInputElement>) => {
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
      // Add space if needed
      const separator = currentText && !currentText.endsWith(' ') ? ' ' : '';
      field.handleChange(currentText + separator + suggestion);
    }
    setShowPopup(false);
    setSuggestion('');
    inputRef.current?.focus();
  }, [field, suggestion]);

  const handleReject = useCallback(() => {
    setShowPopup(false);
    setSuggestion('');
    inputRef.current?.focus();
  }, []);

  return (
    <Field className="flex flex-row relative">
      {labelEl}
      <div className="flex-1 relative">
        <Input
          ref={inputRef}
          id={textId}
          className="w-full"
          value={field.state.value}
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
