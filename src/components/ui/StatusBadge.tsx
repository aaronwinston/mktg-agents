interface StatusBadgeProps {
  status: 'pending' | 'active' | 'complete' | string;
}

const STATUS_CONFIG = {
  pending: { label: 'Pending', className: 'bg-fg-tertiary/10 text-fg-tertiary' },
  active: { label: 'Active', className: 'bg-warning/10 text-warning' },
  complete: { label: 'Complete', className: 'bg-success/10 text-success' },
};

export function StatusBadge({ status }: StatusBadgeProps) {
  const config = STATUS_CONFIG[status as keyof typeof STATUS_CONFIG] || { label: status, className: 'bg-bg-tertiary text-fg-secondary' };
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${config.className}`}>
      {config.label}
    </span>
  );
}
