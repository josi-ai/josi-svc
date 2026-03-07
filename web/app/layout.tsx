import type { Metadata } from 'next';
import { Inter, JetBrains_Mono } from 'next/font/google';
import Providers from '@/components/providers';
import './globals.css';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'Josi',
  description: 'Multi-tradition astrology platform',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${inter.variable} ${jetbrainsMono.variable}`}
        style={{ fontFamily: 'var(--font-inter)', backgroundColor: '#0f0a1e', margin: 0 }}
      >
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
