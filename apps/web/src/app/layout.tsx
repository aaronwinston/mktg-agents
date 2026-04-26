import type { Metadata } from 'next';
import './globals.css';
import Sidebar from '@/components/Sidebar';
import { AgentTracker } from '@/components/layout/AgentTracker';

export const metadata: Metadata = {
  title: 'ForgeOS',
  description: 'AI-native editorial and marketing operating system',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="flex h-screen bg-bg-primary overflow-hidden">
          <Sidebar />
          <main className="flex-1 overflow-auto">{children}</main>
          <AgentTracker />
        </div>
      </body>
    </html>
  );
}
