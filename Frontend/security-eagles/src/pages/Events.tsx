import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Calendar, MapPin, Users, Clock, ExternalLink } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/hooks/use-toast';
import BinaryLoader from '@/components/common/BinaryLoader';
import MainLayout from '@/components/layout/MainLayout';
import { API_BASE_URL } from '@/lib/api';

interface EventImage {
  id: number;
  image_url: string;
  caption: string;
}

interface Event {
  id: number;
  title: string;
  description: string;
  long_description: string;
  event_type: string;
  is_physical: boolean;
  location: string | null;
  platform: string;
  platform_url: string;
  start_time: string;
  end_time: string;
  max_attendees: number;
  registration_deadline: string;
  is_recurring: boolean;
  recurrence_date: string | null;
  organizer: string;
  is_active: boolean;
  in_lights_date: string;
  created_by: number;
  created_at: string;
  updated_at: string;
  images: EventImage[];
  is_registered: boolean;
}

interface EventsResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Event[];
}

const Events = () => {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [hasNext, setHasNext] = useState(false);
  const { token } = useAuth();
  const { toast } = useToast();

  const fetchEvents = async (pageNum: number = 1) => {
    try {
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(
        `${API_BASE_URL}/events/paginated/?page=${pageNum}&page_size=10`,
        { headers }
      );

      if (response.ok) {
        const data: EventsResponse = await response.json();
        if (pageNum === 1) {
          setEvents(data.results);
        } else {
          setEvents(prev => [...prev, ...data.results]);
        }
        setHasNext(!!data.next);
      }
    } catch (error) {
      console.error('Error fetching events:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRegistration = async (eventId: number, isRegistering: boolean) => {
    if (!token) return;

    try {
      const method = isRegistering ? 'POST' : 'DELETE';
      const response = await fetch(
        `${API_BASE_URL}/events/${eventId}/register/`,
        {
          method,
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (response.ok) {
        setEvents(prev => prev.map(event => 
          event.id === eventId 
            ? { ...event, is_registered: isRegistering }
            : event
        ));
        
        toast({
          title: isRegistering ? "Registration successful!" : "Unregistered successfully!",
          description: isRegistering 
            ? "You are now registered for this event." 
            : "You have been unregistered from this event.",
        });
      } else {
        throw new Error('Registration failed');
      }
    } catch (error) {
      toast({
        title: "Registration failed",
        description: "An error occurred. Please try again.",
        variant: "destructive",
      });
    }
  };

  useEffect(() => {
    fetchEvents();
  }, []);

  const loadMore = () => {
    const nextPage = page + 1;
    setPage(nextPage);
    fetchEvents(nextPage);
  };

  if (loading) {
    return <BinaryLoader fullScreen message="Loading events..." />;
  }

  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gradient mb-4 glitch" data-text="Cyber Events">
            Cyber Events
          </h1>
          <p className="text-muted-foreground text-lg">
            Join cybersecurity events, workshops, and webinars
          </p>
        </div>

        <div className="grid gap-6">
          {events.map((event) => (
            <Card key={event.id} className="cyber-card animate-fade-in hover-scale">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <CardTitle className="text-xl">{event.title}</CardTitle>
                      <Badge variant={event.event_type === 'Webinar' ? 'secondary' : 'default'}>
                        {event.event_type}
                      </Badge>
                      {event.is_registered && (
                        <Badge variant="outline" className="text-secondary border-secondary">
                          Registered
                        </Badge>
                      )}
                    </div>
                    <CardDescription className="text-base mb-4">
                      {event.description}
                    </CardDescription>
                  </div>
                  {event.images.length > 0 && (
                    <img 
                      src={`https://api.securityeagles.com${event.images[0].image_url}`}
                      alt={event.images[0].caption}
                      className="w-24 h-24 object-cover rounded-md ml-4"
                    />
                  )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm text-muted-foreground">
                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4" />
                    <div>
                      <div>{new Date(event.start_time).toLocaleDateString()}</div>
                      <div>{new Date(event.start_time).toLocaleTimeString()}</div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                    <div>
                      Duration: {Math.round((new Date(event.end_time).getTime() - new Date(event.start_time).getTime()) / (1000 * 60))} min
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    {event.is_physical ? <MapPin className="w-4 h-4" /> : <ExternalLink className="w-4 h-4" />}
                    <div>{event.is_physical ? event.location : event.platform}</div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Users className="w-4 h-4" />
                    <div>Max: {event.max_attendees}</div>
                  </div>
                </div>
              </CardHeader>
              
              <CardContent>
                {event.long_description && (
                  <div className="prose prose-sm dark:prose-invert max-w-none mb-4">
                    <div dangerouslySetInnerHTML={{ __html: event.long_description }} />
                  </div>
                )}

                <div className="flex items-center justify-between">
                  <div className="text-sm text-muted-foreground">
                    <div>Organizer: {event.organizer}</div>
                    <div>Registration deadline: {new Date(event.registration_deadline).toLocaleDateString()}</div>
                  </div>

                  <div className="flex gap-2">
                    {!event.is_physical && event.platform_url && (
                      <Button variant="outline" size="sm" asChild>
                        <a href={event.platform_url} target="_blank" rel="noopener noreferrer">
                          <ExternalLink className="w-4 h-4 mr-2" />
                          Join Platform
                        </a>
                      </Button>
                    )}
                    
                    {token && (
                      <Button
                        onClick={() => handleRegistration(event.id, !event.is_registered)}
                        variant={event.is_registered ? "outline" : "default"}
                        size="sm"
                        className="hover-glow"
                      >
                        {event.is_registered ? "Unregister" : "Register"}
                      </Button>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {hasNext && (
          <div className="flex justify-center mt-8">
            <Button onClick={loadMore} variant="outline" className="hover-glow">
              Load More Events
            </Button>
          </div>
        )}

        {events.length === 0 && (
          <div className="text-center py-12">
            <p className="text-muted-foreground text-lg">No events available at the moment.</p>
          </div>
        )}
      </div>
    </MainLayout>
  );
};

export default Events;