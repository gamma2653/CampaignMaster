import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';

// Mock the context hooks
const mockHandleChange = vi.fn();
const mockFieldState: { value: any } = { value: '' };
const mockFormSubscribe = vi.fn();

vi.mock('../features/shared/components/ctx', () => ({
    useFieldContext: () => ({
        state: mockFieldState,
        handleChange: mockHandleChange,
    }),
    useFormContext: () => ({
        Subscribe: ({ children, selector }: { children: (value: boolean) => React.ReactNode; selector: (state: { isSubmitting: boolean }) => boolean }) => {
            return children(mockFormSubscribe());
        },
    }),
}));

// Import after mocking
import {
    TextField,
    TextAreaField,
    NumberField,
    IDDisplayField,
    NameValueCombo,
    PointSelectField,
    SubscribeButton,
} from '../features/shared/components/fields';
import { createMockPoint } from './test-utils';

describe('TextField', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        mockFieldState.value = 'test value';
    });

    it('should render with label', () => {
        render(<TextField label="Test Label" />);
        expect(screen.getByText('Test Label:')).toBeInTheDocument();
    });

    it('should display current value', () => {
        mockFieldState.value = 'Current Value';
        render(<TextField label="Test" />);
        const input = screen.getByRole('textbox');
        expect(input).toHaveValue('Current Value');
    });

    it('should call handleChange on input change', () => {
        render(<TextField label="Test" />);
        const input = screen.getByRole('textbox');
        fireEvent.change(input, { target: { value: 'new value' } });
        expect(mockHandleChange).toHaveBeenCalledWith('new value');
    });

    it('should render without label when label is empty', () => {
        render(<TextField label="" />);
        expect(screen.queryByRole('heading')).not.toBeInTheDocument();
    });

    it('should generate unique id from label', () => {
        render(<TextField label="My Field Name" />);
        const input = screen.getByRole('textbox');
        expect(input).toHaveAttribute('id', 'text-my-field-name');
    });
});

describe('TextAreaField', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        mockFieldState.value = 'textarea content';
    });

    it('should render with label', () => {
        render(<TextAreaField label="Description" />);
        expect(screen.getByText('Description:')).toBeInTheDocument();
    });

    it('should display current value', () => {
        mockFieldState.value = 'Textarea Value';
        render(<TextAreaField label="Test" />);
        const textarea = screen.getByRole('textbox');
        expect(textarea).toHaveValue('Textarea Value');
    });

    it('should render description when provided', () => {
        render(<TextAreaField label="Test" description="This is a description" />);
        expect(screen.getByText('This is a description')).toBeInTheDocument();
    });

    it('should not render description when not provided', () => {
        render(<TextAreaField label="Test" />);
        expect(screen.queryByText('This is a description')).not.toBeInTheDocument();
    });

    it('should call handleChange on textarea change', () => {
        render(<TextAreaField label="Test" />);
        const textarea = screen.getByRole('textbox');
        fireEvent.change(textarea, { target: { value: 'updated content' } });
        expect(mockHandleChange).toHaveBeenCalledWith('updated content');
    });
});

describe('NumberField', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        (mockFieldState as { value: number }).value = 42;
    });

    it('should render with label', () => {
        render(<NumberField label="Quantity" />);
        expect(screen.getByText('Quantity:')).toBeInTheDocument();
    });

    it('should display current numeric value', () => {
        (mockFieldState as { value: number }).value = 100;
        render(<NumberField label="Test" />);
        const input = screen.getByRole('spinbutton');
        expect(input).toHaveValue(100);
    });

    it('should convert string input to number on change', () => {
        render(<NumberField label="Test" />);
        const input = screen.getByRole('spinbutton');
        fireEvent.change(input, { target: { value: '123' } });
        expect(mockHandleChange).toHaveBeenCalledWith(123);
    });

    it('should render with provided id', () => {
        render(<NumberField label="Test" id="custom-id" />);
        const input = screen.getByRole('spinbutton');
        expect(input).toHaveAttribute('id', 'custom-id');
    });
});

describe('IDDisplayField', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('should display ID in PREFIX-NUMERIC format', () => {
        (mockFieldState as { value: { prefix: string; numeric: number } }).value = { prefix: 'P', numeric: 42 };
        render(<IDDisplayField />);
        expect(screen.getByText('ID:')).toBeInTheDocument();
        expect(screen.getByText(/P-42/)).toBeInTheDocument();
    });

    it('should display CampaignPlan ID format correctly', () => {
        (mockFieldState as { value: { prefix: string; numeric: number } }).value = { prefix: 'CampPlan', numeric: 1 };
        render(<IDDisplayField />);
        expect(screen.getByText(/CampPlan-1/)).toBeInTheDocument();
    });

    it('should handle large numeric IDs', () => {
        (mockFieldState as { value: { prefix: string; numeric: number } }).value = { prefix: 'R', numeric: 999999 };
        render(<IDDisplayField />);
        expect(screen.getByText(/R-999999/)).toBeInTheDocument();
    });
});

describe('NameValueCombo', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        (mockFieldState as { value: { name: string; value: number } }).value = { name: 'Strength', value: 10 };
    });

    it('should render name input with current value', () => {
        render(<NameValueCombo />);
        const inputs = screen.getAllByRole('textbox');
        expect(inputs[0]).toHaveValue('Strength');
    });

    it('should render value input with current value', () => {
        render(<NameValueCombo />);
        const spinbutton = screen.getByRole('spinbutton');
        expect(spinbutton).toHaveValue(10);
    });

    it('should call handleChange with updated name', () => {
        render(<NameValueCombo />);
        const inputs = screen.getAllByRole('textbox');
        fireEvent.change(inputs[0], { target: { value: 'Dexterity' } });
        expect(mockHandleChange).toHaveBeenCalledWith({ name: 'Dexterity', value: 10 });
    });

    it('should call handleChange with updated value', () => {
        render(<NameValueCombo />);
        const spinbutton = screen.getByRole('spinbutton');
        fireEvent.change(spinbutton, { target: { value: '15' } });
        expect(mockHandleChange).toHaveBeenCalledWith({ name: 'Strength', value: 15 });
    });
});

describe('PointSelectField', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        (mockFieldState as { value: { prefix: string; numeric: number } }).value = { prefix: 'P', numeric: 1 };
    });

    it('should render with label', () => {
        render(<PointSelectField label="Start Point" />);
        expect(screen.getByText('Start Point:')).toBeInTheDocument();
    });

    it('should render select element', () => {
        render(<PointSelectField label="Point" />);
        expect(screen.getByRole('combobox')).toBeInTheDocument();
    });

    it('should render options from points array', () => {
        const points = [
            createMockPoint({ obj_id: { prefix: 'P', numeric: 1 }, name: 'Beginning' }),
            createMockPoint({ obj_id: { prefix: 'P', numeric: 2 }, name: 'Middle' }),
            createMockPoint({ obj_id: { prefix: 'P', numeric: 3 }, name: 'End' }),
        ];
        render(<PointSelectField label="Point" points={points} />);

        expect(screen.getByText('P-1 (Beginning)')).toBeInTheDocument();
        expect(screen.getByText('P-2 (Middle)')).toBeInTheDocument();
        expect(screen.getByText('P-3 (End)')).toBeInTheDocument();
    });

    it('should call handleChange when selection changes', () => {
        const points = [
            createMockPoint({ obj_id: { prefix: 'P', numeric: 1 }, name: 'Beginning' }),
            createMockPoint({ obj_id: { prefix: 'P', numeric: 2 }, name: 'Middle' }),
        ];
        render(<PointSelectField label="Point" points={points} />);

        const select = screen.getByRole('combobox');
        fireEvent.change(select, { target: { value: '2' } });

        expect(mockHandleChange).toHaveBeenCalledWith({
            prefix: 'P',
            numeric: 2,
        });
    });

    it('should render with provided id', () => {
        render(<PointSelectField label="Point" id="point-select" />);
        const select = screen.getByRole('combobox');
        expect(select).toHaveAttribute('id', 'point-select');
    });

    it('should render empty when no points provided', () => {
        render(<PointSelectField label="Point" />);
        const select = screen.getByRole('combobox');
        expect(select.children.length).toBe(0);
    });
});

describe('SubscribeButton', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        mockFormSubscribe.mockReturnValue(false);
    });

    it('should render button with label', () => {
        render(<SubscribeButton label="Save" />);
        expect(screen.getByRole('button', { name: 'Save' })).toBeInTheDocument();
    });

    it('should be enabled when not submitting', () => {
        mockFormSubscribe.mockReturnValue(false);
        render(<SubscribeButton label="Submit" />);
        expect(screen.getByRole('button')).not.toBeDisabled();
    });

    it('should be disabled when submitting', () => {
        mockFormSubscribe.mockReturnValue(true);
        render(<SubscribeButton label="Submit" />);
        expect(screen.getByRole('button')).toBeDisabled();
    });

    it('should apply provided className', () => {
        render(<SubscribeButton label="Save" className="custom-class" />);
        expect(screen.getByRole('button')).toHaveClass('custom-class');
    });

    it('should have type="submit"', () => {
        render(<SubscribeButton label="Submit" />);
        expect(screen.getByRole('button')).toHaveAttribute('type', 'submit');
    });
});
