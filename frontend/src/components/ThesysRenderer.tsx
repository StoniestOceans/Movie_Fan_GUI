'use client';

import React from 'react';

// This is a simplified "Canvas" renderer for our mock C1 schema
// In a real Thesys app, you might use <Canvas /> from @crayonai/react-ui
// But here we will manually traverse the JSON structure we defined in the backend.

interface ComponentProps {
    className?: string;
    children?: React.ReactNode;
    [key: string]: any;
}

interface SchemaNode {
    type: string;
    props?: ComponentProps;
    children?: (SchemaNode | string)[];
}

const renderNode = (node: SchemaNode | string, index: number): React.ReactNode => {
    if (typeof node === 'string') {
        return <span key={index}>{node}</span>;
    }

    const { type, props = {}, children = [] } = node;
    const { className, ...restProps } = props;

    // Recursive children rendering
    const renderedChildren = children.map((child, idx) => renderNode(child, idx));

    // Map "types" to Tailwind classes or HTML elements
    switch (type) {
        case 'Card':
            return (
                <div key={index} className={`rounded-xl border shadow-sm p-4 ${className}`} {...restProps}>
                    {renderedChildren}
                </div>
            );
        case 'CardHeader':
            return <div key={index} className={`flex flex-col space-y-1.5 p-6 ${className}`}>{renderedChildren}</div>;
        case 'CardTitle':
            return <h3 key={index} className={`font-semibold leading-none tracking-tight ${className}`}>{renderedChildren}</h3>;
        case 'CardDescription':
            return <p key={index} className={`text-sm text-muted-foreground ${className}`}>{renderedChildren}</p>;
        case 'CardContent':
            return <div key={index} className={`p-6 pt-0 ${className}`}>{renderedChildren}</div>;
        case 'CardFooter':
            return <div key={index} className={`flex items-center p-6 pt-0 ${className}`}>{renderedChildren}</div>;
        case 'img':
            return <img key={index} className={className} {...restProps} />;
        default:
            // Fallback for standard HTML tags like div, p, span
            return React.createElement(type, { key: index, className, ...restProps }, renderedChildren);
    }
};

export default function ThesysRenderer({ schema }: { schema: SchemaNode[] }) {
    if (!schema || !Array.isArray(schema)) return null;
    return (
        <div className="w-full space-y-4">
            {schema.map((node, i) => renderNode(node, i))}
        </div>
    );
}
