'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function SignUp() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [orgName, setOrgName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleSignUp(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Create org via API
      const orgId = 'org_' + Math.random().toString(36).substr(2, 9);
      const userId = email.split('@')[0];
      
      const payload = {
        sub: userId,
        org_id: orgId,
        role: 'owner',
        email,
      };

      const token = JSON.stringify(payload);
      localStorage.setItem('auth_token', token);
      localStorage.setItem('current_org_id', orgId);
      
      router.push('/dashboard');
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Sign up failed';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="bg-slate-800 rounded-lg shadow-xl p-8 border border-slate-700">
          <h1 className="text-3xl font-bold text-white mb-2">ForgeOS</h1>
          <p className="text-slate-400 mb-8">Create your account</p>

          <form onSubmit={handleSignUp} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Organization Name
              </label>
              <input
                type="text"
                value={orgName}
                onChange={(e) => setOrgName(e.target.value)}
                placeholder="Your Company"
                className="w-full px-4 py-2 rounded bg-slate-700 border border-slate-600 text-white placeholder-slate-500 focus:outline-none focus:border-purple-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full px-4 py-2 rounded bg-slate-700 border border-slate-600 text-white placeholder-slate-500 focus:outline-none focus:border-purple-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-4 py-2 rounded bg-slate-700 border border-slate-600 text-white placeholder-slate-500 focus:outline-none focus:border-purple-500"
                required
              />
            </div>

            {error && (
              <div className="p-3 bg-red-500/10 border border-red-500/50 rounded text-red-400 text-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-slate-600 text-white font-medium rounded transition"
            >
              {loading ? 'Creating account...' : 'Sign Up'}
            </button>
          </form>

          <p className="text-center text-slate-400 text-sm mt-6">
            Already have an account?{' '}
            <a href="/auth/signin" className="text-purple-400 hover:text-purple-300">
              Sign in
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
