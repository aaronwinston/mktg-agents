'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

export default function Sidebar() {
  const pathname = usePathname();
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [projects, setProjects] = useState<any[]>([]);

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { api.getProjects().then(setProjects).catch(() => {}); }, []);

  const navItems = [
    { href: '/dashboard', label: 'Dashboard' },
    { href: '/intelligence', label: 'Intelligence' },
    { href: '/settings', label: 'Settings' },
  ];

  return (
    <aside className="w-56 border-r bg-background flex flex-col">
      <div className="p-4 border-b">
        <h1 className="font-bold text-sm">ForgeOS</h1>
        <p className="text-xs text-muted-foreground">Marketing Command Center</p>
      </div>
      <nav className="p-2 space-y-1">
        {navItems.map(item => (
          <Link
            key={item.href}
            href={item.href}
            className={`block px-3 py-2 rounded text-sm ${pathname === item.href ? 'bg-accent font-medium' : 'hover:bg-accent/50'}`}
          >
            {item.label}
          </Link>
        ))}
      </nav>
      <div className="p-2 border-t mt-2">
        <p className="text-xs text-muted-foreground px-3 mb-1 uppercase font-semibold">Projects</p>
        {projects.map(p => (
          <Link
            key={p.id}
            href={`/projects/${p.id}`}
            className={`block px-3 py-1.5 rounded text-xs ${pathname === `/projects/${p.id}` ? 'bg-accent font-medium' : 'hover:bg-accent/50'}`}
          >
            {p.name}
          </Link>
        ))}
        <button
          className="w-full text-left px-3 py-1.5 text-xs text-muted-foreground hover:text-foreground"
          onClick={async () => {
            const name = prompt('Project name:');
            if (name) {
              await api.createProject({ name });
              api.getProjects().then(setProjects);
            }
          }}
        >
          + New project
        </button>
      </div>
    </aside>
  );
}
