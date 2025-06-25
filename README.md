# 🚀 Universal Project Todo Tracker

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![Status](https://img.shields.io/badge/status-production%20ready-green.svg)

**AI-powered GitHub project management automation that transforms any project description into organized GitHub issues, labels, and project boards.**

## ✨ Features

- 🧠 **AI-Powered Analysis**: Uses OpenRouter AI to intelligently parse project descriptions
- 📋 **Automatic Issue Creation**: Generates structured GitHub issues with priorities and labels
- 🏷️ **Smart Labeling**: Creates semantic labels for effective project organization
- 🗂️ **Project Boards**: Sets up GitHub Projects v2 boards (with manual linking)
- 🎯 **Phase-Based Organization**: Breaks projects into logical development phases
- 🔧 **Effort Estimation**: Assigns realistic time estimates to tasks

## 🎉 Success Story

✅ **Fully Tested & Working!** This tool has been successfully tested and created:
- **14 GitHub Issues** for a TaskFlow project
- **20 Smart Labels** with proper categorization
- **Project Boards** ready for organization
- **Full AI Analysis** with proper task breakdown

![GitHub Issues Screenshot](./assets/github_issues_screenshot.png)

## 🛠️ Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file with your API keys:
```env
# Required API Keys
OPENROUTER_API_KEY=your_openrouter_api_key_here
GITHUB_TOKEN=your_github_token_here

# Optional Configuration
DEFAULT_MODEL=mistralai/mistral-7b-instruct:free
MAX_TASKS_PER_PHASE=10
DEFAULT_ASSIGNEE=your_username
```

### 3. Get Your API Keys

**OpenRouter API Key:**
1. Visit [OpenRouter.ai](https://openrouter.ai)
2. Sign up and get your API key
3. Choose from many free models available

**GitHub Token:**
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Create token with scopes: `repo`, `project`, `workflow`

## 🚀 Usage

### Basic Usage
```bash
python main.py --file project_description.md --repo username/repository-name
```

### Advanced Usage
```bash
# Use specific AI model
python main.py --file project.md --repo user/repo --model mistralai/mistral-7b-instruct:free

# Limit number of tasks
python main.py --file project.md --repo user/repo --max-tasks 15

# Skip project board creation
python main.py --file project.md --repo user/repo --no-board

# Save results to JSON
python main.py --file project.md --repo user/repo --output results.json
```

### Command Line Options
- `--repo, -r`: GitHub repository (required)
- `--file, -f`: Project description file
- `--description, -d`: Project description text
- `--model, -m`: AI model to use
- `--max-tasks`: Maximum tasks to generate
- `--no-board`: Skip project board creation
- `--output, -o`: Save results to JSON file
- `--verbose, -v`: Verbose output

## 📝 Project Description Format

Create a markdown file describing your project:

```markdown
# My Awesome Project

A comprehensive web application for task management.

## Features
- User authentication
- Project workspaces
- Real-time collaboration
- Task assignment and tracking
- File attachments
- Mobile responsive design

## Tech Stack
- Backend: Node.js, Express, MongoDB
- Frontend: React, TypeScript
- Real-time: Socket.io
- Authentication: JWT
```

## 🎯 What Gets Created

### GitHub Issues
- Structured tasks with clear descriptions
- Priority levels (high, medium, low)
- Effort estimates (1-day, 3-days, 1-week, 2-weeks)
- Proper labels and assignments

### Labels
- **Priority**: `priority:high`, `priority:medium`, `priority:low`
- **Type**: `type:feature`, `type:backend`, `type:frontend`, `type:testing`
- **Phase**: `phase:planning`, `phase:development`, `phase:testing`
- **Effort**: `effort:small`, `effort:medium`, `effort:large`

### Project Organization
- Logical phases (Planning, Development, Testing, Deployment)
- Task dependencies and relationships
- Clear acceptance criteria

## 🔧 Supported AI Models

### Free Models (Recommended)
- `mistralai/mistral-7b-instruct:free`
- `mistralai/mistral-small-3.2-24b-instruct:free`
- `huggingface/microsoft/DialoGPT-medium:free`

### Premium Models
- `openai/gpt-4`
- `anthropic/claude-3.5-sonnet`
- `deepseek/deepseek-r1-distill-llama-70b`

## 📁 Project Structure

```
universal-project-todo-tracker/
├── main.py                 # Main application
├── src/
│   ├── openrouter_client.py    # OpenRouter AI client
│   ├── github_client.py        # GitHub API client
│   ├── task_parser.py          # AI task parsing
│   └── project_builder.py      # GitHub project builder
├── prompts/
│   └── extract_tasks.txt       # AI prompt template
├── templates/
│   ├── issue_template.md       # Issue template
│   └── project_readme.md       # Project README template
├── .env.example               # Environment variables example
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```

## 🎉 Example Output

```
🚀 Universal Project To-Do Tracker
Transforming your project idea into organized GitHub issues

✅ Project analysis complete
✅ Repository validated  
✅ Created 20 labels
✅ Created 14 issues
⚠️ Project board creation requires manual setup

📊 Summary:
  • Project: TaskFlow - Modern Task Management Platform
  • Tasks Created: 14
  • Labels Created: 20
  • Phases: 7

🚀 Next Steps:
  1. View repository: https://github.com/username/repo
  2. Check issues: https://github.com/username/repo/issues
  3. Create project board manually
  4. Start coding! 🎯
```

## 🔨 Manual Project Board Setup

Since GitHub's Projects v2 API requires manual issue linking:

1. Go to your repository → Projects tab
2. Click "Link a project" or "New project"  
3. Create a new project board
4. Add items from your repository
5. Select all created issues
6. Organize into columns by phase/status

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🙋 Support

If you encounter any issues:
1. Check that your API keys are valid
2. Ensure you have proper repository permissions
3. Verify the AI model is available and free
4. Check your internet connection

---

**Made with ❤️ for developers who want to organize their projects efficiently!**
