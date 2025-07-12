import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ExternalLink, Clock, Award, Target, Timer, TrendingUp } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/hooks/use-toast';
import BinaryLoader from '@/components/common/BinaryLoader';
import MainLayout from '@/components/layout/MainLayout';
import { API_BASE_URL } from '@/lib/api';

interface Lab {
  id: number;
  name: string;
  description: string;
  lab_url: string;
  objectives: string;
  difficulty_level: string;
  category: string;
  prize: string;
  estimated_time: number;
  notes: string;
  cooldown_minutes: number;
  max_score: number;
  reward_points: number;
  external_lab_id: string;
  created_by: number;
  created_at: string;
  updated_at: string;
}

interface UserLabAttempt {
  id: number;
  user: number;
  lab: number;
  time_spent: number;
  started_at: string;
  ended_at: string;
  score: number;
  is_ok: boolean;
  reward_points_earned: number;
  external_attempt_id: string | null;
  cooldown_until: string;
  created_at: string;
  updated_at: string;
}

interface LabsResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Lab[];
}

const Labs = () => {
  const [labs, setLabs] = useState<Lab[]>([]);
  const [attempts, setAttempts] = useState<UserLabAttempt[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [hasNext, setHasNext] = useState(false);
  const { token } = useAuth();
  const { toast } = useToast();

  const fetchLabs = async (pageNum: number = 1) => {
    try {
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(
        `${API_BASE_URL}/labs/paginated/?page=${pageNum}&page_size=10`,
        { headers }
      );

      if (response.ok) {
        const data: LabsResponse = await response.json();
        // Defensive: ensure data.results is always an array
        const results = Array.isArray(data.results) ? data.results : [];
        if (pageNum === 1) {
          setLabs(results);
        } else {
          setLabs(prev => [...prev, ...results]);
        }
        setHasNext(!!data.next);
      } else {
        setLabs([]); // fallback to empty array on error
      }
    } catch (error) {
      setLabs([]); // fallback to empty array on error
      console.error('Error fetching labs:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAttempts = async () => {
    if (!token) return;

    try {
      const response = await fetch(`${API_BASE_URL}/labs/user-labs/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setAttempts(Array.isArray(data) ? data : []);
      }
    } catch (error) {
      console.error('Error fetching attempts:', error);
    }
  };

  const startLab = async (lab: Lab) => {
    if (!token) {
      toast({
        title: "Authentication required",
        description: "Please log in to start labs.",
        variant: "destructive",
      });
      return;
    }

    // Check cooldown
    const lastAttempt = attempts.find(attempt => attempt.lab === lab.id);
    if (lastAttempt && new Date(lastAttempt.cooldown_until) > new Date()) {
      const cooldownTime = Math.ceil((new Date(lastAttempt.cooldown_until).getTime() - new Date().getTime()) / (1000 * 60));
      toast({
        title: "Cooldown active",
        description: `Please wait ${cooldownTime} minutes before attempting again.`,
        variant: "destructive",
      });
      return;
    }

    // Open external lab
    window.open(lab.lab_url, '_blank');
    
    toast({
      title: "Lab started!",
      description: "Complete the lab and return here to submit your results.",
    });
  };

  const submitResults = async (labId: number, score: number, timeSpent: number) => {
    if (!token) return;

    try {
      const now = new Date().toISOString();
      const startTime = new Date(new Date().getTime() - timeSpent * 60000).toISOString();

      const response = await fetch(`${API_BASE_URL}/labs/user-labs/create/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          lab: labId,
          time_spent: timeSpent,
          started_at: startTime,
          ended_at: now,
          score: score,
          is_ok: score >= 70, // Assuming 70% is passing
        }),
      });

      if (response.ok) {
        toast({
          title: "Results submitted!",
          description: "Your lab attempt has been recorded.",
        });
        fetchAttempts();
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to submit results.",
        variant: "destructive",
      });
    }
  };

  useEffect(() => {
    fetchLabs();
    if (token) {
      fetchAttempts();
    }
  }, [token]);

  const loadMore = () => {
    const nextPage = page + 1;
    setPage(nextPage);
    fetchLabs(nextPage);
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case 'beginner': return 'bg-green-500/20 text-green-300';
      case 'intermediate': return 'bg-yellow-500/20 text-yellow-300';
      case 'advanced': return 'bg-red-500/20 text-red-300';
      default: return 'bg-secondary/20 text-secondary';
    }
  };

  const getLabAttempt = (labId: number) => {
    return attempts.find(attempt => attempt.lab === labId);
  };

  const isCooldownActive = (attempt: UserLabAttempt | undefined) => {
    if (!attempt) return false;
    return new Date(attempt.cooldown_until) > new Date();
  };

  if (loading) {
    return <BinaryLoader fullScreen message="Loading lab environment..." />;
  }

  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gradient mb-4 glitch" data-text="Cyber Labs">
            Cyber Labs
          </h1>
          <p className="text-muted-foreground text-lg">
            Hands-on cybersecurity labs to test and improve your skills
          </p>
        </div>

        {token && attempts.length > 0 && (
          <div className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">Your Lab History</h2>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {attempts.slice(0, 3).map((attempt) => {
                const lab = labs.find(l => l.id === attempt.lab);
                return (
                  <Card key={attempt.id} className="cyber-card">
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-semibold text-sm">{lab?.name || `Lab ${attempt.lab}`}</h3>
                        <Badge variant={attempt.is_ok ? "default" : "secondary"}>
                          {attempt.score}%
                        </Badge>
                      </div>
                      <div className="flex items-center gap-4 text-xs text-muted-foreground">
                        <div className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {attempt.time_spent}m
                        </div>
                        <div className="flex items-center gap-1">
                          <Award className="w-3 h-3" />
                          {attempt.reward_points_earned} pts
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>
        )}

        <div className="grid gap-6">
          {labs.map((lab) => {
            const attempt = getLabAttempt(lab.id);
            const onCooldown = isCooldownActive(attempt);
            const cooldownTime = attempt && onCooldown 
              ? Math.ceil((new Date(attempt.cooldown_until).getTime() - new Date().getTime()) / (1000 * 60))
              : 0;

            return (
              <Card key={lab.id} className="cyber-card animate-fade-in hover-scale">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-xl mb-2">{lab.name}</CardTitle>
                      <CardDescription className="text-base mb-4">
                        {lab.description}
                      </CardDescription>
                      
                      <div className="flex flex-wrap gap-2 mb-4">
                        <Badge className={getDifficultyColor(lab.difficulty_level)}>
                          {lab.difficulty_level}
                        </Badge>
                        <Badge variant="outline">{lab.category}</Badge>
                        {attempt && (
                          <Badge variant={attempt.is_ok ? "default" : "secondary"}>
                            Last Score: {attempt.score}%
                          </Badge>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div className="flex items-center gap-2 text-muted-foreground">
                      <Clock className="w-4 h-4" />
                      <div>
                        <div className="font-medium">{lab.estimated_time}m</div>
                        <div className="text-xs">Estimated</div>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2 text-muted-foreground">
                      <Target className="w-4 h-4" />
                      <div>
                        <div className="font-medium">{lab.max_score}</div>
                        <div className="text-xs">Max Score</div>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 text-muted-foreground">
                      <Award className="w-4 h-4" />
                      <div>
                        <div className="font-medium">{lab.reward_points}</div>
                        <div className="text-xs">Reward Points</div>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 text-muted-foreground">
                      <Timer className="w-4 h-4" />
                      <div>
                        <div className="font-medium">{lab.cooldown_minutes}m</div>
                        <div className="text-xs">Cooldown</div>
                      </div>
                    </div>
                  </div>
                </CardHeader>
                
                <CardContent>
                  <div className="mb-4">
                    <h4 className="font-semibold mb-2">Objectives:</h4>
                    <p className="text-sm text-muted-foreground">{lab.objectives}</p>
                  </div>

                  {lab.prize && (
                    <div className="mb-4">
                      <h4 className="font-semibold mb-2">Prize:</h4>
                      <p className="text-sm text-muted-foreground">{lab.prize}</p>
                    </div>
                  )}

                  {lab.notes && (
                    <div className="mb-4">
                      <h4 className="font-semibold mb-2">Notes:</h4>
                      <p className="text-sm text-muted-foreground">{lab.notes}</p>
                    </div>
                  )}

                  <div className="flex items-center justify-between">
                    {onCooldown && (
                      <div className="text-sm text-muted-foreground">
                        Cooldown: {cooldownTime} minutes remaining
                      </div>
                    )}
                    
                    <div className="flex gap-2 ml-auto">
                      <Button
                        onClick={() => startLab(lab)}
                        disabled={onCooldown}
                        className="hover-glow"
                      >
                        <ExternalLink className="w-4 h-4 mr-2" />
                        {attempt ? "Retry Lab" : "Start Lab"}
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {hasNext && (
          <div className="flex justify-center mt-8">
            <Button onClick={loadMore} variant="outline" className="hover-glow">
              Load More Labs
            </Button>
          </div>
        )}

        {labs.length === 0 && (
          <div className="text-center py-12">
            <p className="text-muted-foreground text-lg">No labs available at the moment.</p>
          </div>
        )}
      </div>
    </MainLayout>
  );
};

export default Labs;