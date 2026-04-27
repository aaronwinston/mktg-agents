'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import type { CalendarEvent } from '@/lib/api';
import { getUpcomingEvents } from '@/lib/api';
import { CONTENT_TYPE_CONFIG } from '@/components/calendar/contentTypeConfig';

const INITIAL_LIMIT = 5;
const FETCH_LIMIT = 20; // fetch ahead so expansion is instant (no second request)

function formatEventDate(iso: string, allDay: boolean) {
  const d = new Date(iso);
  const dateStr = d.toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' });
  if (allDay) return dateStr;
  const timeStr = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  return `${dateStr} · ${timeStr}`;
}

/**
 * Dashboard "Up next" widget — next 7 days, sorted by start_at ASC.
 *
 * Fetches up to FETCH_LIMIT (20) events up-front; displays INITIAL_LIMIT (5)
 * with a "See N more" expand button for the rest. No second network call needed.
 *
 * Click → /workspace/[deliverable_id] when linked, or /calendar when not.
 */
export function UpNext() {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    getUpcomingEvents(FETCH_LIMIT)
      .then(setEvents)
      .finally(() => setLoading(false));
  }, []);

  const visible = expanded ? events : events.slice(0, INITIAL_LIMIT);
  const hiddenCount = events.length - INITIAL_LIMIT;

  return (
    <section>
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-base font-semibold text-fg-primary">Up next</h2>
        <Link href="/calendar" className="text-xs text-fg-tertiary hover:text-accent transition-colors">
          View calendar →
        </Link>
      </div>

      {/* Loading skeleton */}
      {loading && (
        <div className="space-y-2">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-12 border border-border rounded-card bg-bg-secondary animate-shimmer" />
          ))}
        </div>
      )}

      {/* Empty state */}
      {!loading && events.length === 0 && (
        <div className="flex flex-col items-center justify-center py-8 text-fg-tertiary border border-border rounded-card bg-bg-secondary">
          <span className="text-2xl mb-2">📅</span>
          <p className="text-sm">No events scheduled this week</p>
          <Link href="/calendar" className="text-xs text-accent hover:underline mt-2">
            Open calendar
          </Link>
        </div>
      )}

      {/* Event list */}
      {!loading && events.length > 0 && (
        <div className="space-y-2">
          {visible.map(ev => {
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

          {/* Expand / collapse toggle */}
          {hiddenCount > 0 && !expanded && (
            <button
              onClick={() => setExpanded(true)}
              className="w-full py-2 text-xs text-fg-tertiary hover:text-accent transition-colors border border-dashed border-border rounded-card"
            >
              See {hiddenCount} more event{hiddenCount !== 1 ? 's' : ''} →
            </button>
          )}
          {expanded && events.length > INITIAL_LIMIT && (
            <button
              onClick={() => setExpanded(false)}
              className="w-full py-2 text-xs text-fg-tertiary hover:text-accent transition-colors"
            >
              Show less ↑
            </button>
          )}
        </div>
      )}
    </section>
  );
}
