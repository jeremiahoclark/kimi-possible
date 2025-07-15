# Kimi Possible

🕵️‍♀️ **AI Research Assistant & Code Helper**

A powerful AI assistant powered by Kimi-K2 that combines advanced code analysis with comprehensive web research capabilities. Kimi Possible can help you with software development tasks while also researching content reactions across multiple platforms.

## Features

### 🔧 Code & File Operations
- **File Management**: Read, create, and edit files with precision
- **Multi-file Operations**: Handle multiple files simultaneously
- **Smart Editing**: Precise snippet-based file modifications
- **Code Analysis**: Expert-level code review and optimization suggestions

### 🌐 Web Research Capabilities
- **General Web Search**: Powered by Exa.ai for comprehensive web results
- **X.com/Twitter Search**: Direct integration with X.ai Live Search API for real-time Twitter data
- **Content Research**: Specialized workflows for finding reactions to movies, TV shows, and content across:
  - Reddit discussions
  - Letterboxd reviews (for movies)
  - X.com/Twitter reactions
  - Rotten Tomatoes scores and reviews

### 💬 Interactive Interface
- Beautiful terminal UI with Rich styling
- Natural language interaction
- Tool function calling with visual feedback
- File context management with `/add` commands

## Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/kimi-possible.git
cd kimi-possible
```

2. **Install dependencies**
```bash
uv pip install -r requirements.txt
# or
pip install -r requirements.txt
```

3. **Configure API keys**
Create a `.env` file with:
```env
OPENROUTER_API_KEY=your_openrouter_api_key
EXA_API_KEY=your_exa_api_key
X_API_KEY=your_x_ai_api_key
```

4. **Run the application**
```bash
python kimi-possible.py
```

## Usage

### File Operations
```bash
You> /add myfile.py                    # Add single file to context
You> /add src/                         # Add entire directory
You> Create a new Python script...     # Natural language requests
```

### Web Research
```bash
You> Search Twitter for reactions to The Batman 2022
You> Find what people think about Oppenheimer movie
You> Research public opinion on latest iPhone release
```

### Code Analysis
```bash
You> Review this code for potential issues
You> Optimize this function for better performance
You> Add error handling to this script
```

## API Requirements

- **OpenRouter**: For Kimi-K2 model access
- **Exa.ai**: For general web search capabilities
- **X.ai**: For Twitter/X.com search functionality

## Dependencies

- `openai` - OpenAI API client for Kimi-K2 via OpenRouter
- `exa-py` - Exa.ai search API client
- `requests` - HTTP requests for X.ai Live Search
- `rich` - Beautiful terminal interface
- `prompt-toolkit` - Interactive prompts
- `pydantic` - Data validation
- `python-dotenv` - Environment variable management

## License

MIT License - see LICENSE file for details
