#!/usr/bin/env python3

import os
import sys
import json
from pathlib import Path
from textwrap import dedent
from typing import List, Dict, Any, Optional
from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.style import Style
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style as PromptStyle
import time

# Initialize Rich console and prompt session
console = Console()
prompt_session = PromptSession(
    style=PromptStyle.from_dict({
        'prompt': '#ff6b6b bold',  # Bright red-pink prompt for Kimi
        'completion-menu.completion': 'bg:#8b5cf6 fg:#ffffff',
        'completion-menu.completion.current': 'bg:#a855f7 fg:#ffffff bold',
    })
)

# --------------------------------------------------------------------------------
# 1. Configure OpenAI client for Kimi via OpenRouter
# --------------------------------------------------------------------------------
load_dotenv()
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# Add Exa client
try:
    from exa_py import Exa
    exa_client = Exa(api_key=os.getenv("EXA_API_KEY"))
except ImportError:
    console.print("[bold yellow]⚠[/bold yellow] 'exa_py' not found. To enable web search, please run: [bright_cyan]pip install exa-py[/bright_cyan]")
    exa_client = None

# --------------------------------------------------------------------------------
# 2. Define our schema using Pydantic for type safety
# --------------------------------------------------------------------------------
class FileToCreate(BaseModel):
    path: str
    content: str

class FileToEdit(BaseModel):
    path: str
    original_snippet: str
    new_snippet: str

# --------------------------------------------------------------------------------
# 2.1. Define Function Calling Tools (same as DeepSeek)
# --------------------------------------------------------------------------------
tools = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the content of a single file from the filesystem",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The path to the file to read (relative or absolute)",
                    }
                },
                "required": ["file_path"]
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_multiple_files",
            "description": "Read the content of multiple files from the filesystem",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Array of file paths to read (relative or absolute)",
                    }
                },
                "required": ["file_paths"]
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_file",
            "description": "Create a new file or overwrite an existing file with the provided content",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The path where the file should be created",
                    },
                    "content": {
                        "type": "string",
                        "description": "The content to write to the file",
                    }
                },
                "required": ["file_path", "content"]
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_multiple_files",
            "description": "Create multiple files at once",
            "parameters": {
                "type": "object",
                "properties": {
                    "files": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "path": {"type": "string"},
                                "content": {"type": "string"}
                            },
                            "required": ["path", "content"]
                        },
                        "description": "Array of files to create with their paths and content",
                    }
                },
                "required": ["files"]
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Edit an existing file by replacing a specific snippet with new content",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The path to the file to edit",
                    },
                    "original_snippet": {
                        "type": "string",
                        "description": "The exact text snippet to find and replace",
                    },
                    "new_snippet": {
                        "type": "string",
                        "description": "The new text to replace the original snippet with",
                    }
                },
                "required": ["file_path", "original_snippet", "new_snippet"]
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "exa_search",
            "description": "Perform a web search using Exa.ai for recent and relevant information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to find information on the web.",
                    }
                },
                "required": ["query"]
            },
        }
    }
]

# --------------------------------------------------------------------------------
# 3. System prompt adapted for Kimi
# --------------------------------------------------------------------------------
system_PROMPT = dedent("""
    You are Kimi Possible, an expert software engineer with decades of experience across all programming domains.
    Your expertise spans system design, algorithms, testing, and best practices.
    You provide thoughtful, well-structured solutions while explaining your reasoning.

    Core capabilities:
    1. Code Analysis & Discussion
       - Analyze code with expert-level insight
       - Explain complex concepts clearly
       - Suggest optimizations and best practices
       - Debug issues with precision

    2. File Operations (via function calls):
       - read_file: Read a single file's content
       - read_multiple_files: Read multiple files at once
       - create_file: Create or overwrite a single file
       - create_multiple_files: Create multiple files at once
       - edit_file: Make precise edits to existing files using snippet replacement
       - exa_search: Perform a web search for up-to-date information

    Guidelines:
    1. Provide natural, conversational responses explaining your reasoning
    2. Use function calls when you need to read or modify files, or search the web
    3. For file operations:
       - Always read files first before editing them to understand the context
       - Use precise snippet matching for edits
       - Explain what changes you're making and why
       - Consider the impact of changes on the overall codebase
    4. Follow language-specific best practices
    5. Suggest tests or validation steps when appropriate
    6. Be thorough in your analysis and recommendations

    Remember: You're a senior engineer - be thoughtful, precise, and explain your reasoning clearly.
""")

# --------------------------------------------------------------------------------
# 4. Helper functions (same as DeepSeek)
# --------------------------------------------------------------------------------

def read_local_file(file_path: str) -> str:
    """Return the text content of a local file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def create_file(path: str, content: str):
    """Create (or overwrite) a file at 'path' with the given 'content'."""
    file_path = Path(path)
    
    # Security checks
    if any(part.startswith('~') for part in file_path.parts):
        raise ValueError("Home directory references not allowed")
    normalized_path = normalize_path(str(file_path))
    
    # Validate reasonable file size for operations
    if len(content) > 5_000_000:  # 5MB limit
        raise ValueError("File content exceeds 5MB size limit")
    
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    console.print(f"[bold magenta]✓[/bold magenta] File created at '[bright_cyan]{file_path}[/bright_cyan]'")

def show_diff_table(files_to_edit: List[FileToEdit]) -> None:
    if not files_to_edit:
        return
    
    table = Table(title="📝 Proposed Edits", show_header=True, header_style="bold bright_magenta", show_lines=True, border_style="magenta")
    table.add_column("File Path", style="bright_cyan", no_wrap=True)
    table.add_column("Original", style="red dim")
    table.add_column("New", style="bright_green")

    for edit in files_to_edit:
        table.add_row(edit.path, edit.original_snippet, edit.new_snippet)
    
    console.print(table)

def apply_diff_edit(path: str, original_snippet: str, new_snippet: str):
    """Reads the file at 'path', replaces the first occurrence of 'original_snippet' with 'new_snippet', then overwrites."""
    try:
        content = read_local_file(path)
        
        # Verify we're replacing the exact intended occurrence
        occurrences = content.count(original_snippet)
        if occurrences == 0:
            raise ValueError("Original snippet not found")
        if occurrences > 1:
            console.print(f"[bold yellow]⚠ Multiple matches ({occurrences}) found - requiring line numbers for safety[/bold yellow]")
            console.print("[dim]Use format:\n--- original.py (lines X-Y)\n+++ modified.py[/dim]")
            raise ValueError(f"Ambiguous edit: {occurrences} matches")
        
        updated_content = content.replace(original_snippet, new_snippet, 1)
        create_file(path, updated_content)
        console.print(f"[bold magenta]✓[/bold magenta] File updated in '[bright_cyan]{path}[/bright_cyan]'")

    except FileNotFoundError:
        console.print(f"[bold red]✗[/bold red] File not found: '[bright_cyan]{path}[/bright_cyan]'")
    except ValueError as e:
        console.print(f"[bold yellow]⚠[/bold yellow] {str(e)} in '[bright_cyan]{path}[/bright_cyan]'. No changes made.")
        console.print("\n[bold magenta]Expected snippet:[/bold magenta]")
        console.print(Panel(original_snippet, title="Expected", border_style="magenta", title_align="left"))
        console.print("\n[bold magenta]Actual file content:[/bold magenta]")
        console.print(Panel(content, title="Actual", border_style="yellow", title_align="left"))

def try_handle_add_command(user_input: str) -> bool:
    prefix = "/add "
    if user_input.strip().lower().startswith(prefix):
        path_to_add = user_input[len(prefix):].strip()
        try:
            normalized_path = normalize_path(path_to_add)
            if os.path.isdir(normalized_path):
                # Handle entire directory
                add_directory_to_conversation(normalized_path)
            else:
                # Handle a single file as before
                content = read_local_file(normalized_path)
                conversation_history.append({
                    "role": "system",
                    "content": f"Content of file '{normalized_path}':\n\n{content}"
                })
                console.print(f"[bold magenta]✓[/bold magenta] File '[bright_cyan]{normalized_path}[/bright_cyan]' added to context.\n")
        except OSError as e:
            console.print(f"[bold red]✗[/bold red] Cannot access path '[bright_cyan]{path_to_add}[/bright_cyan]': {e}\n")
        return True
    return False

def add_directory_to_conversation(directory_path: str):
    with console.status("[bold bright_magenta]📁 Scanning directory...[/bold bright_magenta]") as status:
        excluded_files = {
            # Python specific
            ".DS_Store", "Thumbs.db", ".gitignore", ".python-version",
            "uv.lock", ".uv", "uvenv", ".uvenv", ".venv", "venv",
            "__pycache__", ".pytest_cache", ".coverage", ".mypy_cache",
            # Node.js / Web specific
            "node_modules", "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
            ".next", ".nuxt", "dist", "build", ".cache", ".parcel-cache",
            ".turbo", ".vercel", ".output", ".contentlayer",
            # Build outputs
            "out", "coverage", ".nyc_output", "storybook-static",
            # Environment and config
            ".env", ".env.local", ".env.development", ".env.production",
            # Misc
            ".git", ".svn", ".hg", "CVS"
        }
        excluded_extensions = {
            # Binary and media files
            ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp", ".avif",
            ".mp4", ".webm", ".mov", ".mp3", ".wav", ".ogg",
            ".zip", ".tar", ".gz", ".7z", ".rar",
            ".exe", ".dll", ".so", ".dylib", ".bin",
            # Documents
            ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
            # Python specific
            ".pyc", ".pyo", ".pyd", ".egg", ".whl",
            # UV specific
            ".uv", ".uvenv",
            # Database and logs
            ".db", ".sqlite", ".sqlite3", ".log",
            # IDE specific
            ".idea", ".vscode",
            # Web specific
            ".map", ".chunk.js", ".chunk.css",
            ".min.js", ".min.css", ".bundle.js", ".bundle.css",
            # Cache and temp files
            ".cache", ".tmp", ".temp",
            # Font files
            ".ttf", ".otf", ".woff", ".woff2", ".eot"
        }
        skipped_files = []
        added_files = []
        total_files_processed = 0
        max_files = 1000  # Reasonable limit for files to process
        max_file_size = 5_000_000  # 5MB limit

        for root, dirs, files in os.walk(directory_path):
            if total_files_processed >= max_files:
                console.print(f"[bold yellow]⚠[/bold yellow] Reached maximum file limit ({max_files})")
                break

            status.update(f"[bold bright_magenta]📁 Processing {root}...[/bold bright_magenta]")
            # Skip hidden directories and excluded directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in excluded_files]

            for file in files:
                if total_files_processed >= max_files:
                    break

                if file.startswith('.') or file in excluded_files:
                    skipped_files.append(os.path.join(root, file))
                    continue

                _, ext = os.path.splitext(file)
                if ext.lower() in excluded_extensions:
                    skipped_files.append(os.path.join(root, file))
                    continue

                full_path = os.path.join(root, file)

                try:
                    # Check file size before processing
                    if os.path.getsize(full_path) > max_file_size:
                        skipped_files.append(f"{full_path} (exceeds size limit)")
                        continue

                    # Check if it's binary
                    if is_binary_file(full_path):
                        skipped_files.append(full_path)
                        continue

                    normalized_path = normalize_path(full_path)
                    content = read_local_file(normalized_path)
                    conversation_history.append({
                        "role": "system",
                        "content": f"Content of file '{normalized_path}':\n\n{content}"
                    })
                    added_files.append(normalized_path)
                    total_files_processed += 1

                except OSError:
                    skipped_files.append(full_path)

        console.print(f"[bold magenta]✓[/bold magenta] Added folder '[bright_cyan]{directory_path}[/bright_cyan]' to conversation.")
        if added_files:
            console.print(f"\n[bold bright_magenta]📁 Added files:[/bold bright_magenta] [dim]({len(added_files)} of {total_files_processed})[/dim]")
            for f in added_files:
                console.print(f"  [bright_cyan]📄 {f}[/bright_cyan]")
        if skipped_files:
            console.print(f"\n[bold yellow]⏭ Skipped files:[/bold yellow] [dim]({len(skipped_files)})[/dim]")
            for f in skipped_files[:10]:  # Show only first 10 to avoid clutter
                console.print(f"  [yellow dim]⚠ {f}[/yellow dim]")
            if len(skipped_files) > 10:
                console.print(f"  [dim]... and {len(skipped_files) - 10} more[/dim]")
        console.print()

def is_binary_file(file_path: str, peek_size: int = 1024) -> bool:
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(peek_size)
        # If there is a null byte in the sample, treat it as binary
        if b'\0' in chunk:
            return True
        return False
    except Exception:
        # If we fail to read, just treat it as binary to be safe
        return True

def ensure_file_in_context(file_path: str) -> bool:
    try:
        normalized_path = normalize_path(file_path)
        content = read_local_file(normalized_path)
        file_marker = f"Content of file '{normalized_path}'"
        if not any(file_marker in msg["content"] for msg in conversation_history):
            conversation_history.append({
                "role": "system",
                "content": f"{file_marker}:\n\n{content}"
            })
        return True
    except OSError:
        console.print(f"[bold red]✗[/bold red] Could not read file '[bright_cyan]{file_path}[/bright_cyan]' for editing context")
        return False

def normalize_path(path_str: str) -> str:
    """Return a canonical, absolute version of the path with security checks."""
    path = Path(path_str).resolve()
    
    # Prevent directory traversal attacks
    if ".." in path.parts:
        raise ValueError(f"Invalid path: {path_str} contains parent directory references")
    
    return str(path)

# --------------------------------------------------------------------------------
# 5. Conversation state
# --------------------------------------------------------------------------------
conversation_history = [
    {"role": "system", "content": system_PROMPT}
]

# --------------------------------------------------------------------------------
# 6. Tool execution functions
# --------------------------------------------------------------------------------

# Map each tool name to its corresponding function
tool_map = {
    "read_file": lambda args: execute_read_file(args),
    "read_multiple_files": lambda args: execute_read_multiple_files(args),
    "create_file": lambda args: execute_create_file(args),
    "create_multiple_files": lambda args: execute_create_multiple_files(args),
    "edit_file": lambda args: execute_edit_file(args),
    "exa_search": lambda args: execute_exa_search(args),
}

def execute_read_file(arguments: Dict[str, Any]) -> str:
    file_path = arguments["file_path"]
    normalized_path = normalize_path(file_path)
    content = read_local_file(normalized_path)
    return f"Content of file '{normalized_path}':\n\n{content}"

def execute_read_multiple_files(arguments: Dict[str, Any]) -> str:
    file_paths = arguments["file_paths"]
    results = []
    for file_path in file_paths:
        try:
            normalized_path = normalize_path(file_path)
            content = read_local_file(normalized_path)
            results.append(f"Content of file '{normalized_path}':\n\n{content}")
        except OSError as e:
            results.append(f"Error reading '{file_path}': {e}")
    return "\n\n" + "="*50 + "\n\n".join(results)

def execute_create_file(arguments: Dict[str, Any]) -> str:
    file_path = arguments["file_path"]
    content = arguments["content"]
    create_file(file_path, content)
    return f"Successfully created file '{file_path}'"

def execute_create_multiple_files(arguments: Dict[str, Any]) -> str:
    files = arguments["files"]
    created_files = []
    for file_info in files:
        create_file(file_info["path"], file_info["content"])
        created_files.append(file_info["path"])
    return f"Successfully created {len(created_files)} files: {', '.join(created_files)}"

def execute_edit_file(arguments: Dict[str, Any]) -> str:
    file_path = arguments["file_path"]
    original_snippet = arguments["original_snippet"]
    new_snippet = arguments["new_snippet"]
    
    # Ensure file is in context first
    if not ensure_file_in_context(file_path):
        return f"Error: Could not read file '{file_path}' for editing"
    
    apply_diff_edit(file_path, original_snippet, new_snippet)
    return f"Successfully edited file '{file_path}'"

def execute_exa_search(arguments: Dict[str, Any]) -> str:
    if not exa_client:
        return "Error: Exa client is not configured. Please install exa-py and set EXA_API_KEY."
    query = arguments["query"]
    try:
        console.print(f"[bright_magenta]🔍 Searching for:[/bright_magenta] [dim]{query}[/dim]")
        search_results = exa_client.search_and_contents(
            query,
            use_autoprompt=True,
            num_results=3,
            text={"include_html_tags": False}
        )
        # Format the results for the LLM
        formatted_results = f"Search results for '{query}':\n\n"
        for result in search_results.results:
            formatted_results += f"Title: {result.title}\n"
            formatted_results += f"URL: {result.url}\n"
            formatted_results += f"Content: {result.text}\n"
            formatted_results += "-"*20 + "\n"
        return formatted_results
    except Exception as e:
        return f"Error performing Exa search: {e}"

# --------------------------------------------------------------------------------
# 7. Kimi API interaction (adapted from tool calling example)
# --------------------------------------------------------------------------------

def trim_conversation_history():
    """Trim conversation history to prevent token limit issues while preserving tool call sequences"""
    if len(conversation_history) <= 20:  # Don't trim if conversation is still small
        return
        
    # Always keep the system prompt
    system_msgs = [msg for msg in conversation_history if msg["role"] == "system"]
    other_msgs = [msg for msg in conversation_history if msg["role"] != "system"]
    
    # Keep only the last 15 messages to prevent token overflow
    if len(other_msgs) > 15:
        other_msgs = other_msgs[-15:]
    
    # Rebuild conversation history
    conversation_history.clear()
    conversation_history.extend(system_msgs + other_msgs)

def kimi_chat_with_tools(user_message: str):
    # Add the user message to conversation history
    conversation_history.append({"role": "user", "content": user_message})
    
    # Trim conversation history if it's getting too long
    trim_conversation_history()
    
    finish_reason = None
    
    try:
        # Use Kimi's tool calling pattern
        while finish_reason is None or finish_reason == "tool_calls":
            completion = client.chat.completions.create(
                model="moonshotai/kimi-k2",
                messages=conversation_history,
                temperature=0.3,
                tools=tools,
                extra_headers={
                    "HTTP-Referer": "https://github.com/kingj/kimi-possible",
                    "X-Title": "Kimi Possible",
                },
            )
            
            choice = completion.choices[0]
            finish_reason = choice.finish_reason
            
            if finish_reason == "tool_calls":
                # Add assistant message to context
                conversation_history.append(choice.message)
                
                console.print(f"\n[bold bright_magenta]⚡ Executing {len(choice.message.tool_calls)} function call(s)...[/bold bright_magenta]")
                
                # Execute each tool call
                for tool_call in choice.message.tool_calls:
                    tool_call_name = tool_call.function.name
                    tool_call_arguments = json.loads(tool_call.function.arguments)
                    
                    console.print(f"[bright_magenta]→ {tool_call_name}[/bright_magenta]")
                    
                    try:
                        tool_function = tool_map[tool_call_name]
                        tool_result = tool_function(tool_call_arguments)
                        
                        # Add tool result to conversation
                        conversation_history.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_call_name,
                            "content": json.dumps({"result": tool_result}),
                        })
                        
                    except Exception as e:
                        console.print(f"[red]Error executing {tool_call_name}: {e}[/red]")
                        conversation_history.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_call_name,
                            "content": json.dumps({"error": str(e)}),
                        })
            else:
                # Final response - display it
                console.print(f"\n[bold bright_magenta]🕵️‍♀️ Kimi>[/bold bright_magenta] {choice.message.content}")
                # Add final response to conversation history
                conversation_history.append(choice.message)
        
        return {"success": True}
        
    except Exception as e:
        error_msg = f"Kimi API error: {str(e)}"
        console.print(f"\n[bold red]❌ {error_msg}[/bold red]")
        return {"error": error_msg}

# --------------------------------------------------------------------------------
# 8. Main interactive loop
# --------------------------------------------------------------------------------

def main():
    # Create a beautiful gradient-style welcome panel
    welcome_text = """[bold bright_magenta]🕵️‍♀️ Kimi Possible[/bold bright_magenta] [bright_cyan]AI Code Assistant[/bright_cyan]
[dim magenta]Powered by Kimi-K2 with Function Calling[/dim magenta]"""
    
    console.print(Panel.fit(
        welcome_text,
        border_style="bright_magenta",
        padding=(1, 2),
        title="[bold bright_cyan]🕵️‍♀️ AI Code Assistant[/bold bright_cyan]",
        title_align="center"
    ))
    
    # Create an elegant instruction panel
    instructions = """[bold bright_magenta]📁 File Operations:[/bold bright_magenta]
  • [bright_cyan]/add path/to/file[/bright_cyan] - Include a single file in conversation
  • [bright_cyan]/add path/to/folder[/bright_cyan] - Include all files in a folder
  • [dim]The AI can automatically read and create files using function calls[/dim]

[bold bright_magenta]🎯 Commands:[/bold bright_magenta]
  • [bright_cyan]exit[/bright_cyan] or [bright_cyan]quit[/bright_cyan] - End the session
  • Just ask naturally - the AI will handle file operations automatically!"""
    
    console.print(Panel(
        instructions,
        border_style="magenta",
        padding=(1, 2),
        title="[bold magenta]💡 How to Use[/bold magenta]",
        title_align="left"
    ))
    console.print()

    while True:
        try:
            user_input = prompt_session.prompt("💜 You> ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[bold yellow]👋 Exiting gracefully...[/bold yellow]")
            break

        if not user_input:
            continue

        if user_input.lower() in ["exit", "quit"]:
            console.print("[bold bright_magenta]👋 Goodbye! Happy coding![/bold bright_magenta]")
            break

        if try_handle_add_command(user_input):
            continue

        response_data = kimi_chat_with_tools(user_input)
        
        if response_data.get("error"):
            console.print(f"[bold red]❌ Error: {response_data['error']}[/bold red]")

    console.print("[bold magenta]✨ Session finished. Thank you for using Kimi Possible![/bold magenta]")

if __name__ == "__main__":
    main()
