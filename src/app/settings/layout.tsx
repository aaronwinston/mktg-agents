'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

interface SettingsLayout {
  children: React.ReactNode;
}

export default function SettingsLayout({ children }: SettingsLayout) {
  const pathname = usePathname();

  const sections = [
    { href: '/settings', label: 'Engine & Rules', isMain: true },
    { href: '/settings/runtimes', label: 'Runtime Credentials' },
    { href: '/settings/usage', label: 'Usage & Billing' },
  ];

  return (
    <div className="flex h-full">
      {/* Sidebar */}
      <div className="w-48 border-r border-gray-200 bg-gray-50 flex flex-col">
        <div className="p-6 border-b border-gray-200">
          <h2 className="font-semibold text-gray-900">Settings</h2>
        </div>
        <nav className="flex-1 overflow-y-auto p-4 space-y-1">
          {sections.map((section) => (
            <Link
              key={section.href}
              href={section.href}
              className={`block px-4 py-2 text-sm rounded-md transition ${
                pathname === section.href
                  ? 'bg-blue-100 text-blue-700 font-medium'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              {section.label}
            </Link>
          ))}
        </nav>
      </div>

      {/* Main content */}
      <div className="flex-1 overflow-auto">
        {children}
      </div>
    </div>
  );
}
