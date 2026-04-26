'use client';

interface Props {
  value: string;
  onChange: (v: string) => void;
}

export default function MarkdownEditor({ value, onChange }: Props) {
  return (
    <textarea
      className="flex-1 w-full h-full min-h-[500px] font-mono text-sm p-4 border rounded bg-background resize-none focus:outline-none focus:ring-1 focus:ring-ring"
      value={value}
      onChange={e => onChange(e.target.value)}
      spellCheck={false}
    />
  );
}
