"""
Project Builder - GitHub project creation and management
"""

from typing import Dict, List, Optional
from .github_client import GitHubClient


class ProjectBuilder:
    """Build and manage GitHub projects with issues and boards"""
    
    def __init__(self, github_client: GitHubClient):
        self.client = github_client
    
    def create_labels(self, repo_name: str, labels: List[Dict]) -> List[Dict]:
        """
        Create labels in the repository
        
        Args:
            repo_name: Repository name in format 'owner/repo'
            labels: List of label dictionaries
            
        Returns:
            List of created/existing labels
        """
        
        created_labels = []
        
        for label_data in labels:
            try:
                label = self.client.create_label(
                    repo_name=repo_name,
                    name=label_data['name'],
                    color=label_data['color'],
                    description=label_data.get('description', '')
                )
                created_labels.append(label)
                
            except Exception as e:
                # Continue with other labels if one fails
                print(f"Warning: Failed to create label '{label_data['name']}': {str(e)}")
                continue
        
        return created_labels
    
    def create_issues(self, repo_name: str, tasks: List[Dict]) -> List[Dict]:
        """
        Create GitHub issues from tasks
        
        Args:
            repo_name: Repository name in format 'owner/repo'
            tasks: List of task dictionaries
            
        Returns:
            List of created issues
        """
        
        created_issues = []
        
        for task in tasks:
            try:
                # Build issue body
                body = self._build_issue_body(task)
                
                # Prepare labels
                labels = self._prepare_issue_labels(task)
                
                # Create the issue
                issue = self.client.create_issue(
                    repo_name=repo_name,
                    title=task['title'],
                    body=body,
                    labels=labels
                )
                
                # Add task metadata to issue for later use
                issue.update({
                    'priority': task.get('priority', 'medium'),
                    'effort': task.get('effort', '3-days'),
                    'phase': task.get('phase', 'Development'),
                    'task_type': task.get('type', 'feature')
                })
                
                created_issues.append(issue)
                
            except Exception as e:
                print(f"Warning: Failed to create issue '{task['title']}': {str(e)}")
                continue
        
        return created_issues
    
    def create_project_board(self, repo_name: str, project_name: str, 
                           issues: List[Dict]) -> Optional[str]:
        """
        Create a GitHub Projects v2 board and add issues to it
        
        Args:
            repo_name: Repository name in format 'owner/repo'
            project_name: Name for the project board
            issues: List of created issues
            
        Returns:
            Project URL if successful, None otherwise
        """
        
        try:
            # Get owner ID
            owner_id = self.client.get_repository_owner_id(repo_name)
            
            # Create project
            project = self.client.create_project_v2(
                owner_id=owner_id,
                title=project_name,
                description=f"Auto-generated project board for {repo_name}"
            )
            
            # Add issues to project
            added_count = 0
            for issue in issues:
                try:
                    result = self.client.add_issue_to_project(
                        project_id=project['id'],
                        issue_id=issue['node_id']
                    )
                    if result and 'id' in result:
                        added_count += 1
                except Exception as e:
                    print(f"Warning: Failed to add issue to project: {str(e)}")
            
            print(f"Added {added_count}/{len(issues)} issues to project board")
            return project['url']
            
        except Exception as e:
            raise Exception(f"Failed to create project board: {str(e)}")
    
    def _build_issue_body(self, task: Dict) -> str:
        """Build the issue body from task data"""
        
        body_parts = []
        
        # Add description
        if task.get('description'):
            body_parts.append(task['description'])
            body_parts.append("")
        
        # Add metadata section
        metadata = []
        metadata.append("## 📋 Task Details")
        metadata.append("")
        
        # Phase
        if task.get('phase'):
            metadata.append(f"**Phase:** {task['phase']}")
        
        # Priority
        priority = task.get('priority', 'medium')
        priority_emoji = {
            'high': '🔴',
            'medium': '🟡', 
            'low': '⚪'
        }.get(priority, '🟡')
        metadata.append(f"**Priority:** {priority_emoji} {priority.title()}")
        
        # Effort estimate
        effort = task.get('effort', '3-days')
        effort_emoji = {
            '1-day': '⚡',
            '3-days': '🔨',
            '1-week': '📅',
            '2-weeks': '📆'
        }.get(effort, '🔨')
        metadata.append(f"**Estimated Effort:** {effort_emoji} {effort}")
        
        # Task type
        task_type = task.get('type', 'feature')
        type_emoji = {
            'feature': '✨',
            'bug': '🐛',
            'documentation': '📝',
            'testing': '🧪',
            'devops': '⚙️',
            'research': '🔬'
        }.get(task_type, '✨')
        metadata.append(f"**Type:** {type_emoji} {task_type.title()}")
        
        body_parts.extend(metadata)
        
        # Add dependencies if any
        if task.get('dependencies'):
            body_parts.append("")
            body_parts.append("## 🔗 Dependencies")
            body_parts.append("")
            for dep in task['dependencies']:
                body_parts.append(f"- [ ] {dep}")
        
        # Add acceptance criteria template
        body_parts.extend([
            "",
            "## ✅ Acceptance Criteria",
            "",
            "- [ ] Task objective is clearly defined",
            "- [ ] Implementation meets requirements",
            "- [ ] Code is properly tested",
            "- [ ] Documentation is updated (if needed)",
            "",
            "---",
            "*This issue was automatically generated by Universal Project Todo Tracker*"
        ])
        
        return "\n".join(body_parts)
    
    def _prepare_issue_labels(self, task: Dict) -> List[str]:
        """Prepare labels for the issue"""
        
        labels = []
        
        # Add priority label
        priority = task.get('priority', 'medium')
        labels.append(f"priority:{priority}")
        
        # Add effort label
        effort = task.get('effort', '3-days')
        labels.append(f"effort:{effort}")
        
        # Add phase label
        phase = task.get('phase', '').lower().replace(' ', '-')
        if phase:
            labels.append(f"phase:{phase}")
        
        # Add type label
        task_type = task.get('type', 'feature')
        labels.append(f"type:{task_type}")
        
        # Add custom labels from task
        if task.get('labels'):
            labels.extend(task['labels'])
        
        return labels
    
    def get_project_summary(self, repo_name: str) -> Dict:
        """Get a summary of the project state"""
        
        try:
            # Get repository info
            repo = self.client.get_repository(repo_name)
            if not repo:
                return {"error": "Repository not found"}
            
            # Get issues and labels
            issues = self.client.list_repository_issues(repo_name)
            labels = self.client.list_repository_labels(repo_name)
            
            # Count by priority
            priority_counts = {'high': 0, 'medium': 0, 'low': 0}
            for issue in issues:
                for label in issue.get('labels', []):
                    if label['name'].startswith('priority:'):
                        priority = label['name'].split(':')[1]
                        if priority in priority_counts:
                            priority_counts[priority] += 1
            
            # Count by phase
            phase_counts = {}
            for issue in issues:
                for label in issue.get('labels', []):
                    if label['name'].startswith('phase:'):
                        phase = label['name'].split(':')[1]
                        phase_counts[phase] = phase_counts.get(phase, 0) + 1
            
            return {
                "repository": repo.full_name,
                "total_issues": len(issues),
                "total_labels": len(labels),
                "priority_breakdown": priority_counts,
                "phase_breakdown": phase_counts,
                "open_issues": len([i for i in issues if i['state'] == 'open']),
                "closed_issues": len([i for i in issues if i['state'] == 'closed'])
            }
            
        except Exception as e:
            return {"error": str(e)}
