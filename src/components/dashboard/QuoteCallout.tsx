'use client';
import { useEffect, useState } from 'react';

interface Quote {
  text: string;
  author: string;
}

export function QuoteCallout() {
  const [quote, setQuote] = useState<Quote | null>(null);
  
  useEffect(() => {
    fetch('/quotes.json')
      .then(r => r.json())
      .then((quotes: Quote[]) => {
        const now = new Date();
        const start = new Date(now.getFullYear(), 0, 0);
        const diff = now.getTime() - start.getTime();
        const dayOfYear = Math.floor(diff / (1000 * 60 * 60 * 24));
        setQuote(quotes[dayOfYear % quotes.length]);
      })
      .catch(() => {});
  }, []);
  
  if (!quote) return <div className="h-10" />;
  
  return (
    <blockquote className="border-l-2 border-brand-purple pl-4 py-1">
      <p className="text-sm text-fg-secondary italic leading-relaxed">&ldquo;{quote.text}&rdquo;</p>
      <footer className="text-xs text-fg-tertiary mt-1">— {quote.author}</footer>
    </blockquote>
  );
}
