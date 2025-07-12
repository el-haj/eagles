import React, { useState, useEffect } from 'react';
import { API_BASE_URL } from '@/lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { Button } from '@/components/ui/button';
import { ChevronDown, ChevronRight, ExternalLink, FileText } from 'lucide-react';
import BinaryLoader from '@/components/common/BinaryLoader';
import MainLayout from '@/components/layout/MainLayout';

interface DocumentationItem {
  id: number;
  title: string;
  name: string;
  description: string;
}

interface DocumentationLink {
  name: string;
  url: string;
}

interface DocumentationDetail {
  id: number;
  title: string;
  category: string;
  main_markdown: string;
  links: DocumentationLink[];
  meta_data: any;
  created_at: string;
  updated_at: string;
}

interface AccordionData {
  [category: string]: DocumentationItem[];
}

const Docs = () => {
  const [accordionData, setAccordionData] = useState<AccordionData>({});
  const [selectedDoc, setSelectedDoc] = useState<DocumentationDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [docLoading, setDocLoading] = useState(false);
  const [openCategories, setOpenCategories] = useState<Set<string>>(new Set());

  const fetchAccordionData = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/documentations/accordion/`);

      if (response.ok) {
        const data = await response.json();
        setAccordionData(data);
      }
    } catch (error) {
      console.error('Error fetching documentation accordion:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchDocumentation = async (docId: number) => {
    setDocLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/documentations/${docId}/markdown/`);

      if (response.ok) {
        const data = await response.json();
        setSelectedDoc(data);
      }
    } catch (error) {
      console.error('Error fetching documentation:', error);
    } finally {
      setDocLoading(false);
    }
  };

  const toggleCategory = (category: string) => {
    const newOpenCategories = new Set(openCategories);
    if (newOpenCategories.has(category)) {
      newOpenCategories.delete(category);
    } else {
      newOpenCategories.add(category);
    }
    setOpenCategories(newOpenCategories);
  };

  useEffect(() => {
    fetchAccordionData();
  }, []);

  if (loading) {
    return <BinaryLoader fullScreen message="Loading documentation..." />;
  }

  if (selectedDoc) {
    return (
      <MainLayout>
        <div className="container mx-auto px-4 py-8">
          <div className="mb-6">
            <Button 
              variant="outline" 
              onClick={() => setSelectedDoc(null)}
              className="mb-4"
            >
              ← Back to Documentation
            </Button>
            
            <h1 className="text-4xl font-bold text-gradient mb-4 glitch" data-text={selectedDoc.title}>
              {selectedDoc.title}
            </h1>
            <p className="text-muted-foreground">
              Category: {selectedDoc.category}
            </p>
          </div>

          {docLoading ? (
            <div className="flex justify-center py-12">
              <BinaryLoader message="Loading content..." />
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
              <div className="lg:col-span-3">
                <Card className="cyber-card">
                  <CardContent className="p-6">
                    <div className="prose prose-sm dark:prose-invert max-w-none">
                      <div dangerouslySetInnerHTML={{ __html: selectedDoc.main_markdown }} />
                    </div>
                  </CardContent>
                </Card>
              </div>

              {selectedDoc.links.length > 0 && (
                <div className="lg:col-span-1">
                  <Card className="cyber-card sticky top-8">
                    <CardHeader>
                      <CardTitle className="text-lg">External Resources</CardTitle>
                      <CardDescription>
                        Additional links and references
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {selectedDoc.links.map((link, index) => (
                          <Button
                            key={index}
                            variant="outline"
                            size="sm"
                            className="w-full justify-start h-auto p-3"
                            asChild
                          >
                            <a 
                              href={link.url} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              className="flex items-start gap-2"
                            >
                              <ExternalLink className="w-4 h-4 mt-0.5 flex-shrink-0" />
                              <span className="text-left text-wrap">{link.name}</span>
                            </a>
                          </Button>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              )}
            </div>
          )}
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gradient mb-4 glitch" data-text="Documentation">
            Documentation
          </h1>
          <p className="text-muted-foreground text-lg">
            Comprehensive guides and resources for cybersecurity professionals
          </p>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Accordion Sidebar */}
          <div className="lg:col-span-1 sticky top-8 h-fit max-h-[80vh] overflow-y-auto">
            <div className="space-y-4">
              {Object.entries(accordionData).map(([category, docs]) => (
                <Card key={category} className="cyber-card">
                  <Collapsible 
                    open={openCategories.has(category)}
                    onOpenChange={() => toggleCategory(category)}
                  >
                    <CollapsibleTrigger asChild>
                      <CardHeader className="hover:bg-accent/50 transition-colors cursor-pointer">
                        <div className="flex items-center justify-between">
                          <CardTitle className="text-xl">{category}</CardTitle>
                          <div className="flex items-center gap-2">
                            <span className="text-sm text-muted-foreground">
                              {docs.length} {docs.length === 1 ? 'document' : 'documents'}
                            </span>
                            {openCategories.has(category) ? (
                              <ChevronDown className="w-5 h-5" />
                            ) : (
                              <ChevronRight className="w-5 h-5" />
                            )}
                          </div>
                        </div>
                      </CardHeader>
                    </CollapsibleTrigger>
                    <CollapsibleContent>
                      <CardContent className="pt-0">
                        <div className="grid gap-3">
                          {docs.map((doc) => (
                            <div
                              key={doc.id}
                              className={`flex items-center justify-between p-4 border border-border rounded-md hover:bg-accent/30 transition-colors cursor-pointer ${selectedDoc && selectedDoc.id === doc.id ? 'bg-accent/50' : ''}`}
                              onClick={() => fetchDocumentation(doc.id)}
                            >
                              <div className="flex items-start gap-3">
                                <FileText className="w-5 h-5 text-secondary mt-1 flex-shrink-0" />
                                <div>
                                  <h3 className="font-semibold text-base">{doc.title}</h3>
                                  <p className="text-sm text-muted-foreground mt-1">
                                    {doc.description}
                                  </p>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </CollapsibleContent>
                  </Collapsible>
                </Card>
              ))}
            </div>
          </div>
          {/* Main Content */}
          <div className="lg:col-span-3">
            {docLoading ? (
              <div className="flex justify-center py-12">
                <BinaryLoader message="Loading content..." />
              </div>
            ) : selectedDoc ? (
              <Card className="cyber-card">
                <CardHeader>
                  <CardTitle className="text-2xl">{selectedDoc.title}</CardTitle>
                  <CardDescription>Category: {selectedDoc.category}</CardDescription>
                </CardHeader>
                <CardContent className="p-6">
                  <div className="prose prose-sm dark:prose-invert max-w-none mb-4">
                    <div dangerouslySetInnerHTML={{ __html: selectedDoc.main_markdown }} />
                  </div>
                  {selectedDoc.links.length > 0 && (
                    <div className="mt-6">
                      <h3 className="font-semibold mb-2">External Resources</h3>
                      <div className="space-y-2">
                        {selectedDoc.links.map((link, index) => (
                          <Button
                            key={index}
                            variant="outline"
                            size="sm"
                            className="w-full justify-start h-auto p-3"
                            asChild
                          >
                            <a 
                              href={link.url} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              className="flex items-start gap-2"
                            >
                              <ExternalLink className="w-4 h-4 mt-0.5 flex-shrink-0" />
                              <span className="text-left text-wrap">{link.name}</span>
                            </a>
                          </Button>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            ) : (
              <div className="flex items-center justify-center h-full text-muted-foreground">
                <span>Select a document from the left to view its content.</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default Docs;