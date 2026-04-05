'use client';

export function ComingSoonCard({ icon, bgColor, message }: { icon: React.ReactNode; bgColor: string; message: string }) {
  return (
    <div
      style={{
        display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
        border: '1px solid var(--border)', borderRadius: 12, background: 'var(--bg-card)',
        padding: '64px 24px', textAlign: 'center',
      }}
    >
      <div
        style={{
          width: 48, height: 48, borderRadius: 12, display: 'flex',
          alignItems: 'center', justifyContent: 'center', background: bgColor, marginBottom: 16,
        }}
      >
        {icon}
      </div>
      <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>{message}</p>
    </div>
  );
}
