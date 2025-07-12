import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { MapPin, Building, DollarSign, Clock, ExternalLink, Search, Users } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/hooks/use-toast';
import BinaryLoader from '@/components/common/BinaryLoader';
import MainLayout from '@/components/layout/MainLayout';
import { API_BASE_URL } from '@/lib/api';

interface Job {
  id: number;
  title: string;
  description: string;
  requirements: string;
  responsibilities: string;
  company_name: string;
  logo: string;
  location: string;
  location_url: string;
  job_type: string;
  experience_level: string;
  category: string;
  salary_min: string;
  salary_max: string;
  is_remote: boolean;
  application_deadline: string;
  contact_email: string;
  contact_phone: string;
  external_url: string;
  posted_by: number;
  closed_at: string | null;
  application_count: number;
  in_lights_date: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  is_applied: boolean;
  logo_url: string;
}

interface JobsResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Job[];
}

const Jobs = () => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [highlightedJob, setHighlightedJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [hasNext, setHasNext] = useState(false);
  const [filters, setFilters] = useState({
    search: '',
    category: '',
    location: '',
    job_type: '',
    experience_level: '',
    is_remote: '',
  });
  const { token } = useAuth();
  const { toast } = useToast();

  const fetchHighlightedJob = async () => {
    try {
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${API_BASE_URL}/jobs/highlighted/`, { headers });

      if (response.ok) {
        const data = await response.json();
        setHighlightedJob(data);
      }
    } catch (error) {
      console.error('Error fetching highlighted job:', error);
    }
  };

  const fetchJobs = async (pageNum: number = 1, newFilters = filters) => {
    try {
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const params = new URLSearchParams({
        page: pageNum.toString(),
        page_size: '10',
        ...Object.fromEntries(
          Object.entries(newFilters).filter(([_, value]) => value !== '')
        ),
      });

      const response = await fetch(
        `${API_BASE_URL}/jobs/paginated/?${params}`,
        { headers }
      );

      if (response.ok) {
        const data: JobsResponse = await response.json();
        if (pageNum === 1) {
          setJobs(data.results);
        } else {
          setJobs(prev => [...prev, ...data.results]);
        }
        setHasNext(!!data.next);
      }
    } catch (error) {
      console.error('Error fetching jobs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApplication = async (jobId: number, isApplying: boolean) => {
    if (!token) {
      toast({
        title: "Authentication required",
        description: "Please log in to apply for jobs.",
        variant: "destructive",
      });
      return;
    }

    try {
      const endpoint = isApplying ? 'apply' : 'unapply';
      const response = await fetch(
        `${API_BASE_URL}/jobs/${jobId}/${endpoint}/`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: isApplying ? JSON.stringify({ message: "I am interested in this position." }) : undefined,
        }
      );

      if (response.ok) {
        const updateJob = (job: Job) => 
          job.id === jobId 
            ? { 
                ...job, 
                is_applied: isApplying,
                application_count: isApplying ? job.application_count + 1 : job.application_count - 1
              }
            : job;

        setJobs(prev => prev.map(updateJob));
        if (highlightedJob && highlightedJob.id === jobId) {
          setHighlightedJob(updateJob(highlightedJob));
        }
        
        toast({
          title: isApplying ? "Application submitted!" : "Application withdrawn!",
          description: isApplying 
            ? "Your application has been sent to the employer." 
            : "Your application has been withdrawn.",
        });
      } else {
        throw new Error('Application failed');
      }
    } catch (error) {
      toast({
        title: "Application failed",
        description: "An error occurred. Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleFilterChange = (key: string, value: string) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    setPage(1);
    fetchJobs(1, newFilters);
  };

  const loadMore = () => {
    const nextPage = page + 1;
    setPage(nextPage);
    fetchJobs(nextPage);
  };

  useEffect(() => {
    fetchHighlightedJob();
    fetchJobs();
  }, []);

  if (loading) {
    return <BinaryLoader fullScreen message="Loading job opportunities..." />;
  }

  const JobCard = ({ job, isHighlighted = false }: { job: Job; isHighlighted?: boolean }) => (
    <Card className={`cyber-card animate-fade-in hover-scale ${isHighlighted ? 'border-secondary' : ''}`}>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-4 flex-1">
            {job.logo_url && (
              <img 
                src={`https://api.securityeagles.com${job.logo_url}`}
                alt={`${job.company_name} logo`}
                className="w-12 h-12 object-contain rounded-md bg-card"
              />
            )}
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <CardTitle className="text-xl">{job.title}</CardTitle>
                {isHighlighted && (
                  <Badge variant="secondary" className="text-xs">Featured</Badge>
                )}
                {job.is_applied && (
                  <Badge variant="outline" className="text-secondary border-secondary text-xs">
                    Applied
                  </Badge>
                )}
              </div>
              <CardDescription className="text-base mb-2">
                <strong>{job.company_name}</strong>
              </CardDescription>
              <CardDescription className="text-sm">
                {job.description.length > 200 ? `${job.description.substring(0, 200)}...` : job.description}
              </CardDescription>
            </div>
          </div>
        </div>

        <div className="flex flex-wrap gap-2 mt-4">
          <Badge variant="outline">{job.job_type}</Badge>
          <Badge variant="outline">{job.experience_level}</Badge>
          <Badge variant="outline">{job.category}</Badge>
          {job.is_remote && <Badge variant="secondary">Remote</Badge>}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-2">
            <MapPin className="w-4 h-4" />
            <span>{job.location}</span>
          </div>
          
          {job.salary_min && job.salary_max && (
            <div className="flex items-center gap-2">
              <DollarSign className="w-4 h-4" />
              <span>${job.salary_min} - ${job.salary_max}</span>
            </div>
          )}

          <div className="flex items-center gap-2">
            <Users className="w-4 h-4" />
            <span>{job.application_count} applicants</span>
          </div>
        </div>

        <div className="flex items-center justify-between mt-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4" />
            Deadline: {new Date(job.application_deadline).toLocaleDateString()}
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        <div className="flex items-center justify-between">
          <div className="flex gap-2">
            {job.external_url && (
              <Button variant="outline" size="sm" asChild>
                <a href={job.external_url} target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="w-4 h-4 mr-2" />
                  View Details
                </a>
              </Button>
            )}
          </div>
          
          {token && (
            <Button
              onClick={() => handleApplication(job.id, !job.is_applied)}
              variant={job.is_applied ? "outline" : "default"}
              size="sm"
              className="hover-glow"
            >
              {job.is_applied ? "Withdraw" : "Apply Now"}
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );

  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gradient mb-4 glitch" data-text="Cyber Jobs">
            Cyber Jobs
          </h1>
          <p className="text-muted-foreground text-lg">
            Find your next cybersecurity career opportunity
          </p>
        </div>

        {/* Filters */}
        <div className="mb-8 p-6 bg-card/50 rounded-lg border">
          <h2 className="text-lg font-semibold mb-4">Filter Jobs</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search jobs..."
                value={filters.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                className="pl-10"
              />
            </div>
            
            <Select value={filters.category} onValueChange={(value) => handleFilterChange('category', value)}>
              <SelectTrigger>
                <SelectValue placeholder="Category" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Categories</SelectItem>
                <SelectItem value="Security">Security</SelectItem>
                <SelectItem value="Penetration Testing">Penetration Testing</SelectItem>
                <SelectItem value="Incident Response">Incident Response</SelectItem>
                <SelectItem value="Compliance">Compliance</SelectItem>
              </SelectContent>
            </Select>

            <Select value={filters.job_type} onValueChange={(value) => handleFilterChange('job_type', value)}>
              <SelectTrigger>
                <SelectValue placeholder="Job Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Types</SelectItem>
                <SelectItem value="Full-Time">Full-Time</SelectItem>
                <SelectItem value="Part-Time">Part-Time</SelectItem>
                <SelectItem value="Contract">Contract</SelectItem>
                <SelectItem value="Freelance">Freelance</SelectItem>
              </SelectContent>
            </Select>

            <Select value={filters.experience_level} onValueChange={(value) => handleFilterChange('experience_level', value)}>
              <SelectTrigger>
                <SelectValue placeholder="Experience Level" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Levels</SelectItem>
                <SelectItem value="Entry Level">Entry Level</SelectItem>
                <SelectItem value="Junior">Junior</SelectItem>
                <SelectItem value="Mid-Level">Mid-Level</SelectItem>
                <SelectItem value="Senior">Senior</SelectItem>
                <SelectItem value="Lead">Lead</SelectItem>
              </SelectContent>
            </Select>

            <Input
              placeholder="Location"
              value={filters.location}
              onChange={(e) => handleFilterChange('location', e.target.value)}
            />

            <Select value={filters.is_remote} onValueChange={(value) => handleFilterChange('is_remote', value)}>
              <SelectTrigger>
                <SelectValue placeholder="Remote Options" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Options</SelectItem>
                <SelectItem value="true">Remote Only</SelectItem>
                <SelectItem value="false">On-site Only</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Highlighted Job */}
        {highlightedJob && (
          <div className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">Featured Opportunity</h2>
            <JobCard job={highlightedJob} isHighlighted />
          </div>
        )}

        {/* Job List */}
        <div className="grid gap-6">
          {jobs.map((job) => (
            <JobCard key={job.id} job={job} />
          ))}
        </div>

        {hasNext && (
          <div className="flex justify-center mt-8">
            <Button onClick={loadMore} variant="outline" className="hover-glow">
              Load More Jobs
            </Button>
          </div>
        )}

        {jobs.length === 0 && (
          <div className="text-center py-12">
            <p className="text-muted-foreground text-lg">No jobs found with current filters.</p>
          </div>
        )}
      </div>
    </MainLayout>
  );
};

export default Jobs;