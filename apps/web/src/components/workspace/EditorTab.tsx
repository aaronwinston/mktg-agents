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
    <div className="h-full flex items-center justify-center">
      <div className="text-center space-y-3">
        <p className="text-sm text-gray-500">✏️ Editor coming soon</p>
        <p className="text-xs text-gray-400">For: {deliverable.title}</p>
      </div>
    </div>
  );
}
