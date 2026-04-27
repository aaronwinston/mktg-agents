'use client';
import { useMemo, useState } from 'react';
import type { CalendarEvent } from '@/lib/api';
import { EventPill } from './EventPill';

interface Props {
  /** Any date within the target week */
  weekStart: Date;
  events: CalendarEvent[];
  onDateClick: (date: Date) => void;
  onEventDrop: (eventId: number, newDate: Date) => void;
  /** Optimistically-moved event ids mapped to their pending new ISO start string */
  pendingMoves: Record<number, string>;
}

const MAX_VISIBLE_PER_DAY = 5;

function addDays(d: Date, n: number) {
  const r = new Date(d);
  r.setDate(r.getDate() + n);
  return r;
}

function isToday(d: Date) {
  return d.toDateString() === new Date().toDateString();
}

function toDateKey(d: Date) {
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
}

/**
 * Returns true if `day` falls within [eventStart, eventEnd] inclusive (date-only comparison).
 * When end_at is absent or same as start, only the start date matches.
 */
function eventSpansDay(ev: CalendarEvent, day: Date, pendingMoves: Record<number, string>): boolean {
  const dayStr = toDateKey(day);
  const startStr = pendingMoves[ev.id]
    ? pendingMoves[ev.id].slice(0, 10)
    : ev.start_at.slice(0, 10);
  // Compute end: apply same day-offset as the pending move when present
  let endStr = startStr;
  if (ev.end_at) {
    if (pendingMoves[ev.id] && ev.end_at) {
      const originalDuration =
        new Date(ev.end_at).getTime() - new Date(ev.start_at).getTime();
      const movedEnd = new Date(new Date(pendingMoves[ev.id]).getTime() + originalDuration);
      endStr = movedEnd.toISOString().slice(0, 10);
    } else {
      endStr = ev.end_at.slice(0, 10);
    }
  }
  return startStr <= dayStr && dayStr <= endStr;
}

/**
 * Week strip view — 7 columns, one day each.
 *
 * Multi-day events: rendered in every column their date range spans.
 * Drag-to-reschedule: HTML5 DnD, same pattern as MonthView.
 *   Drop sets the new start date while preserving time-of-day and duration.
 *   Optimistic update is applied immediately via pendingMoves.
 * Overflow: days with > MAX_VISIBLE_PER_DAY events show a '+N more' badge.
 */
export function WeekView({ weekStart, events, onDateClick, onEventDrop, pendingMoves }: Props) {
  const [draggingId, setDraggingId] = useState<number | null>(null);
  const [dragOverKey, setDragOverKey] = useState<string | null>(null);

  // Align weekStart to Sunday
  const sunday = useMemo(() => {
    const d = new Date(weekStart);
    d.setDate(d.getDate() - d.getDay());
    return d;
  }, [weekStart]);

  const days = useMemo(() => Array.from({ length: 7 }, (_, i) => addDays(sunday, i)), [sunday]);

  // Events for each day, accounting for multi-day spans and pending moves
  const eventsByDay = useMemo(() => {
    return days.map(day =>
      events.filter(ev => eventSpansDay(ev, day, pendingMoves))
    );
  }, [days, events, pendingMoves]);

  // ── DnD handlers ────────────────────────────────────────────────────────

  const handleDragStart = (e: React.DragEvent, ev: CalendarEvent) => {
    e.dataTransfer.setData('eventId', String(ev.id));
    e.dataTransfer.effectAllowed = 'move';
    setDraggingId(ev.id);
  };

  const handleDragOver = (e: React.DragEvent, key: string) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    setDragOverKey(key);
  };

  const handleDrop = (e: React.DragEvent, date: Date) => {
    e.preventDefault();
    const idStr = e.dataTransfer.getData('eventId');
    if (!idStr) return;
    setDraggingId(null);
    setDragOverKey(null);
    onEventDrop(parseInt(idStr, 10), date);
  };

  // ── Render ───────────────────────────────────────────────────────────────

  const MONTH_NAMES = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  const DOW = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];

  return (
    <div className="flex flex-col h-full">
      {/* Header row */}
      <div className="grid grid-cols-7 border-b border-border shrink-0">
        {days.map((d, i) => {
          const today = isToday(d);
          return (
            <div key={i} className="py-3 text-center border-r border-border last:border-r-0">
              <p className="text-xs text-fg-tertiary font-medium uppercase">{DOW[i]}</p>
              <p className={`
                text-xl font-bold mt-0.5 mx-auto w-9 h-9 flex items-center justify-center rounded-full
                ${today ? 'bg-accent text-white' : 'text-fg-primary'}
              `}>
                {d.getDate()}
              </p>
              <p className="text-[10px] text-fg-tertiary mt-0.5">{MONTH_NAMES[d.getMonth()]}</p>
            </div>
          );
        })}
      </div>

      {/* Day columns */}
      <div className="grid grid-cols-7 flex-1 overflow-y-auto">
        {days.map((d, i) => {
          const key = toDateKey(d);
          const isOver = dragOverKey === key;
          const dayEvents = eventsByDay[i];
          const visible = dayEvents.slice(0, MAX_VISIBLE_PER_DAY);
          const overflow = dayEvents.length - visible.length;

          return (
            <div
              key={i}
              onClick={() => onDateClick(d)}
              onDragOver={(e) => handleDragOver(e, key)}
              onDragLeave={() => setDragOverKey(null)}
              onDrop={(e) => handleDrop(e, d)}
              className={`
                border-r border-border last:border-r-0 p-2 flex flex-col gap-1 cursor-pointer
                transition-colors duration-100 min-h-[200px]
                ${isOver ? 'bg-accent/10 outline outline-1 outline-accent' : 'hover:bg-bg-secondary'}
              `}
            >
              {visible.map(ev => (
                <EventPill
                  key={ev.id}
                  event={ev}
                  dragging={draggingId === ev.id}
                  onDragStart={handleDragStart}
                />
              ))}
              {overflow > 0 && (
                <span className="text-[10px] text-fg-tertiary pl-1 mt-0.5">
                  +{overflow} more
                </span>
              )}
              {dayEvents.length === 0 && (
                <span className="text-[11px] text-fg-tertiary italic mt-1 px-1">No events</span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
