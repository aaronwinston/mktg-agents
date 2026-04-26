'use client';
import { QuoteCallout } from '@/components/dashboard/QuoteCallout';
import { HeroSection } from '@/components/dashboard/HeroSection';
import { BriefingBook } from '@/components/dashboard/BriefingBook';
import { ActiveSessions } from '@/components/dashboard/ActiveSessions';
import { NewSessionModal } from '@/components/dashboard/NewSessionModal';
import { Button } from '@/components/ui/Button';
import { useState } from 'react';

export default function DashboardPage() {
  const [showModal, setShowModal] = useState(false);
  
  return (
    <div className="p-6 max-w-6xl mx-auto space-y-8">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 space-y-4">
          <HeroSection />
          <QuoteCallout />
        </div>
        <Button onClick={() => setShowModal(true)}>+ New Session</Button>
      </div>
      
      <ActiveSessions />
      <BriefingBook />
      
      {showModal && (
        <NewSessionModal
          onClose={() => setShowModal(false)}
          onCreated={() => setShowModal(false)}
        />
      )}
    </div>
  );
}
