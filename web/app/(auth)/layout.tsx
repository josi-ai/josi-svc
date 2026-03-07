export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'radial-gradient(ellipse at 50% 30%, rgba(107, 92, 231, 0.1) 0%, #0f0a1e 70%)',
        padding: 24,
      }}
    >
      {children}
    </div>
  );
}
