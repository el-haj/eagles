import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Eye, Calendar, User } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import BinaryLoader from '@/components/common/BinaryLoader';
import MainLayout from '@/components/layout/MainLayout';
import { API_BASE_URL } from '@/lib/api';

interface NewsImage {
  id: number;
  image_url: string;
  caption: string;
}

interface NewsItem {
  id: number;
  title: string;
  author: string;
  description: string;
  long_description: string;
  is_published: boolean;
  published_at: string;
  created_by: number;
  created_at: string;
  updated_at: string;
  tags: string[];
  images: NewsImage[];
  views: number;
}

interface NewsResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: NewsItem[];
}

const News = () => {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [hasNext, setHasNext] = useState(false);
  const { token } = useAuth();

  const fetchNews = async (pageNum: number = 1) => {
    try {
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(
        `${API_BASE_URL}/news/paginated/?page=${pageNum}&page_size=10`,
        { headers }
      );

      if (response.ok) {
        const data: NewsResponse = await response.json();
        if (pageNum === 1) {
          setNews(data.results);
        } else {
          setNews(prev => [...prev, ...data.results]);
        }
        setHasNext(!!data.next);
      }
    } catch (error) {
      console.error('Error fetching news:', error);
    } finally {
      setLoading(false);
    }
  };

  const incrementView = async (newsId: number) => {
    try {
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };
      
      await fetch(`${API_BASE_URL}/news/${newsId}/view/`, {
        method: 'POST',
        headers
      });
      
      // Update local state
      setNews(prev => prev.map(item => 
        item.id === newsId ? { ...item, views: item.views + 1 } : item
      ));
    } catch (error) {
      console.error('Error incrementing view:', error);
    }
  };

  useEffect(() => {
    fetchNews();
  }, []);

  const loadMore = () => {
    const nextPage = page + 1;
    setPage(nextPage);
    fetchNews(nextPage);
  };

  if (loading) {
    return <BinaryLoader fullScreen message="Loading latest news..." />;
  }

  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gradient mb-4 glitch" data-text="Security News">
            Security News
          </h1>
          <p className="text-muted-foreground text-lg">
            Stay updated with the latest cybersecurity news and insights
          </p>
        </div>

        <div className="grid gap-6">
          {news.map((item) => (
            <Card key={item.id} className="cyber-card animate-fade-in hover-scale">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-xl mb-2 hover:text-secondary transition-colors cursor-pointer"
                      onClick={() => incrementView(item.id)}>
                      {item.title}
                    </CardTitle>
                    <CardDescription className="text-base mb-4">
                      {item.description}
                    </CardDescription>
                  </div>
                  {item.images.length > 0 && (
                    <img 
                      src={`https://api.securityeagles.com${item.images[0].image_url}`}
                      alt={item.images[0].caption}
                      className="w-24 h-24 object-cover rounded-md ml-4"
                    />
                  )}
                </div>
                
                <div className="flex flex-wrap gap-2 mb-4">
                  {item.tags.map((tag, idx) => (
                    <Badge key={tag + '-' + item.id + '-' + idx} variant="secondary" className="text-xs">
                      {tag}
                    </Badge>
                  ))}
                </div>

                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <User className="w-4 h-4" />
                    {item.author}
                  </div>
                  <div className="flex items-center gap-1">
                    <Calendar className="w-4 h-4" />
                    {new Date(item.published_at).toLocaleDateString()}
                  </div>
                  <div className="flex items-center gap-1">
                    <Eye className="w-4 h-4" />
                    {item.views} views
                  </div>
                </div>
              </CardHeader>
              
              {item.long_description && (
                <CardContent>
                  <div className="prose prose-sm dark:prose-invert max-w-none">
                    <div dangerouslySetInnerHTML={{ __html: item.long_description }} />
                  </div>
                </CardContent>
              )}
            </Card>
          ))}
        </div>

        {hasNext && (
          <div className="flex justify-center mt-8">
            <Button onClick={loadMore} variant="outline" className="hover-glow">
              Load More News
            </Button>
          </div>
        )}

        {news.length === 0 && (
          <div className="text-center py-12">
            <p className="text-muted-foreground text-lg">No news available at the moment.</p>
          </div>
        )}
      </div>
    </MainLayout>
  );
};

export default News;