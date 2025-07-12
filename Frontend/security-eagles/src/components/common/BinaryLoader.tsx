import React, { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';

interface BinaryLoaderProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  fullScreen?: boolean;
  message?: string;
  className?: string;
}

const BinaryLoader: React.FC<BinaryLoaderProps> = ({
  size = 'md',
  fullScreen = false,
  message = 'Loading...',
  className
}) => {
  const [binaryStrings, setBinaryStrings] = useState<string[]>([]);

  useEffect(() => {
    const generateBinaryString = () => {
      return Array.from({ length: 20 }, () => 
        Math.random() > 0.5 ? '1' : '0'
      ).join('');
    };

    const interval = setInterval(() => {
      setBinaryStrings(prev => [
        ...prev.slice(-10), // Keep last 10 strings
        generateBinaryString()
      ]);
    }, 100);

    return () => clearInterval(interval);
  }, []);

  const sizeClasses = {
    sm: 'w-8 h-8 text-xs',
    md: 'w-16 h-16 text-sm',
    lg: 'w-24 h-24 text-base',
    xl: 'w-32 h-32 text-lg'
  };

  const containerClasses = fullScreen 
    ? 'fixed inset-0 z-50 bg-background/80 backdrop-blur-sm' 
    : '';

  return (
    <div className={cn(
      'flex flex-col items-center justify-center',
      containerClasses,
      className
    )}>
      {/* Binary Rain Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {Array.from({ length: 6 }).map((_, i) => (
          <div
            key={i}
            className="absolute text-secondary/20 font-mono text-xs animate-binary-rain"
            style={{
              left: `${i * 16 + 10}%`,
              animationDelay: `${i * 0.5}s`,
              animationDuration: `${3 + i * 0.5}s`
            }}
          >
            {binaryStrings.slice(0, 15).map((str, idx) => (
              <div key={idx} className="whitespace-nowrap">
                {str}
              </div>
            ))}
          </div>
        ))}
      </div>

      {/* Central Loading Icon */}
      <div className={cn(
        'relative flex items-center justify-center rounded-full border-2 border-secondary bg-card loading-pulse',
        sizeClasses[size]
      )}>
        {/* CPU Chip Icon */}
        <div className="relative">
          <div className="w-6 h-6 border border-secondary/60 rounded-sm bg-primary/20">
            <div className="absolute inset-1 grid grid-cols-3 gap-0.5">
              {Array.from({ length: 9 }).map((_, i) => (
                <div 
                  key={i} 
                  className={cn(
                    'bg-secondary rounded-xs',
                    Math.random() > 0.5 ? 'animate-pulse' : ''
                  )}
                />
              ))}
            </div>
          </div>
          
          {/* Connection Lines */}
          <div className="absolute -left-2 top-1/2 w-1 h-0.5 bg-secondary/60" />
          <div className="absolute -right-2 top-1/2 w-1 h-0.5 bg-secondary/60" />
          <div className="absolute left-1/2 -top-2 w-0.5 h-1 bg-secondary/60" />
          <div className="absolute left-1/2 -bottom-2 w-0.5 h-1 bg-secondary/60" />
        </div>
      </div>

      {/* Loading Message */}
      {message && (
        <div className="mt-4 text-center">
          <p className="text-foreground font-mono text-sm glitch" data-text={message}>
            {message}
          </p>
          <div className="flex justify-center mt-2 space-x-1">
            {Array.from({ length: 3 }).map((_, i) => (
              <div
                key={i}
                className="w-1 h-1 bg-secondary rounded-full animate-pulse"
                style={{ animationDelay: `${i * 0.2}s` }}
              />
            ))}
          </div>
        </div>
      )}

      {/* Binary Code Stream */}
      <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 text-xs font-mono text-muted-foreground">
        {binaryStrings.slice(-1)[0]?.slice(0, 12)}
      </div>
    </div>
  );
};

export default BinaryLoader;