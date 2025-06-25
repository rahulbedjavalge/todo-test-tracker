"""
Task Parser - AI-powered project analysis and task extraction
"""

import json
import re
from typing import Dict, List, Optional
from .openrouter_client import OpenRouterClient


class TaskParser:
    """Parse project descriptions into structured tasks using AI"""
    
    def __init__(self, openrouter_client: OpenRouterClient):
        self.client = openrouter_client
        
    def parse_project(self, project_description: str, 
                     model: str = "deepseek/deepseek-r1-distill-llama-70b",
                     max_tasks: int = 12) -> Dict:
        """
        Parse a project description into structured tasks, phases, and labels
        
        Args:
            project_description: Raw project description text
            model: AI model to use for parsing
            max_tasks: Maximum number of tasks to generate
            
        Returns:
            Structured project data with tasks, labels, phases, etc.
        """
        
        prompt = self._build_extraction_prompt(project_description, max_tasks)
        
        try:
            parsed_data = self.client.extract_structured_data(
                prompt=prompt,
                model=model,
                response_format="json"
            )
            
            # Validate and clean the parsed data
            return self._validate_and_clean_data(parsed_data)
            
        except Exception as e:
            raise Exception(f"Failed to parse project: {str(e)}")
    
    def _build_extraction_prompt(self, description: str, max_tasks: int) -> str:
        """Build the prompt for task extraction"""
        
        return f"""
Analyze this project description and extract structured information for GitHub project management.

PROJECT DESCRIPTION:
{description}

Extract the following information in JSON format:

{{
    "project_name": "Concise project name (max 50 chars)",
    "project_summary": "Brief 1-2 sentence summary",
    "phases": [
        {{
            "name": "Phase name",
            "description": "Phase description",
            "order": 1
        }}
    ],
    "tasks": [
        {{
            "title": "Clear, actionable task title",
            "description": "Detailed task description with acceptance criteria",
            "phase": "Phase name this task belongs to",
            "priority": "high|medium|low",
            "effort": "1-day|3-days|1-week|2-weeks",
            "labels": ["label1", "label2"],
            "dependencies": ["task_title_dependency"],
            "type": "feature|bug|documentation|testing|devops|research"
        }}
    ],
    "labels": [
        {{
            "name": "label-name",
            "color": "hex-color-without-hash",
            "description": "Label description"
        }}
    ]
}}

REQUIREMENTS:
1. Generate maximum {max_tasks} tasks
2. Create logical phases (planning, development, testing, deployment, etc.)
3. Assign realistic effort estimates
4. Include comprehensive labels for:
   - Phases (phase:planning, phase:backend, etc.)
   - Priorities (priority:high, priority:medium, priority:low)
   - Effort levels (effort:1-day, effort:3-days, etc.)
   - Task types (type:feature, type:bug, etc.)
   - Technology-specific labels
5. Use semantic colors for labels:
   - Red (ff0000) for high priority/critical
   - Orange (ffa500) for medium priority/warnings
   - Green (00ff00) for completed/success
   - Blue (0000ff) for features/information
   - Purple (800080) for enhancement/nice-to-have
   - Gray (808080) for low priority/maintenance
6. Make tasks specific and actionable
7. Include dependencies where logical
8. Ensure tasks cover the full project lifecycle

Focus on creating a realistic, well-organized project structure that a development team could immediately start working on.
"""
    
    def _validate_and_clean_data(self, data: Dict) -> Dict:
        """Validate and clean the parsed project data"""
        
        # Ensure required fields exist
        required_fields = ['project_name', 'tasks', 'labels']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Clean project name
        data['project_name'] = self._clean_project_name(data['project_name'])
        
        # Validate and clean tasks
        data['tasks'] = self._validate_tasks(data['tasks'])
        
        # Validate and clean labels
        data['labels'] = self._validate_labels(data['labels'])
        
        # Add default phases if missing
        if 'phases' not in data or not data['phases']:
            data['phases'] = self._generate_default_phases()
        
        # Add summary if missing
        if 'project_summary' not in data:
            data['project_summary'] = f"A software project: {data['project_name']}"
        
        return data
    
    def _clean_project_name(self, name: str) -> str:
        """Clean and validate project name"""
        if not name:
            return "Untitled Project"
        
        # Remove special characters, limit length
        cleaned = re.sub(r'[^\w\s-]', '', name.strip())
        return cleaned[:50]
    
    def _validate_tasks(self, tasks: List[Dict]) -> List[Dict]:
        """Validate and clean task data"""
        
        valid_tasks = []
        
        for task in tasks:
            if not isinstance(task, dict):
                continue
                
            # Required fields
            if 'title' not in task or not task['title']:
                continue
            
            cleaned_task = {
                'title': str(task['title']).strip()[:100],
                'description': str(task.get('description', '')).strip(),
                'phase': str(task.get('phase', 'Development')).strip(),
                'priority': self._validate_priority(task.get('priority', 'medium')),
                'effort': self._validate_effort(task.get('effort', '3-days')),
                'labels': self._validate_task_labels(task.get('labels', [])),
                'dependencies': task.get('dependencies', []),
                'type': self._validate_task_type(task.get('type', 'feature'))
            }
            
            valid_tasks.append(cleaned_task)
        
        return valid_tasks
    
    def _validate_labels(self, labels: List[Dict]) -> List[Dict]:
        """Validate and clean label data"""
        
        valid_labels = []
        seen_names = set()
        
        for label in labels:
            if not isinstance(label, dict):
                continue
                
            name = label.get('name', '').strip()
            if not name or name in seen_names:
                continue
            
            seen_names.add(name)
            
            cleaned_label = {
                'name': name,
                'color': self._validate_color(label.get('color', '808080')),
                'description': str(label.get('description', '')).strip()[:100]
            }
            
            valid_labels.append(cleaned_label)
        
        # Add essential labels if missing
        essential_labels = [
            {'name': 'priority:high', 'color': 'ff0000', 'description': 'High priority task'},
            {'name': 'priority:medium', 'color': 'ffa500', 'description': 'Medium priority task'},
            {'name': 'priority:low', 'color': '808080', 'description': 'Low priority task'},
        ]
        
        existing_names = {label['name'] for label in valid_labels}
        for essential in essential_labels:
            if essential['name'] not in existing_names:
                valid_labels.append(essential)
        
        return valid_labels
    
    def _validate_priority(self, priority: str) -> str:
        """Validate task priority"""
        valid_priorities = ['high', 'medium', 'low']
        priority = str(priority).lower().strip()
        return priority if priority in valid_priorities else 'medium'
    
    def _validate_effort(self, effort: str) -> str:
        """Validate task effort estimate"""
        valid_efforts = ['1-day', '3-days', '1-week', '2-weeks']
        effort = str(effort).lower().strip()
        return effort if effort in valid_efforts else '3-days'
    
    def _validate_task_type(self, task_type: str) -> str:
        """Validate task type"""
        valid_types = ['feature', 'bug', 'documentation', 'testing', 'devops', 'research']
        task_type = str(task_type).lower().strip()
        return task_type if task_type in valid_types else 'feature'
    
    def _validate_task_labels(self, labels: List) -> List[str]:
        """Validate task labels"""
        if not isinstance(labels, list):
            return []
        
        return [str(label).strip() for label in labels if str(label).strip()]
    
    def _validate_color(self, color: str) -> str:
        """Validate hex color"""
        color = str(color).strip().lower()
        
        # Remove # if present
        if color.startswith('#'):
            color = color[1:]
        
        # Check if valid hex
        if re.match(r'^[0-9a-f]{6}$', color):
            return color
        
        # Return default gray if invalid
        return '808080'
    
    def _generate_default_phases(self) -> List[Dict]:
        """Generate default project phases"""
        return [
            {
                "name": "Planning",
                "description": "Project planning and requirements gathering",
                "order": 1
            },
            {
                "name": "Development", 
                "description": "Core development and implementation",
                "order": 2
            },
            {
                "name": "Testing",
                "description": "Testing and quality assurance",
                "order": 3
            },
            {
                "name": "Deployment",
                "description": "Deployment and release preparation",
                "order": 4
            }
        ]
