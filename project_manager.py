"""
Project Manager - Handle multiple manhwa projects
"""
from pathlib import Path
import json
from datetime import datetime
from typing import List, Dict, Optional
import shutil

class ManhwaProject:
    """Represents a single manhwa project"""
    
    def __init__(self, project_id: str, title: str = "Untitled"):
        self.project_id = project_id
        self.title = title
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.chapter_text = ""
        self.characters = []
        self.scenes = []
        self.generated_panels = []
        self.settings = {
            'model': 'sd15',
            'style': 'manhwa',
            'quality': 'normal',
            'max_panels': 10
        }
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'project_id': self.project_id,
            'title': self.title,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'chapter_text': self.chapter_text,
            'characters': self.characters,
            'scenes': self.scenes,
            'generated_panels': self.generated_panels,
            'settings': self.settings
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create from dictionary"""
        project = cls(data['project_id'], data.get('title', 'Untitled'))
        project.created_at = data.get('created_at', project.created_at)
        project.updated_at = data.get('updated_at', project.updated_at)
        project.chapter_text = data.get('chapter_text', '')
        project.characters = data.get('characters', [])
        project.scenes = data.get('scenes', [])
        project.generated_panels = data.get('generated_panels', [])
        project.settings = data.get('settings', project.settings)
        return project


class ProjectManager:
    """Manage multiple manhwa projects"""
    
    def __init__(self, projects_dir: str = "projects"):
        self.projects_dir = Path(projects_dir)
        self.projects_dir.mkdir(exist_ok=True)
    
    def create_project(self, title: str) -> ManhwaProject:
        """Create a new project"""
        import uuid
        project_id = str(uuid.uuid4())[:8]
        project = ManhwaProject(project_id, title)
        
        # Create project directory
        project_dir = self.projects_dir / project_id
        project_dir.mkdir(exist_ok=True)
        (project_dir / 'characters').mkdir(exist_ok=True)
        (project_dir / 'outputs').mkdir(exist_ok=True)
        
        # Save project file
        self.save_project(project)
        
        return project
    
    def save_project(self, project: ManhwaProject):
        """Save project to disk"""
        project.updated_at = datetime.now().isoformat()
        project_file = self.projects_dir / project.project_id / 'project.json'
        
        with open(project_file, 'w', encoding='utf-8') as f:
            json.dump(project.to_dict(), f, indent=2)
    
    def load_project(self, project_id: str) -> Optional[ManhwaProject]:
        """Load project from disk"""
        project_file = self.projects_dir / project_id / 'project.json'
        
        if not project_file.exists():
            return None
        
        with open(project_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return ManhwaProject.from_dict(data)
    
    def list_projects(self) -> List[Dict]:
        """List all projects"""
        projects = []
        
        for project_dir in self.projects_dir.iterdir():
            if project_dir.is_dir():
                project_file = project_dir / 'project.json'
                if project_file.exists():
                    with open(project_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        projects.append({
                            'project_id': data['project_id'],
                            'title': data.get('title', 'Untitled'),
                            'created_at': data.get('created_at', ''),
                            'updated_at': data.get('updated_at', ''),
                            'panel_count': len(data.get('generated_panels', []))
                        })
        
        # Sort by updated_at (newest first)
        projects.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
        
        return projects
    
    def delete_project(self, project_id: str) -> bool:
        """Delete a project"""
        project_dir = self.projects_dir / project_id
        
        if project_dir.exists():
            shutil.rmtree(project_dir)
            return True
        
        return False
    
    def duplicate_project(self, project_id: str, new_title: str = None) -> Optional[ManhwaProject]:
        """Duplicate an existing project"""
        original = self.load_project(project_id)
        
        if not original:
            return None
        
        # Create new project
        if new_title is None:
            new_title = f"{original.title} (Copy)"
        
        new_project = self.create_project(new_title)
        
        # Copy data
        new_project.chapter_text = original.chapter_text
        new_project.characters = original.characters.copy()
        new_project.scenes = original.scenes.copy()
        new_project.settings = original.settings.copy()
        
        self.save_project(new_project)
        
        # Copy character reference images
        old_char_dir = self.projects_dir / project_id / 'characters'
        new_char_dir = self.projects_dir / new_project.project_id / 'characters'
        
        if old_char_dir.exists():
            for img in old_char_dir.glob('*'):
                shutil.copy(img, new_char_dir / img.name)
        
        return new_project


# Global instance
project_manager = ProjectManager()


if __name__ == "__main__":
    # Test project manager
    pm = ProjectManager()
    
    # Create project
    project = pm.create_project("Test Manhwa")
    print(f"Created project: {project.project_id}")
    
    # Update project
    project.chapter_text = "Chapter 1 content..."
    project.characters.append({
        'name': 'Elena',
        'hair': 'silver',
        'eyes': 'blue'
    })
    pm.save_project(project)
    
    # List projects
    projects = pm.list_projects()
    print(f"\nProjects: {len(projects)}")
    for p in projects:
        print(f"  - {p['title']} ({p['project_id']})")
    
    # Load project
    loaded = pm.load_project(project.project_id)
    print(f"\nLoaded: {loaded.title}")
    print(f"Characters: {loaded.characters}")
