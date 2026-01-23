/**
 * CompletionPopup - Floating popup showing AI suggestion.
 *
 * Appears below the input with the AI-generated suggestion.
 * User can accept with Tab/Enter or reject with Escape.
 */

import { useEffect, useRef, useCallback } from 'react';

interface CompletionPopupProps {
  /** The AI-generated suggestion text */
  suggestion: string;
  /** Whether the popup is visible */
  isVisible: boolean;
  /** Whether completion is loading */
  isLoading: boolean;
  /** Callback when user accepts the suggestion */
  onAccept: () => void;
  /** Callback when user rejects the suggestion */
  onReject: () => void;
  /** Position relative to parent (optional) */
  position?: { top: number; left: number };
}

export function CompletionPopup({
  suggestion,
  isVisible,
  isLoading,
  onAccept,
  onReject,
  position,
}: CompletionPopupProps) {
  const popupRef = useRef<HTMLDivElement>(null);

  // Handle keyboard events
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (!isVisible) return;

      if (e.key === 'Tab' || e.key === 'Enter') {
        e.preventDefault();
        e.stopPropagation();
        onAccept();
      } else if (e.key === 'Escape') {
        e.preventDefault();
        e.stopPropagation();
        onReject();
      }
    },
    [isVisible, onAccept, onReject],
  );

  // Add/remove keyboard listener
  useEffect(() => {
    if (isVisible) {
      document.addEventListener('keydown', handleKeyDown, true);
      return () => {
        document.removeEventListener('keydown', handleKeyDown, true);
      };
    }
  }, [isVisible, handleKeyDown]);

  // Handle click outside
  useEffect(() => {
    if (!isVisible) return;

    const handleClickOutside = (e: MouseEvent) => {
      if (popupRef.current && !popupRef.current.contains(e.target as Node)) {
        onReject();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isVisible, onReject]);

  if (!isVisible) return null;

  const style: React.CSSProperties = position
    ? {
        top: position.top,
        left: position.left,
      }
    : {};

  return (
    <div
      ref={popupRef}
      className="absolute z-50 mt-1 p-3 bg-gray-800 border border-gray-600 rounded-lg shadow-xl max-w-md"
      style={style}
    >
      {isLoading ? (
        <div className="flex items-center gap-2 text-gray-400">
          <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
              fill="none"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          <span>Generating completion...</span>
        </div>
      ) : (
        <>
          <div className="text-green-400 font-mono text-sm whitespace-pre-wrap mb-2">
            {suggestion}
          </div>
          <div className="flex items-center gap-4 text-xs text-gray-500 border-t border-gray-700 pt-2">
            <span className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 bg-gray-700 rounded text-gray-300">
                Tab
              </kbd>
              <span>or</span>
              <kbd className="px-1.5 py-0.5 bg-gray-700 rounded text-gray-300">
                Enter
              </kbd>
              <span>to accept</span>
            </span>
            <span className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 bg-gray-700 rounded text-gray-300">
                Esc
              </kbd>
              <span>to dismiss</span>
            </span>
          </div>
        </>
      )}
    </div>
  );
}
