import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import MainLayout from '@/components/layout/MainLayout';
import { useAuth } from '@/contexts/AuthContext';

const Index = () => {
  const { user } = useAuth();

  const features = [
    {
      title: 'Latest News',
      description: 'Stay updated with the latest cybersecurity news and insights',
      icon: '📰',
      href: '/news'
    },
    {
      title: 'Events & Webinars',
      description: 'Join exclusive events and expand your network',
      icon: '🎯',
      href: '/events'
    },
    {
      title: 'Learning Paths',
      description: 'Structured learning journeys for every skill level',
      icon: '🎓',
      href: '/learning'
    },
    {
      title: 'Hands-on Labs',
      description: 'Practice your skills in real-world scenarios',
      icon: '🔬',
      href: '/labs'
    },
    {
      title: 'Job Opportunities',
      description: 'Discover your next career opportunity',
      icon: '💼',
      href: '/jobs'
    },
    {
      title: 'Documentation',
      description: 'Comprehensive guides and resources',
      icon: '📚',
      href: '/docs'
    }
  ];

  return (
    <MainLayout>
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-r from-primary via-primary to-secondary/20">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmZmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PGNpcmNsZSBjeD0iMzAiIGN5PSIzMCIgcj0iMiIvPjwvZz48L2c+PC9zdmc+')] opacity-20" />
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 sm:py-32">
          <div className="text-center">
            <h1 className="text-4xl sm:text-6xl font-bold text-primary-foreground mb-6 glitch" data-text="Security Eagles">
              <span className="text-gradient-secondary">Security</span>{' '}
              <span className="text-primary-foreground">Eagles</span>
            </h1>
            
            <p className="text-xl sm:text-2xl text-primary-foreground/90 mb-8 max-w-3xl mx-auto">
              Soar to new heights in cybersecurity. Learn, practice, and advance your career 
              with cutting-edge training and real-world experience.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              {!user ? (
                <>
                  <Button size="lg" variant="secondary" className="hover-glow" asChild>
                    <Link to="/register">Get Started Free</Link>
                  </Button>
                  <Button size="lg" variant="outline" className="border-primary-foreground text-primary-foreground hover:bg-primary-foreground hover:text-primary" asChild>
                    <Link to="/login">Sign In</Link>
                  </Button>
                </>
              ) : (
                <Button size="lg" variant="secondary" className="hover-glow" asChild>
                  <Link to="/learning">Continue Learning</Link>
                </Button>
              )}
            </div>

            {user && (
              <div className="mt-6 p-4 bg-card/20 backdrop-blur-sm rounded-lg border border-primary-foreground/20">
                <p className="text-primary-foreground/80">
                  Welcome back, <span className="font-semibold text-secondary">{user.first_name}</span>! 
                  Your current score: <span className="font-bold text-secondary">{user.score}</span>
                </p>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl sm:text-4xl font-bold text-foreground mb-4">
            Everything You Need to Excel
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Comprehensive platform designed for cybersecurity professionals at every stage of their journey
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <Card 
              key={feature.title} 
              className="hover-glow transition-all duration-300 animate-fade-in-up border-border/50 hover:border-secondary/50"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <CardHeader>
                <div className="text-4xl mb-2">{feature.icon}</div>
                <CardTitle className="text-xl text-foreground">{feature.title}</CardTitle>
                <CardDescription className="text-muted-foreground">
                  {feature.description}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button variant="outline" className="w-full hover:bg-secondary hover:text-secondary-foreground" asChild>
                  <Link to={feature.href}>Explore</Link>
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-accent/30 border-y border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-foreground mb-4">
              Ready to Elevate Your Cybersecurity Career?
            </h2>
            <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
              Join thousands of professionals who trust Security Eagles for their continuous learning and career advancement.
            </p>
            {!user && (
              <Button size="lg" className="hover-glow" asChild>
                <Link to="/register">Start Your Journey</Link>
              </Button>
            )}
          </div>
        </div>
      </section>
    </MainLayout>
  );
};

export default Index;
