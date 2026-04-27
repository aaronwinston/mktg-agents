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
    <div className="h-full flex items-center justify-center">
      <div className="text-center space-y-3">
        <p className="text-sm text-gray-500">📋 Brief editor coming soon</p>
        <p className="text-xs text-gray-400">For: {deliverable.title}</p>
        {brief && <p className="text-xs text-gray-400">Brief ID: {brief.id}</p>}
      </div>
    </div>
  );
}
