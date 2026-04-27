'use client';
import { useEffect, useState } from 'react';
import { getSessions } from '@/lib/api';

export function HeroSection() {
  const [sessionCount, setSessionCount] = useState<number | null>(null);
  
  useEffect(() => {
    getSessions().then(sessions => setSessionCount(sessions.length)).catch(() => setSessionCount(0));
  }, []);
  
  return (
    <div>
      <h1 className="font-display text-3xl font-semibold text-fg-primary leading-tight">
        Hi, Aaron. What markets should we move today?
      </h1>
      <p className="text-fg-tertiary text-sm mt-2">
        {sessionCount === null ? (
          <span className="inline-block h-4 w-24 bg-bg-tertiary rounded animate-pulse" />
        ) : (
          <span>{sessionCount} session{sessionCount !== 1 ? 's' : ''} in the system</span>
        )}
      </p>
    </div>
  );
}
