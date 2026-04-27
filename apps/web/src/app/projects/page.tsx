'use client';
import { useEffect, useState } from 'react';
import { getProjects } from '@/lib/api';
import type { Project } from '@/lib/api';
import { SkeletonCard } from '@/components/ui/SkeletonCard';
import Link from 'next/link';

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    getProjects()
      .then(setProjects)
      .finally(() => setLoading(false));
  }, []);
  
  return (
    <div className="p-6 max-w-6xl mx-auto">
      <h1 className="text-2xl font-semibold text-fg-primary mb-6">Projects</h1>
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => <SkeletonCard key={i} />)}
        </div>
      ) : projects.length === 0 ? (
        <p className="text-fg-secondary text-sm">No projects yet.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {projects.map(p => (
            <Link key={p.id} href={`/projects/${p.id}`} className="block border border-border rounded-xl p-4 bg-bg-secondary hover:border-brand-purple/30 transition-all group">
              <h3 className="text-sm font-semibold text-fg-primary group-hover:text-brand-purple transition-colors">{p.name}</h3>
              {p.description && <p className="text-xs text-fg-secondary mt-1">{p.description}</p>}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
