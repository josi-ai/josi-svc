import DashboardShell from '@/components/layout/dashboard-shell';

// This layout is a server component. DashboardShell is a client component
// that defers all rendering until after mount — zero SSR for the dashboard,
// zero hydration mismatches. Public pages (landing, pricing) use other layouts.
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <DashboardShell>{children}</DashboardShell>;
}
