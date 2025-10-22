import React from 'react';

export interface ObjectFormField {
    name: string;
    label: string;
    type: 'text' | 'number' | 'checkbox' | 'select';
    options?: string[]; // For 'select' type
}

export interface ObjectFormProps {
    title: string;
    description?: string;
    onSubmit: (data: { [key: string]: any }) => void;
    fields: ObjectFormField[];
}


export const ObjectForm: React.FC<ObjectFormProps> = ({ title, description, onSubmit, fields }) => {
    const [formData, setFormData] = React.useState<{ [key: string]: any }>({});
    const handleChange = (name: string, value: any) => {
        setFormData(prev => ({ ...prev, [name]: value }));
    };
    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onSubmit(formData);
    };
    console.log('Rendering ObjectForm with fields:', fields);
    return (
        <Form onSubmit={handleSubmit} className="ObjectForm">
            <h2>{title}</h2>
            {description && <p>{description}</p>}
            {fields.map(field => (
                <Form.Group key={field.name} className="mb-3" controlId={field.name}>
                    <Form.Label>{field.label}</Form.Label>
                    {field.type === 'text' && (
                        <Form.Control
                            type="text"
                            value={formData[field.name] || ''}
                            onChange={e => handleChange(field.name, e.target.value)}
                        />
                    )}
                    {field.type === 'number' && (
                        <Form.Control
                            type="number"
                            value={formData[field.name] || ''}
                            onChange={e => handleChange(field.name, parseFloat(e.target.value))}
                        />
                    )}
                    {field.type === 'checkbox' && (
                        <Form.Check
                            type="checkbox"
                            checked={formData[field.name] || false}
                            onChange={e => handleChange(field.name, e.target.checked)}
                        />
                    )}
                    {field.type === 'select' && field.options && (
                        <Form.Select
                            value={formData[field.name] || ''}
                            onChange={e => handleChange(field.name, e.target.value)}
                        >
                            {field.options.map(option => (
                                <option key={option} value={option}>{option}</option>
                            ))}
                        </Form.Select>
                    )}
                </Form.Group>
            ))}
            <Button variant="primary" type="submit">
                Submit
            </Button>
        </Form>
    );
}
