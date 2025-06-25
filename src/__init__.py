"""
Universal Project Todo Tracker - Source Package

AI-powered GitHub project management automation.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .openrouter_client import OpenRouterClient
from .github_client import GitHubClient  
from .task_parser import TaskParser
from .project_builder import ProjectBuilder

__all__ = [
    "OpenRouterClient",
    "GitHubClient", 
    "TaskParser",
    "ProjectBuilder"
]