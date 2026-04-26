'use client';
import { useEffect, useState } from 'react';

export default function DashboardPage() {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [feed, setFeed] = useState<any[]>([]);

  useEffect(() => {
    fetch('http://localhost:8000/api/intelligence/feed')
      .then(r => r.json())
      .then(setFeed)
      .catch(console.error);
  }, []);

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="border rounded-lg p-4">
          <h2 className="text-sm font-medium mb-3">In Flight</h2>
          <p className="text-sm text-gray-500">No active deliverables. Start a project to begin.</p>
        </div>
        <div className="border rounded-lg p-4">
          <h2 className="text-sm font-medium mb-3">Today&apos;s Intelligence</h2>
          <div className="space-y-2">
            {feed.slice(0, 3).map(item => (
              <div key={item.id} className="text-xs">
                <span className="inline-block border rounded px-1 mb-1">{item.source}</span>
                <p className="font-medium line-clamp-2">{item.title}</p>
                <p className="text-gray-500">{item.score_reasoning}</p>
              </div>
            ))}
            {feed.length === 0 && <p className="text-sm text-gray-500">No intelligence yet. Trigger a scrape.</p>}
          </div>
        </div>
        <div className="border rounded-lg p-4">
          <h2 className="text-sm font-medium mb-3">Upcoming</h2>
          <p className="text-sm text-gray-500">Calendar view coming in v2.</p>
        </div>
      </div>
    </div>
  );
}
