'use client';

interface BriefTabProps {
  deliverable: {
    id: number;
    title: string;
  };
  brief?: {
    id: number;
    brief_md: string;
  };
}

export default function BriefTab({ deliverable, brief }: BriefTabProps) {
  return (
    <div className="h-full flex flex-col items-center justify-center text-center">
      <div className="space-y-2">
        <p className="text-sm font-medium text-gray-700">📋 Brief editor coming soon</p>
        <p className="text-xs text-gray-500">Brief editor for: {deliverable.title}</p>
        {brief && <p className="text-xs text-gray-400 mt-2">Brief ID: {brief.id}</p>}
      </div>
    </div>
  );
}
