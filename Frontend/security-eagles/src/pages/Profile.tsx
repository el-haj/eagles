import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { User, Mail, Phone, MapPin, Github, Linkedin, Globe, Upload, Award } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/hooks/use-toast';
import BinaryLoader from '@/components/common/BinaryLoader';
import MainLayout from '@/components/layout/MainLayout';

interface ProfileData {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  sso_provider: string | null;
  sso_id: string | null;
  score: number;
  cv: string;
  profile_pic: string;
  github: string;
  linkedin: string;
  portfolio_url: string;
  phone: string;
  city: string;
  type: string;
  is_active: boolean;
  created_by: number | null;
  created_at: string;
  updated_at: string;
  meta_data: any;
}

const Profile = () => {
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [formData, setFormData] = useState<Partial<ProfileData>>({});
  const { token, user, updateUser } = useAuth();
  const { toast } = useToast();

  const { API_BASE_URL } = require('@/lib/api');
  const fetchProfile = async () => {
    if (!token) {
      console.warn('No token found. User is not authenticated.');
      setLoading(false);
      return;
    }

    try {
      console.log('Using token:', token);
      const response = await fetch(`${API_BASE_URL}/users/profile/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setProfile(data);
        setFormData(data);
      } else if (response.status === 401) {
        console.warn('Unauthorized: Invalid or expired token.');
      }
    } catch (error) {
      console.error('Error fetching profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSave = async () => {
    if (!token) return;

    setSaving(true);
    try {
      const response = await fetch(`${API_BASE_URL}/users/profile/`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        const updatedProfile = await response.json();
        setProfile(updatedProfile);
        updateUser(updatedProfile);
        setEditMode(false);
        toast({
          title: "Profile updated!",
          description: "Your profile has been successfully updated.",
        });
      } else {
        throw new Error('Update failed');
      }
    } catch (error) {
      toast({
        title: "Update failed",
        description: "An error occurred while updating your profile.",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  const handleFileUpload = async (file: File, type: 'profile_pic' | 'cv') => {
    if (!token) return;

    const formData = new FormData();
    formData.append(type, file);

    try {
      const endpoint = type === 'profile_pic' ? 'upload-pic' : 'upload-cv';
      const response = await fetch(`${API_BASE_URL}/users/profile/${endpoint}/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setProfile(prev => prev ? { ...prev, [type]: data[type] } : null);
        updateUser({ [type]: data[type] });
        toast({
          title: `${type === 'profile_pic' ? 'Profile picture' : 'CV'} updated!`,
          description: "Your file has been uploaded successfully.",
        });
      }
    } catch (error) {
      toast({
        title: "Upload failed",
        description: "An error occurred while uploading the file.",
        variant: "destructive",
      });
    }
  };

  useEffect(() => {
    fetchProfile();
  }, [token]);

  if (loading) {
    return <BinaryLoader fullScreen message="Loading profile..." />;
  }

  if (!profile) {
    return (
      <MainLayout>
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <p className="text-muted-foreground">Profile not found.</p>
          </div>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gradient mb-4 glitch" data-text="Profile">
            Profile
          </h1>
          <p className="text-muted-foreground text-lg">
            Manage your Security Eagles profile and information
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Profile Overview */}
          <div className="lg:col-span-1">
            <Card className="cyber-card">
              <CardContent className="p-6 text-center">
                <div className="relative inline-block mb-4">
                  <Avatar className="w-24 h-24">
                    <AvatarImage 
                      src={profile.profile_pic ? `https://api.securityeagles.com${profile.profile_pic}` : undefined} 
                      alt="Profile picture" 
                    />
                    <AvatarFallback className="bg-primary text-primary-foreground text-2xl">
                      {profile.first_name?.[0]?.toUpperCase() || profile.username?.[0]?.toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  <label className="absolute bottom-0 right-0 bg-secondary text-secondary-foreground rounded-full p-2 cursor-pointer hover:bg-secondary/80 transition-colors">
                    <Upload className="w-4 h-4" />
                    <input
                      type="file"
                      accept="image/*"
                      className="hidden"
                      onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0], 'profile_pic')}
                    />
                  </label>
                </div>
                
                <h2 className="text-2xl font-bold mb-2">
                  {profile.first_name} {profile.last_name}
                </h2>
                <p className="text-muted-foreground mb-4">@{profile.username}</p>
                
                <div className="flex items-center justify-center gap-2 mb-4">
                  <Award className="w-5 h-5 text-secondary" />
                  <span className="text-xl font-semibold text-secondary">{profile.score}</span>
                  <span className="text-sm text-muted-foreground">points</span>
                </div>

                <Badge variant={profile.type === 'public' ? 'default' : 'secondary'}>
                  {profile.type} Profile
                </Badge>
              </CardContent>
            </Card>

            {/* Quick Links */}
            <Card className="cyber-card mt-6">
              <CardHeader>
                <CardTitle>Quick Links</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {profile.github && (
                  <Button variant="outline" size="sm" className="w-full justify-start" asChild>
                    <a href={profile.github} target="_blank" rel="noopener noreferrer">
                      <Github className="w-4 h-4 mr-2" />
                      GitHub
                    </a>
                  </Button>
                )}
                {profile.linkedin && (
                  <Button variant="outline" size="sm" className="w-full justify-start" asChild>
                    <a href={profile.linkedin} target="_blank" rel="noopener noreferrer">
                      <Linkedin className="w-4 h-4 mr-2" />
                      LinkedIn
                    </a>
                  </Button>
                )}
                {profile.portfolio_url && (
                  <Button variant="outline" size="sm" className="w-full justify-start" asChild>
                    <a href={profile.portfolio_url} target="_blank" rel="noopener noreferrer">
                      <Globe className="w-4 h-4 mr-2" />
                      Portfolio
                    </a>
                  </Button>
                )}
                {profile.cv && (
                  <Button variant="outline" size="sm" className="w-full justify-start" asChild>
                    <a href={`${API_BASE_URL}${profile.cv}`} target="_blank" rel="noopener noreferrer">
                      <User className="w-4 h-4 mr-2" />
                      Download CV
                    </a>
                  </Button>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Profile Details */}
          <div className="lg:col-span-2">
            <Tabs defaultValue="personal" className="space-y-6">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="personal">Personal Info</TabsTrigger>
                <TabsTrigger value="professional">Professional</TabsTrigger>
              </TabsList>

              <TabsContent value="personal">
                <Card className="cyber-card">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle>Personal Information</CardTitle>
                        <CardDescription>
                          Manage your personal details and contact information
                        </CardDescription>
                      </div>
                      <Button
                        onClick={() => editMode ? handleSave() : setEditMode(true)}
                        disabled={saving}
                        className="hover-glow"
                      >
                        {saving ? "Saving..." : editMode ? "Save Changes" : "Edit Profile"}
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="first_name">First Name</Label>
                        <Input
                          id="first_name"
                          value={editMode ? formData.first_name || '' : profile.first_name}
                          onChange={(e) => handleInputChange('first_name', e.target.value)}
                          disabled={!editMode}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="last_name">Last Name</Label>
                        <Input
                          id="last_name"
                          value={editMode ? formData.last_name || '' : profile.last_name}
                          onChange={(e) => handleInputChange('last_name', e.target.value)}
                          disabled={!editMode}
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="email">Email</Label>
                      <Input
                        id="email"
                        value={profile.email}
                        disabled
                        className="bg-muted"
                      />
                      <p className="text-xs text-muted-foreground">
                        Email cannot be changed from this interface
                      </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="phone">Phone</Label>
                        <Input
                          id="phone"
                          value={editMode ? formData.phone || '' : profile.phone}
                          onChange={(e) => handleInputChange('phone', e.target.value)}
                          disabled={!editMode}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="city">City</Label>
                        <Input
                          id="city"
                          value={editMode ? formData.city || '' : profile.city}
                          onChange={(e) => handleInputChange('city', e.target.value)}
                          disabled={!editMode}
                        />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="professional">
                <Card className="cyber-card">
                  <CardHeader>
                    <CardTitle>Professional Information</CardTitle>
                    <CardDescription>
                      Manage your professional profiles and documents
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="space-y-2">
                      <Label htmlFor="github">GitHub Profile</Label>
                      <Input
                        id="github"
                        value={editMode ? formData.github || '' : profile.github}
                        onChange={(e) => handleInputChange('github', e.target.value)}
                        disabled={!editMode}
                        placeholder="https://github.com/username"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="linkedin">LinkedIn Profile</Label>
                      <Input
                        id="linkedin"
                        value={editMode ? formData.linkedin || '' : profile.linkedin}
                        onChange={(e) => handleInputChange('linkedin', e.target.value)}
                        disabled={!editMode}
                        placeholder="https://linkedin.com/in/username"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="portfolio_url">Portfolio URL</Label>
                      <Input
                        id="portfolio_url"
                        value={editMode ? formData.portfolio_url || '' : profile.portfolio_url}
                        onChange={(e) => handleInputChange('portfolio_url', e.target.value)}
                        disabled={!editMode}
                        placeholder="https://yourportfolio.com"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label>CV/Resume</Label>
                      <div className="flex items-center gap-2">
                        {profile.cv ? (
                          <Button variant="outline" size="sm" asChild>
                            <a href={`${API_BASE_URL}${profile.cv}`} target="_blank" rel="noopener noreferrer">
                              View Current CV
                            </a>
                          </Button>
                        ) : (
                          <p className="text-sm text-muted-foreground">No CV uploaded</p>
                        )}
                        <label className="cursor-pointer">
                          <Button variant="secondary" size="sm" asChild>
                            <span>
                              <Upload className="w-4 h-4 mr-2" />
                              Upload CV
                            </span>
                          </Button>
                          <input
                            type="file"
                            accept=".pdf,.doc,.docx"
                            className="hidden"
                            onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0], 'cv')}
                          />
                        </label>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default Profile;