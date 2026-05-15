import '@/styles/globals.css';
import type { ReactNode } from 'react';

export default function RootLayout({ children }: { children: ReactNode }) {
  return <html lang="de"><body className="bg-background text-white min-h-screen">{children}</body></html>;
}
