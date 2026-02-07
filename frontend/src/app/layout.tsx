import './globals.css';
import type { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'NCR Voyix Inventory Health Dashboard',
  description: 'Predictive inventory management with anomaly detection',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased bg-ncr-gray-50">
        {/* NCR Voyix Header with Purple Theme */}
        <nav className="bg-white border-b border-ncr-gray-200 sticky top-0 z-50 shadow-sm">
          <div className="max-w-7xl mx-auto px-8">
            <div className="flex items-center justify-between h-16">
              {/* Logo */}
              <Link href="/" className="flex items-center space-x-2">
                <span className="text-2xl font-bold text-ncr-dark tracking-tight">
                  NCR V
                  <span className="inline-flex items-center">
                    <span className="relative">
                      <span className="text-ncr-primary">O</span>
                      <span className="absolute inset-0 flex items-center justify-center">
                        <span className="w-1.5 h-1.5 bg-ncr-primary rounded-full"></span>
                      </span>
                    </span>
                  </span>
                  YIX
                </span>
              </Link>

              {/* Navigation */}
              <div className="flex items-center space-x-1">
                <NavLink href="/" label="Overview" />
                <NavLink href="/transfers" label="Transfers" />
              </div>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="min-h-screen">{children}</main>

        {/* Footer */}
        <footer className="bg-white border-t border-ncr-gray-200 mt-12">
          <div className="max-w-7xl mx-auto px-8 py-6">
            <div className="flex items-center justify-between text-sm text-ncr-gray-600">
              <p>© 2025 NCR Voyix Corporation</p>
              <p className="text-ncr-primary font-semibold">UGAHacks 11</p>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}

function NavLink({ href, label }: { href: string; label: string }) {
  return (
    <Link
      href={href}
      className="px-4 py-2 rounded-lg text-ncr-gray-700 hover:text-ncr-primary hover:bg-ncr-primary-pale transition-colors font-medium"
    >
      {label}
    </Link>
  );
}