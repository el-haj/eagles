from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from learnings.models import Track, LearningPath, LearningSection
from django.core.files.base import ContentFile
import tempfile
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample learning data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample learning data...')
        
        # Create sample tracks
        self.create_sample_tracks()
        
        # Create sample learning paths
        self.create_sample_learning_paths()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created sample learning data!')
        )

    def create_sample_tracks(self):
        """Create sample tracks"""
        tracks_data = [
            {
                'title': 'Introduction to Cybersecurity',
                'description': 'Comprehensive guide to cybersecurity fundamentals covering network security, threat analysis, and basic defense mechanisms.',
                'category': 'cyber',
                'level': 'beginner',
                'tags': ['security', 'fundamentals', 'networking'],
                'duration_hours': 8,
                'prerequisites': 'Basic computer knowledge',
            },
            {
                'title': 'Advanced Penetration Testing',
                'description': 'Deep dive into penetration testing methodologies, tools, and advanced attack techniques.',
                'category': 'cyber',
                'level': 'advanced',
                'tags': ['pentesting', 'security', 'hacking'],
                'duration_hours': 16,
                'prerequisites': 'Basic cybersecurity knowledge, networking fundamentals',
            },
            {
                'title': 'Cloud Infrastructure Basics',
                'description': 'Learn the fundamentals of cloud computing, AWS services, and infrastructure management.',
                'category': 'infrastructure',
                'level': 'beginner',
                'tags': ['cloud', 'aws', 'infrastructure'],
                'duration_hours': 12,
                'prerequisites': 'Basic IT knowledge',
            },
            {
                'title': 'Python Programming Fundamentals',
                'description': 'Complete guide to Python programming from basics to intermediate concepts.',
                'category': 'software_engineering',
                'level': 'beginner',
                'tags': ['python', 'programming', 'development'],
                'duration_hours': 20,
                'prerequisites': 'No programming experience required',
            },
            {
                'title': 'DevOps and CI/CD Pipelines',
                'description': 'Master DevOps practices, continuous integration, and deployment pipelines.',
                'category': 'infrastructure',
                'level': 'intermediate',
                'tags': ['devops', 'cicd', 'automation'],
                'duration_hours': 15,
                'prerequisites': 'Basic Linux knowledge, understanding of software development',
            }
        ]
        
        for track_data in tracks_data:
            # Create a dummy PDF file
            pdf_content = f"Sample PDF content for {track_data['title']}"
            pdf_file = ContentFile(pdf_content.encode(), name=f"{track_data['title'].lower().replace(' ', '_')}.pdf")
            
            track, created = Track.objects.get_or_create(
                title=track_data['title'],
                defaults={
                    **track_data,
                    'pdf_file': pdf_file,
                }
            )
            
            if created:
                self.stdout.write(f'Created track: {track.title}')
            else:
                self.stdout.write(f'Track already exists: {track.title}')

    def create_sample_learning_paths(self):
        """Create sample learning paths"""
        # Get or create a user for instructor
        instructor, created = User.objects.get_or_create(
            username='instructor',
            defaults={
                'email': 'instructor@example.com',
                'first_name': 'John',
                'last_name': 'Instructor'
            }
        )
        
        learning_paths_data = [
            {
                'title': 'Complete Cybersecurity Bootcamp',
                'description': 'Comprehensive cybersecurity training covering all essential topics from basics to advanced techniques.',
                'short_description': 'Master cybersecurity from fundamentals to advanced practices',
                'category': 'cyber',
                'level': 'intermediate',
                'estimated_duration_hours': 40,
                'prerequisites': 'Basic computer knowledge',
                'learning_objectives': [
                    'Understand cybersecurity fundamentals',
                    'Learn threat analysis and risk assessment',
                    'Master security tools and techniques',
                    'Implement security best practices'
                ],
                'tags': ['cybersecurity', 'security', 'bootcamp'],
                'status': 'published',
                'sections': [
                    {
                        'title': 'Introduction to Cybersecurity',
                        'description': 'Overview of cybersecurity landscape and fundamentals',
                        'content_type': 'video',
                        'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                        'estimated_duration_minutes': 45,
                        'order': 1
                    },
                    {
                        'title': 'Network Security Basics',
                        'description': 'Understanding network protocols and security measures',
                        'content_type': 'markdown',
                        'markdown_content': '# Network Security\n\nNetwork security involves protecting networks and their services...',
                        'estimated_duration_minutes': 60,
                        'order': 2
                    },
                    {
                        'title': 'Security Assessment Tools',
                        'description': 'Hands-on with security assessment tools',
                        'content_type': 'pdf',
                        'estimated_duration_minutes': 90,
                        'order': 3
                    }
                ]
            },
            {
                'title': 'Full Stack Web Development',
                'description': 'Complete web development course covering frontend, backend, and deployment.',
                'short_description': 'Learn full stack web development with modern technologies',
                'category': 'software_engineering',
                'level': 'intermediate',
                'estimated_duration_hours': 60,
                'prerequisites': 'Basic programming knowledge',
                'learning_objectives': [
                    'Build responsive web applications',
                    'Master frontend and backend development',
                    'Learn database design and management',
                    'Deploy applications to production'
                ],
                'tags': ['web development', 'fullstack', 'javascript'],
                'status': 'published',
                'sections': [
                    {
                        'title': 'HTML & CSS Fundamentals',
                        'description': 'Building blocks of web development',
                        'content_type': 'video',
                        'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                        'estimated_duration_minutes': 120,
                        'order': 1
                    },
                    {
                        'title': 'JavaScript Essentials',
                        'description': 'Core JavaScript concepts and ES6+ features',
                        'content_type': 'markdown',
                        'markdown_content': '# JavaScript Essentials\n\nJavaScript is the programming language of the web...',
                        'estimated_duration_minutes': 180,
                        'order': 2
                    }
                ]
            }
        ]
        
        for path_data in learning_paths_data:
            sections_data = path_data.pop('sections', [])
            
            learning_path, created = LearningPath.objects.get_or_create(
                title=path_data['title'],
                defaults={
                    **path_data,
                    'instructor': instructor,
                }
            )
            
            if created:
                self.stdout.write(f'Created learning path: {learning_path.title}')
                
                # Create sections
                for section_data in sections_data:
                    # Create dummy PDF if needed
                    if section_data['content_type'] == 'pdf':
                        pdf_content = f"Sample PDF content for {section_data['title']}"
                        pdf_file = ContentFile(pdf_content.encode(), name=f"{section_data['title'].lower().replace(' ', '_')}.pdf")
                        section_data['pdf_file'] = pdf_file
                    
                    section = LearningSection.objects.create(
                        learning_path=learning_path,
                        **section_data
                    )
                    self.stdout.write(f'  Created section: {section.title}')
            else:
                self.stdout.write(f'Learning path already exists: {learning_path.title}')
