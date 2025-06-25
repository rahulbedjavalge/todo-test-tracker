"""
GitHub API Client for repository and project management
"""

import requests
import json
import base64
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from urllib.parse import quote


@dataclass
class GitHubRepository:
    """GitHub repository information"""
    name: str
    full_name: str
    owner: str
    url: str
    default_branch: str
    private: bool


class GitHubClient:
    """Client for interacting with GitHub API"""
    
    def __init__(self, token: str, base_url: str = "https://api.github.com"):
        self.token = token
        self.base_url = base_url
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Universal-Project-Todo-Tracker"
        }
        
        # GraphQL endpoint for Projects v2
        self.graphql_url = "https://api.github.com/graphql"
        self.graphql_headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def get_repository(self, repo_name: str) -> Optional[GitHubRepository]:
        """
        Get repository information
        
        Args:
            repo_name: Repository name in format 'owner/repo'
            
        Returns:
            GitHubRepository object or None if not found
        """
        try:
            response = requests.get(
                f"{self.base_url}/repos/{repo_name}",
                headers=self.headers
            )
            
            if response.status_code == 404:
                return None
            
            response.raise_for_status()
            data = response.json()
            
            return GitHubRepository(
                name=data['name'],
                full_name=data['full_name'],
                owner=data['owner']['login'],
                url=data['html_url'],
                default_branch=data['default_branch'],
                private=data['private']
            )
            
        except Exception as e:
            raise Exception(f"Failed to get repository info: {str(e)}")
    
    def create_label(self, repo_name: str, name: str, color: str, description: str = "") -> Dict:
        """
        Create a label in the repository
        
        Args:
            repo_name: Repository name in format 'owner/repo'
            name: Label name
            color: Label color (hex without #)
            description: Label description
            
        Returns:
            Created label data
        """
        
        # Clean color - remove # if present
        if color.startswith('#'):
            color = color[1:]
        
        payload = {
            "name": name,
            "color": color,
            "description": description
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/repos/{repo_name}/labels",
                headers=self.headers,
                json=payload
            )
            
            # If label already exists, return existing one
            if response.status_code == 422:
                existing = self.get_label(repo_name, name)
                if existing:
                    return existing
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            raise Exception(f"Failed to create label '{name}': {str(e)}")
    
    def get_label(self, repo_name: str, name: str) -> Optional[Dict]:
        """Get existing label"""
        try:
            response = requests.get(
                f"{self.base_url}/repos/{repo_name}/labels/{quote(name)}",
                headers=self.headers
            )
            
            if response.status_code == 404:
                return None
                
            response.raise_for_status()
            return response.json()
            
        except Exception:
            return None
    
    def create_issue(self, repo_name: str, title: str, body: str = "", 
                    labels: List[str] = None, assignees: List[str] = None) -> Dict:
        """
        Create an issue in the repository
        
        Args:
            repo_name: Repository name in format 'owner/repo'
            title: Issue title
            body: Issue body/description
            labels: List of label names
            assignees: List of usernames to assign
            
        Returns:
            Created issue data
        """
        
        payload = {
            "title": title,
            "body": body
        }
        
        if labels:
            payload["labels"] = labels
        
        if assignees:
            payload["assignees"] = assignees
        
        try:
            response = requests.post(
                f"{self.base_url}/repos/{repo_name}/issues",
                headers=self.headers,
                json=payload
            )
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            raise Exception(f"Failed to create issue '{title}': {str(e)}")
    
    def get_repository_owner_id(self, repo_name: str) -> str:
        """Get the repository owner's ID for GraphQL queries"""
        owner = repo_name.split('/')[0]
        
        query = """
        query($login: String!) {
            user(login: $login) {
                id
            }
            organization(login: $login) {
                id
            }
        }
        """
        
        try:
            response = requests.post(
                self.graphql_url,
                headers=self.graphql_headers,
                json={
                    "query": query,
                    "variables": {"login": owner}
                }
            )
            
            response.raise_for_status()
            data = response.json()
            
            if 'errors' in data:
                raise Exception(f"GraphQL errors: {data['errors']}")
            
            # Try user first, then organization
            if data['data']['user']:
                return data['data']['user']['id']
            elif data['data']['organization']:
                return data['data']['organization']['id']
            else:
                raise Exception(f"Could not find owner ID for {owner}")
                
        except Exception as e:
            raise Exception(f"Failed to get owner ID: {str(e)}")
    
    def get_repository_id(self, repo_name: str) -> str:
        """Get repository ID for GraphQL queries"""
        
        query = """
        query($owner: String!, $name: String!) {
            repository(owner: $owner, name: $name) {
                id
            }
        }
        """
        
        owner, name = repo_name.split('/')
        
        try:
            response = requests.post(
                self.graphql_url,
                headers=self.graphql_headers,
                json={
                    "query": query,
                    "variables": {"owner": owner, "name": name}
                }
            )
            
            response.raise_for_status()
            data = response.json()
            
            if 'errors' in data:
                raise Exception(f"GraphQL errors: {data['errors']}")
            
            return data['data']['repository']['id']
            
        except Exception as e:
            raise Exception(f"Failed to get repository ID: {str(e)}")
    
    def create_project_v2(self, owner_id: str, title: str, description: str = "") -> Dict:
        """
        Create a GitHub Projects v2 board
        
        Args:
            owner_id: Owner ID (user or organization)
            title: Project title
            description: Project description
            
        Returns:
            Created project data
        """
        
        mutation = """
        mutation($ownerId: ID!, $title: String!, $description: String) {
            createProjectV2(input: {
                ownerId: $ownerId,
                title: $title,
                description: $description
            }) {
                projectV2 {
                    id
                    title
                    url
                    description
                }
            }
        }
        """
        
        try:
            response = requests.post(
                self.graphql_url,
                headers=self.graphql_headers,
                json={
                    "query": mutation,
                    "variables": {
                        "ownerId": owner_id,
                        "title": title,
                        "description": description
                    }
                }
            )
            
            response.raise_for_status()
            data = response.json()
            
            if 'errors' in data:
                raise Exception(f"GraphQL errors: {data['errors']}")
            
            return data['data']['createProjectV2']['projectV2']
            
        except Exception as e:
            raise Exception(f"Failed to create project: {str(e)}")
    
    def add_issue_to_project(self, project_id: str, issue_id: str) -> Dict:
        """
        Add an issue to a project board
        
        Args:
            project_id: Project ID
            issue_id: Issue node ID
            
        Returns:
            Project item data
        """
        
        mutation = """
        mutation($projectId: ID!, $contentId: ID!) {
            addProjectV2ItemById(input: {
                projectId: $projectId,
                contentId: $contentId
            }) {
                item {
                    id
                }
            }
        }
        """
        
        try:
            response = requests.post(
                self.graphql_url,
                headers=self.graphql_headers,
                json={
                    "query": mutation,
                    "variables": {
                        "projectId": project_id,
                        "contentId": issue_id
                    }
                }
            )
            
            response.raise_for_status()
            data = response.json()
            
            if 'errors' in data:
                # Some errors are expected (like item already exists)
                return {"success": False, "errors": data['errors']}
            
            return data['data']['addProjectV2ItemById']['item']
            
        except Exception as e:
            raise Exception(f"Failed to add issue to project: {str(e)}")
    
    def get_user_info(self) -> Dict:
        """Get authenticated user information"""
        try:
            response = requests.get(
                f"{self.base_url}/user",
                headers=self.headers
            )
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            raise Exception(f"Failed to get user info: {str(e)}")
    
    def list_repository_issues(self, repo_name: str, state: str = "open", 
                              per_page: int = 100) -> List[Dict]:
        """List issues in a repository"""
        try:
            response = requests.get(
                f"{self.base_url}/repos/{repo_name}/issues",
                headers=self.headers,
                params={
                    "state": state,
                    "per_page": per_page
                }
            )
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            raise Exception(f"Failed to list issues: {str(e)}")
    
    def list_repository_labels(self, repo_name: str) -> List[Dict]:
        """List labels in a repository"""
        try:
            response = requests.get(
                f"{self.base_url}/repos/{repo_name}/labels",
                headers=self.headers
            )
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            raise Exception(f"Failed to list labels: {str(e)}")
