import { ReactNode } from 'react';
import { redirect } from 'next/navigation';

export default async function ProtectedRoute({ children }: { children: ReactNode }) {
  const token = globalThis.localStorage?.getItem?.('auth_token');
  
  if (!token) {
    redirect('/auth/signin');
  }
  
  return <>{children}</>;
}
