'use client';

interface EditorTabProps {
  deliverable: {
    id: number;
    title: string;
    body_md?: string;
  };
}

export default function EditorTab({ deliverable }: EditorTabProps) {
  return (
    <div className="h-full flex flex-col items-center justify-center text-center">
      <div className="space-y-2">
        <p className="text-sm font-medium text-gray-700">✏️ Editor coming soon</p>
        <p className="text-xs text-gray-500">Markdown editor for: {deliverable.title}</p>
      </div>
    </div>
  );
}
