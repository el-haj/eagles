import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { BookOpen, Clock, Tag, Play, CheckCircle, Lock } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/hooks/use-toast';
import BinaryLoader from '@/components/common/BinaryLoader';
import MainLayout from '@/components/layout/MainLayout';
import { API_BASE_URL } from '@/lib/api';

interface LearningPath {
  id: number;
  title: string;
  objectives: string;
  category: string;
  tags: string[];
  estimated_time: number;
  meta_data: any;
  created_by: number;
  created_at: string;
  updated_at: string;
  completed: boolean;
  in_progress: boolean;
}

interface PDF {
  id: number;
  order_index: number;
  page_count: number;
  file: string;
  uploaded_at: string;
  meta_data: any;
  unlocked: boolean;
  is_current: boolean;
}

interface LearningPathDetail extends LearningPath {
  pdfs: PDF[];
  current_pdf_id: number;
  last_page: number;
}

const Learning = () => {
  const [paths, setPaths] = useState<LearningPath[]>([]);
  const [selectedPath, setSelectedPath] = useState<LearningPathDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const { token } = useAuth();
  const { toast } = useToast();

  const fetchPaths = async () => {
    if (!token) return;

    try {
      const response = await fetch(`${API_BASE_URL}/learning/paths/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setPaths(data);
      }
    } catch (error) {
      console.error('Error fetching learning paths:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchPathDetail = async (pathId: number) => {
    if (!token) return;

    setDetailLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/learning/paths/${pathId}/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setSelectedPath(data);
      }
    } catch (error) {
      console.error('Error fetching path detail:', error);
    } finally {
      setDetailLoading(false);
    }
  };

  const startLearning = async (pathId: number) => {
    if (!token) return;

    try {
      const response = await fetch(`${API_BASE_URL}/learning/user-learnings/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ learning_path_id: pathId }),
      });

      if (response.ok) {
        toast({
          title: "Learning started!",
          description: "You can now begin this learning path.",
        });
        fetchPaths(); // Refresh to update progress
        fetchPathDetail(pathId);
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to start learning path.",
        variant: "destructive",
      });
    }
  };

  const unlockPDF = async (pathId: number, pdfId: number) => {
    if (!token) return;

    try {
      const response = await fetch(`${API_BASE_URL}/learning/paths/${pathId}/unlock/${pdfId}/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
      });

      if (response.ok) {
        const data = await response.json();
        toast({
          title: "PDF unlocked!",
          description: `Progress: ${(data.completion * 100).toFixed(1)}%`,
        });
        fetchPathDetail(pathId);
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to unlock PDF.",
        variant: "destructive",
      });
    }
  };

  useEffect(() => {
    fetchPaths();
  }, [token]);

  if (loading) {
    return <BinaryLoader fullScreen message="Loading learning paths..." />;
  }

  if (selectedPath && detailLoading) {
    return <BinaryLoader fullScreen message="Loading path details..." />;
  }

  if (selectedPath) {
    const progress = selectedPath.pdfs.length > 0 
      ? (selectedPath.pdfs.filter(pdf => pdf.unlocked).length / selectedPath.pdfs.length) * 100 
      : 0;

    return (
      <MainLayout>
        <div className="container mx-auto px-4 py-8">
          <div className="mb-6">
            <Button 
              variant="outline" 
              onClick={() => setSelectedPath(null)}
              className="mb-4"
            >
              ← Back to Learning Paths
            </Button>
            
            <h1 className="text-4xl font-bold text-gradient mb-4 glitch" data-text={selectedPath.title}>
              {selectedPath.title}
            </h1>
            <p className="text-muted-foreground text-lg mb-6">
              {selectedPath.objectives}
            </p>

            <div className="flex flex-wrap items-center gap-4 mb-6">
              <Badge variant="secondary">{selectedPath.category}</Badge>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Clock className="w-4 h-4" />
                {selectedPath.estimated_time} minutes
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm text-muted-foreground">Progress:</span>
                <Progress value={progress} className="w-32" />
                <span className="text-sm font-medium">{progress.toFixed(1)}%</span>
              </div>
            </div>

            <div className="flex flex-wrap gap-2 mb-8">
              {selectedPath.tags.map((tag) => (
                <Badge key={tag} variant="outline" className="text-xs">
                  <Tag className="w-3 h-3 mr-1" />
                  {tag}
                </Badge>
              ))}
            </div>
          </div>

          <div className="grid gap-4">
            <h2 className="text-2xl font-semibold mb-4">Learning Materials</h2>
            {selectedPath.pdfs.map((pdf, index) => (
              <Card key={pdf.id} className="cyber-card">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="flex items-center justify-center w-10 h-10 rounded-full bg-primary/20">
                        {pdf.unlocked ? (
                          pdf.is_current ? (
                            <Play className="w-5 h-5 text-secondary" />
                          ) : (
                            <CheckCircle className="w-5 h-5 text-green-500" />
                          )
                        ) : (
                          <Lock className="w-5 h-5 text-muted-foreground" />
                        )}
                      </div>
                      <div>
                        <h3 className="font-semibold">Module {pdf.order_index}</h3>
                        <p className="text-sm text-muted-foreground">
                          {pdf.page_count} pages
                          {pdf.is_current && ` • Page ${selectedPath.last_page}`}
                        </p>
                      </div>
                    </div>

                    <div className="flex gap-2">
                      {pdf.unlocked && (
                        <Button variant="outline" size="sm" asChild>
                          <a 
                            href={`https://api.securityeagles.com${pdf.file}`} 
                            target="_blank" 
                            rel="noopener noreferrer"
                          >
                            <BookOpen className="w-4 h-4 mr-2" />
                            Open PDF
                          </a>
                        </Button>
                      )}
                      
                      {!pdf.unlocked && index === 0 && (
                        <Button 
                          onClick={() => unlockPDF(selectedPath.id, pdf.id)}
                          size="sm"
                          className="hover-glow"
                        >
                          Start Learning
                        </Button>
                      )}
                      
                      {!pdf.unlocked && index > 0 && selectedPath.pdfs[index - 1].unlocked && (
                        <Button 
                          onClick={() => unlockPDF(selectedPath.id, pdf.id)}
                          size="sm"
                          className="hover-glow"
                        >
                          Unlock Next
                        </Button>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gradient mb-4 glitch" data-text="Learning Paths">
            Learning Paths
          </h1>
          <p className="text-muted-foreground text-lg">
            Structured learning paths to advance your cybersecurity skills
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {paths.map((path) => (
            <Card key={path.id} className="cyber-card animate-fade-in hover-scale">
              <CardHeader>
                <div className="flex items-start justify-between mb-2">
                  <CardTitle className="text-xl">{path.title}</CardTitle>
                  <Badge variant={path.completed ? "default" : path.in_progress ? "secondary" : "outline"}>
                    {path.completed ? "Completed" : path.in_progress ? "In Progress" : "Not Started"}
                  </Badge>
                </div>
                <CardDescription className="text-base">
                  {path.objectives}
                </CardDescription>
              </CardHeader>
              
              <CardContent>
                <div className="flex items-center justify-between mb-4">
                  <Badge variant="outline">{path.category}</Badge>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Clock className="w-4 h-4" />
                    {path.estimated_time} min
                  </div>
                </div>

                <div className="flex flex-wrap gap-1 mb-4">
                  {path.tags.slice(0, 3).map((tag) => (
                    <Badge key={tag} variant="secondary" className="text-xs">
                      {tag}
                    </Badge>
                  ))}
                  {path.tags.length > 3 && (
                    <Badge variant="secondary" className="text-xs">
                      +{path.tags.length - 3}
                    </Badge>
                  )}
                </div>

                <div className="flex gap-2">
                  <Button 
                    onClick={() => fetchPathDetail(path.id)}
                    className="flex-1 hover-glow"
                  >
                    <BookOpen className="w-4 h-4 mr-2" />
                    View Details
                  </Button>
                  
                  {!path.in_progress && !path.completed && (
                    <Button 
                      onClick={() => startLearning(path.id)}
                      variant="secondary"
                      size="sm"
                    >
                      <Play className="w-4 h-4" />
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {paths.length === 0 && (
          <div className="text-center py-12">
            <p className="text-muted-foreground text-lg">No learning paths available.</p>
          </div>
        )}
      </div>
    </MainLayout>
  );
};

export default Learning;