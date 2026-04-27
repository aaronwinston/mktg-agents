'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import type { CalendarEvent } from '@/lib/api';
import { getUpcomingEvents } from '@/lib/api';
import { CONTENT_TYPE_CONFIG } from '@/components/calendar/contentTypeConfig';

function formatEventDate(iso: string, allDay: boolean) {
  const d = new Date(iso);
  const dateStr = d.toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' });
  if (allDay) return dateStr;
  const timeStr = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  return `${dateStr} · ${timeStr}`;
}

/**
 * Dashboard "Up next" widget — next 7 days, max 5 events, sorted by start_at ASC.
 *
 * Click on an event navigates to /workspace/[deliverable_id] when linked,
 * or /calendar when no deliverable is attached.
 */
export function UpNext() {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getUpcomingEvents(5)
      .then(setEvents)
      .finally(() => setLoading(false));
  }, []);

  return (
    <section>
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-base font-semibold text-fg-primary">Up next</h2>
        <Link href="/calendar" className="text-xs text-fg-tertiary hover:text-accent transition-colors">
          View calendar →
        </Link>
      </div>

      {loading && (
        <div className="space-y-2">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-12 border border-border rounded-card bg-bg-secondary animate-shimmer" />
          ))}
        </div>
      )}

      {!loading && events.length === 0 && (
        <div className="flex flex-col items-center justify-center py-8 text-fg-tertiary border border-border rounded-card bg-bg-secondary">
          <span className="text-2xl mb-2">📅</span>
          <p className="text-sm">No events scheduled this week</p>
          <Link href="/calendar" className="text-xs text-accent hover:underline mt-2">
            Open calendar
          </Link>
        </div>
      )}

      {!loading && events.length > 0 && (
        <div className="space-y-2">
          {events.map(ev => {
            const config = CONTENT_TYPE_CONFIG[ev.content_type] ?? CONTENT_TYPE_CONFIG['blog'];
            const href = ev.deliverable_id ? `/workspace/${ev.deliverable_id}` : '/calendar';

            return (
              <Link
                key={ev.id}
                href={href}
                className="flex items-center gap-3 p-3 border border-border rounded-card bg-bg-secondary hover:border-accent/30 hover:bg-bg-secondary/80 transition-colors group"
              >
                {/* Colour dot */}
                <div
                  className="w-2 h-2 rounded-full shrink-0"
                  style={{ backgroundColor: config.color }}
                />

                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-fg-primary truncate group-hover:text-accent transition-colors">
                    {ev.title}
                  </p>
                  <p className="text-xs text-fg-tertiary mt-0.5">
                    {formatEventDate(ev.start_at, ev.all_day)}
                  </p>
                </div>

                <span className={`text-[10px] px-1.5 py-0.5 rounded border font-medium shrink-0 ${config.pillClass}`}>
                  {config.label}
                </span>
              </Link>
            );
          })}
        </div>
      )}
    </section>
  );
}
