import React, { ReactNode } from 'react';
import Navigation from './Navigation';
import { cn } from '@/lib/utils';

interface MainLayoutProps {
  children: ReactNode;
  className?: string;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children, className }) => {
  return (
    <div className="min-h-screen bg-background">
      {/* Binary Matrix Background */}
      <div className="binary-matrix">
        <div className="absolute inset-0 opacity-5">
          {Array.from({ length: 20 }).map((_, i) => (
            <div
              key={i}
              className="absolute text-secondary font-mono text-xs animate-binary-rain"
              style={{
                left: `${i * 5}%`,
                animationDelay: `${i * 0.3}s`,
                animationDuration: `${4 + (i % 3)}s`
              }}
            >
              {Array.from({ length: 50 }).map((_, j) => (
                <div key={j}>{Math.random() > 0.5 ? '1' : '0'}</div>
              ))}
            </div>
          ))}
        </div>
      </div>

      <Navigation />
      
      <main className={cn('relative z-10', className)}>
        {children}
      </main>

      {/* Footer */}
      <footer className="relative z-10 bg-card/50 border-t border-border mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="col-span-1 md:col-span-2">
              <div className="flex items-center space-x-2 mb-4">
                <div className="w-8 h-8 bg-gradient-primary rounded-md flex items-center justify-center">
                  <div className="w-5 h-5 border border-primary-foreground rounded-sm">
                    <div className="w-full h-full bg-secondary/20 relative">
                      <div className="absolute inset-1 grid grid-cols-2 gap-0.5">
                        <div className="bg-primary-foreground rounded-xs" />
                        <div className="bg-primary-foreground rounded-xs opacity-60" />
                        <div className="bg-primary-foreground rounded-xs opacity-60" />
                        <div className="bg-primary-foreground rounded-xs" />
                      </div>
                    </div>
                  </div>
                </div>
                <span className="text-xl font-bold text-gradient">
                  Security Eagles
                </span>
              </div>
              <p className="text-muted-foreground mb-4">
                Empowering cybersecurity professionals through cutting-edge learning, 
                hands-on labs, and career opportunities.
              </p>
              <div className="text-xs text-muted-foreground">
                © 2025 Security Eagles. All rights reserved.
              </div>
            </div>
            
            <div>
              <h3 className="font-semibold text-foreground mb-4">Platform</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><a href="/news" className="hover:text-secondary transition-colors">News</a></li>
                <li><a href="/events" className="hover:text-secondary transition-colors">Events</a></li>
                <li><a href="/learning" className="hover:text-secondary transition-colors">Learning Paths</a></li>
                <li><a href="/labs" className="hover:text-secondary transition-colors">Labs</a></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold text-foreground mb-4">Community</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><a href="/jobs" className="hover:text-secondary transition-colors">Job Board</a></li>
                <li><a href="/docs" className="hover:text-secondary transition-colors">Documentation</a></li>
                <li><a href="/support" className="hover:text-secondary transition-colors">Support</a></li>
                <li><a href="/contact" className="hover:text-secondary transition-colors">Contact</a></li>
              </ul>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default MainLayout;