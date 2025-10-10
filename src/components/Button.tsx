import * as React from 'react';

// Example of button component
// In reality just use React-Bootstrap or similar

type ButtonProps = {
    title?: string;
    description?: string;
    onClick?: () => void;

}

export const Button = (props: ButtonProps) => {
    return (
        <button onClick={props.onClick}>
            <h2>{props.title}</h2>
            <p>{props.description}</p>
        </button>
    );
}