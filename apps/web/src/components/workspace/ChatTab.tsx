'use client';

interface ChatTabProps {
  deliverable: {
    id: number;
    title: string;
  };
}

export default function ChatTab({ deliverable }: ChatTabProps) {
  return (
    <div className="h-full flex flex-col items-center justify-center text-center">
      <div className="space-y-2">
        <p className="text-sm font-medium text-gray-700">💬 Chat interface coming soon</p>
        <p className="text-xs text-gray-500">Interactive chat for: {deliverable.title}</p>
      </div>
    </div>
  );
}
