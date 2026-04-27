'use client';

interface ChatTabProps {
  deliverable: {
    id: number;
    title: string;
  };
}

export default function ChatTab({ deliverable }: ChatTabProps) {
  return (
    <div className="h-full flex items-center justify-center">
      <div className="text-center space-y-3">
        <p className="text-sm text-gray-500">💬 Chat interface coming soon</p>
        <p className="text-xs text-gray-400">For: {deliverable.title}</p>
      </div>
    </div>
  );
}
