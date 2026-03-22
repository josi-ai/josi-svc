import type { Metadata } from 'next';
import { Inter, DM_Serif_Display, DM_Serif_Text } from 'next/font/google';
import Providers from '@/components/providers';
import './globals.css';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

const dmSerifDisplay = DM_Serif_Display({
  weight: '400',
  subsets: ['latin'],
  variable: '--font-display',
  display: 'swap',
});

const dmSerifText = DM_Serif_Text({
  weight: '400',
  subsets: ['latin'],
  variable: '--font-reading',
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
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${inter.variable} ${dmSerifDisplay.variable} ${dmSerifText.variable}`}
      >
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
