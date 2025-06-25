#!/usr/bin/env python3
"""
Universal Project To-Do Tracker
AI-powered GitHub project management automation
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional

# Try to import optional dependencies
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Please set environment variables manually.")
    def load_dotenv():
        pass

def load_env_manually():
    """Load environment variables from .env file manually if dotenv is not available"""
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

# Load environment variables
load_dotenv()
load_env_manually()  # Fallback for manual loading

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.panel import Panel
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    print("Warning: rich not installed. Using basic console output.")
    RICH_AVAILABLE = False
    # Create basic fallback classes
    class Console:
        def print(self, *args, **kwargs):
            # Remove rich formatting
            text = str(args[0]) if args else ""
            # Simple cleanup of rich markup
            import re
            text = re.sub(r'\[.*?\]', '', text)
            print(text)
    
    class Progress:
        def __init__(self, *args, **kwargs):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def add_task(self, description, total=None):
            # Clean description
            import re
            clean_desc = re.sub(r'\[.*?\]', '', description)
            print(f"Starting: {clean_desc}")
            return "task_id"
        def update(self, task_id, description=None):
            if description:
                import re
                clean_desc = re.sub(r'\[.*?\]', '', description)
                print(f"Update: {clean_desc}")
    
    class Panel:
        @staticmethod
        def fit(content, **kwargs):
            # Clean content
            import re
            clean_content = re.sub(r'\[.*?\]', '', str(content))
            return clean_content
    
    class Text:
        def __init__(self):
            self.content = ""
        def append(self, text, style=None):
            self.content += text
    
    # Dummy classes for compatibility
    SpinnerColumn = lambda: None
    TextColumn = lambda x: None

# Import our modules
from src.openrouter_client import OpenRouterClient
from src.github_client import GitHubClient
from src.task_parser import TaskParser
from src.project_builder import ProjectBuilder

console = Console()

class UniversalTodoTracker:
    """Main application class for the Universal Todo Tracker"""
    
    def __init__(self):
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.default_model = os.getenv('DEFAULT_MODEL', 'deepseek/deepseek-r1-distill-llama-70b')
        
        if not self.openrouter_api_key:
            console.print("[red]❌ OPENROUTER_API_KEY not found in environment variables[/red]")
            console.print("Please set your OpenRouter API key in .env file")
            sys.exit(1)
            
        if not self.github_token:
            console.print("[red]❌ GITHUB_TOKEN not found in environment variables[/red]")
            console.print("Please set your GitHub token in .env file")
            sys.exit(1)
        
        # Initialize clients
        self.openrouter = OpenRouterClient(self.openrouter_api_key)
        self.github = GitHubClient(self.github_token)
        self.task_parser = TaskParser(self.openrouter)
        self.project_builder = ProjectBuilder(self.github)
    
    def load_project_description(self, description: Optional[str], file_path: Optional[str]) -> str:
        """Load project description from argument or file"""
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read().strip()
            except FileNotFoundError:
                console.print(f"[red]❌ File not found: {file_path}[/red]")
                sys.exit(1)
        elif description:
            return description.strip()
        else:
            console.print("[red]❌ No project description provided[/red]")
            console.print("Use --description or --file to provide project details")
            sys.exit(1)
    
    def run(self, repo_name: str, description: Optional[str] = None, 
            file_path: Optional[str] = None, model: Optional[str] = None,
            create_board: bool = True, max_tasks: int = 20) -> Dict:
        """Main execution flow"""
        
        # Load project description
        project_desc = self.load_project_description(description, file_path)
        selected_model = model or self.default_model
        
        console.print(Panel.fit(
            f"[bold blue]🚀 Universal Project To-Do Tracker[/bold blue]\n"
            f"[dim]Transforming your project idea into organized GitHub issues[/dim]",
            border_style="blue"
        ))
        
        with Progress(
            *([SpinnerColumn(), TextColumn("[progress.description]{task.description}")] if RICH_AVAILABLE else []),
            console=console,
        ) as progress:
            
            # Step 1: Parse project into tasks
            task1 = progress.add_task("🧠 Analyzing project with AI...", total=None)
            try:
                parsed_data = self.task_parser.parse_project(
                    project_desc, 
                    model=selected_model, 
                    max_tasks=max_tasks
                )
                progress.update(task1, description="✅ Project analysis complete")
            except Exception as e:
                progress.update(task1, description="❌ Failed to analyze project")
                console.print(f"[red]Error analyzing project: {str(e)}[/red]")
                return {"success": False, "error": str(e)}
            
            # Step 2: Validate repository
            task2 = progress.add_task("🔍 Validating GitHub repository...", total=None)
            try:
                repo_info = self.github.get_repository(repo_name)
                if not repo_info:
                    progress.update(task2, description="❌ Repository not found")
                    console.print(f"[red]Repository {repo_name} not found or not accessible[/red]")
                    return {"success": False, "error": "Repository not found"}
                progress.update(task2, description="✅ Repository validated")
            except Exception as e:
                progress.update(task2, description="❌ Repository validation failed")
                console.print(f"[red]Error accessing repository: {str(e)}[/red]")
                return {"success": False, "error": str(e)}
            
            # Step 3: Create labels
            task3 = progress.add_task("🏷️ Creating GitHub labels...", total=None)
            try:
                labels_created = self.project_builder.create_labels(repo_name, parsed_data['labels'])
                progress.update(task3, description=f"✅ Created {len(labels_created)} labels")
            except Exception as e:
                progress.update(task3, description="❌ Failed to create labels")
                console.print(f"[red]Error creating labels: {str(e)}[/red]")
                return {"success": False, "error": str(e)}
            
            # Step 4: Create issues
            task4 = progress.add_task("📋 Creating GitHub issues...", total=None)
            try:
                issues_created = self.project_builder.create_issues(repo_name, parsed_data['tasks'])
                progress.update(task4, description=f"✅ Created {len(issues_created)} issues")
            except Exception as e:
                progress.update(task4, description="❌ Failed to create issues")
                console.print(f"[red]Error creating issues: {str(e)}[/red]")
                return {"success": False, "error": str(e)}
            
            # Step 5: Create project board (optional)
            project_url = None
            if create_board:
                task5 = progress.add_task("🗂️ Creating project board...", total=None)
                try:
                    project_url = self.project_builder.create_project_board(
                        repo_name, 
                        parsed_data['project_name'],
                        issues_created
                    )
                    progress.update(task5, description="✅ Project board created")
                except Exception as e:
                    progress.update(task5, description="⚠️ Project board creation failed")
                    console.print(f"[yellow]Warning: Could not create project board: {str(e)}[/yellow]")
        
        # Display results
        self.display_results(repo_name, parsed_data, issues_created, labels_created, project_url)
        
        return {
            "success": True,
            "repository": repo_name,
            "project_name": parsed_data['project_name'],
            "tasks_created": len(issues_created),
            "labels_created": len(labels_created),
            "project_url": project_url,
            "issues": issues_created
        }
    
    def display_results(self, repo_name: str, parsed_data: Dict, 
                       issues: List, labels: List, project_url: Optional[str]):
        """Display the results of the project creation"""
        
        console.print("\n" + "="*80)
        console.print(Panel.fit(
            f"[bold green]🎉 Success! Your project has been created[/bold green]\n"
            f"[dim]Repository: {repo_name}[/dim]",
            border_style="green"
        ))
        
        # Summary stats
        stats_text = Text()
        stats_text.append("📊 Summary:\n", style="bold")
        stats_text.append(f"  • Project: {parsed_data['project_name']}\n")
        stats_text.append(f"  • Tasks Created: {len(issues)}\n") 
        stats_text.append(f"  • Labels Created: {len(labels)}\n")
        stats_text.append(f"  • Phases: {len(parsed_data.get('phases', []))}\n")
        
        console.print(Panel(stats_text, title="📈 Results", border_style="cyan"))
        
        # Display created labels
        if labels:
            labels_text = Text()
            for label in labels[:10]:  # Show first 10
                labels_text.append(f"  🏷️ {label['name']}", style=f"#{label['color']}")
                labels_text.append(f" ({label['description']})\n", style="dim")
            
            if len(labels) > 10:
                labels_text.append(f"  ... and {len(labels) - 10} more", style="dim")
            
            console.print(Panel(labels_text, title="🏷️ Labels Created", border_style="blue"))
        
        # Display sample issues
        if issues:
            issues_text = Text()
            for i, issue in enumerate(issues[:5]):  # Show first 5
                issues_text.append(f"  {i+1}. {issue['title']}\n", style="bold")
                issues_text.append(f"     Priority: {issue.get('priority', 'medium')} | ", style="dim")
                issues_text.append(f"Effort: {issue.get('effort', 'unknown')}\n", style="dim")
            
            if len(issues) > 5:
                issues_text.append(f"  ... and {len(issues) - 5} more issues", style="dim")
            
            console.print(Panel(issues_text, title="📋 Issues Created", border_style="yellow"))
        
        # URLs and next steps
        next_steps = Text()
        next_steps.append("🚀 Next Steps:\n", style="bold green")
        next_steps.append(f"  1. View repository: https://github.com/{repo_name}\n")
        next_steps.append(f"  2. Check issues: https://github.com/{repo_name}/issues\n")
        if project_url:
            next_steps.append(f"  3. Manage project: {project_url}\n")
        next_steps.append("  4. Start coding! 🎯\n")
        
        console.print(Panel(next_steps, title="🎯 What's Next", border_style="green"))


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Universal Project To-Do Tracker - AI-powered GitHub project management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --repo "username/my-project" --description "Build a task management app"
  %(prog)s --repo "username/my-project" --file "project_spec.md" --model "anthropic/claude-3.5-sonnet"
  %(prog)s --repo "username/my-project" --description "E-commerce platform" --no-board
        """
    )
    
    parser.add_argument(
        '--repo', '-r',
        required=True,
        help='GitHub repository name (format: username/repo-name)'
    )
    
    parser.add_argument(
        '--description', '-d',
        help='Project description text'
    )
    
    parser.add_argument(
        '--file', '-f',
        help='Path to file containing project description'
    )
    
    parser.add_argument(
        '--model', '-m',
        help='OpenRouter model to use (default: deepseek/deepseek-r1-distill-llama-70b)'
    )
    
    parser.add_argument(
        '--max-tasks',
        type=int,
        default=20,
        help='Maximum number of tasks to generate (default: 20)'
    )
    
    parser.add_argument(
        '--no-board',
        action='store_true',
        help='Skip creating project board'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Save results to JSON file'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    return parser


def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Validate arguments
    if not args.description and not args.file:
        parser.error("Either --description or --file must be provided")
    
    if args.description and args.file:
        parser.error("Cannot use both --description and --file")
    
    try:
        # Initialize tracker
        tracker = UniversalTodoTracker()
        
        # Run the main process
        result = tracker.run(
            repo_name=args.repo,
            description=args.description,
            file_path=args.file,
            model=args.model,
            create_board=not args.no_board,
            max_tasks=args.max_tasks
        )
        
        # Save output if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            console.print(f"[green]Results saved to {args.output}[/green]")
        
        if result['success']:
            console.print("[bold green]🎉 Project setup completed successfully![/bold green]")
            sys.exit(0)
        else:
            console.print("[bold red]❌ Project setup failed[/bold red]")
            sys.exit(1)
            
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ Operation cancelled by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[bold red]❌ Unexpected error: {str(e)}[/bold red]")
        if args.verbose:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
