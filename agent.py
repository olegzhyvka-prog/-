#!/usr/bin/env python3
"""
Autonomous AI Agent — Manus-style task executor.
Usage: python agent.py "your task here"
       python agent.py  (interactive mode)
"""

import os
import sys
import json
import subprocess
import tempfile
import traceback
from pathlib import Path
from datetime import datetime

import httpx
from bs4 import BeautifulSoup
from markdownify import markdownify
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS
import anthropic

# ── Config ────────────────────────────────────────────────────────────────────

MODEL = "claude-opus-4-7"
MAX_ITERATIONS = 50
WORKSPACE = Path("./workspace")
WORKSPACE.mkdir(exist_ok=True)

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# ── Tool implementations ──────────────────────────────────────────────────────

def search_web(query: str, max_results: int = 8) -> str:
    """Search the web using DuckDuckGo."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        if not results:
            return "No results found."
        lines = []
        for i, r in enumerate(results, 1):
            lines.append(f"[{i}] {r['title']}\nURL: {r['href']}\n{r['body']}\n")
        return "\n".join(lines)
    except Exception as e:
        return f"Search error: {e}"


def fetch_page(url: str, max_chars: int = 8000) -> str:
    """Fetch and parse a web page, returning readable text."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; AgentBot/1.0)"}
        resp = httpx.get(url, headers=headers, timeout=15, follow_redirects=True)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        md = markdownify(str(soup), heading_style="ATX")
        md = "\n".join(line for line in md.splitlines() if line.strip())
        return md[:max_chars] + ("…[truncated]" if len(md) > max_chars else "")
    except Exception as e:
        return f"Fetch error: {e}"


def run_python(code: str) -> str:
    """Execute Python code and return stdout + stderr."""
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            fname = f.name
        result = subprocess.run(
            [sys.executable, fname],
            capture_output=True, text=True, timeout=30,
            cwd=str(WORKSPACE)
        )
        os.unlink(fname)
        out = result.stdout + result.stderr
        return out[:5000] if out else "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: code execution timed out (30s)"
    except Exception as e:
        return f"Execution error: {e}"


def run_shell(command: str) -> str:
    """Run a shell command and return output."""
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True,
            timeout=30, cwd=str(WORKSPACE)
        )
        out = result.stdout + result.stderr
        return out[:5000] if out else "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: command timed out (30s)"
    except Exception as e:
        return f"Shell error: {e}"


def write_file(path: str, content: str) -> str:
    """Write content to a file in the workspace."""
    try:
        p = WORKSPACE / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"Written {len(content)} chars to workspace/{path}"
    except Exception as e:
        return f"Write error: {e}"


def read_file(path: str) -> str:
    """Read a file from the workspace."""
    try:
        p = WORKSPACE / path
        content = p.read_text(encoding="utf-8")
        return content[:8000] + ("…[truncated]" if len(content) > 8000 else "")
    except Exception as e:
        return f"Read error: {e}"


def list_files(subdir: str = "") -> str:
    """List files in the workspace."""
    try:
        target = WORKSPACE / subdir if subdir else WORKSPACE
        files = list(target.rglob("*"))
        if not files:
            return "Workspace is empty."
        return "\n".join(
            str(f.relative_to(WORKSPACE)) for f in files if f.is_file()
        )
    except Exception as e:
        return f"List error: {e}"


# ── Tool definitions (for Claude) ─────────────────────────────────────────────

TOOLS = [
    {
        "name": "search_web",
        "description": "Search the internet using DuckDuckGo. Use this to find current information, news, prices, facts, etc.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "max_results": {"type": "integer", "description": "Number of results (default 8)", "default": 8}
            },
            "required": ["query"]
        }
    },
    {
        "name": "fetch_page",
        "description": "Fetch and read a web page. Returns the page content as readable text/markdown.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Full URL to fetch"},
                "max_chars": {"type": "integer", "description": "Max characters to return (default 8000)", "default": 8000}
            },
            "required": ["url"]
        }
    },
    {
        "name": "run_python",
        "description": "Execute Python code. Use for calculations, data processing, generating files, etc. Working directory is ./workspace/",
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Python code to execute"}
            },
            "required": ["code"]
        }
    },
    {
        "name": "run_shell",
        "description": "Run a shell command. Working directory is ./workspace/",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Shell command to run"}
            },
            "required": ["command"]
        }
    },
    {
        "name": "write_file",
        "description": "Save content to a file in ./workspace/. Use to save results, reports, data, code, etc.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path relative to workspace (e.g. 'report.md')"},
                "content": {"type": "string", "description": "File content"}
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "read_file",
        "description": "Read a file from ./workspace/",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path relative to workspace"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "list_files",
        "description": "List all files in ./workspace/",
        "input_schema": {
            "type": "object",
            "properties": {
                "subdir": {"type": "string", "description": "Subdirectory to list (optional)", "default": ""}
            }
        }
    }
]

TOOL_MAP = {
    "search_web": search_web,
    "fetch_page": fetch_page,
    "run_python": run_python,
    "run_shell": run_shell,
    "write_file": write_file,
    "read_file": read_file,
    "list_files": list_files,
}

SYSTEM_PROMPT = """You are an autonomous AI agent — like Manus.
The user gives you a task and you complete it fully, step by step, without asking for help.

Your capabilities:
- search_web: search the internet for any information
- fetch_page: read any web page in full
- run_python: execute Python code (for calculations, data processing, file generation)
- run_shell: run shell commands
- write_file: save files to workspace/
- read_file / list_files: manage files in workspace/

Rules:
1. Work AUTONOMOUSLY — don't ask the user questions, make decisions yourself
2. Always VERIFY your results before reporting completion
3. Save important results to files in workspace/
4. If something fails, try an alternative approach
5. Be thorough — complete the task fully, not halfway
6. At the end, give a clear summary of what you did and what files were created

Today's date: """ + datetime.now().strftime("%Y-%m-%d")


# ── Agent loop ────────────────────────────────────────────────────────────────

def run_agent(task: str) -> None:
    print(f"\n{'='*60}")
    print(f"Task: {task}")
    print(f"{'='*60}\n")

    messages = [{"role": "user", "content": task}]
    iteration = 0

    while iteration < MAX_ITERATIONS:
        iteration += 1
        print(f"[Step {iteration}] Thinking...")

        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        # Add assistant response to history
        messages.append({"role": "assistant", "content": response.content})

        # Check stop reason
        if response.stop_reason == "end_turn":
            # Extract final text
            for block in response.content:
                if hasattr(block, "text"):
                    print(f"\n{'='*60}")
                    print("DONE:")
                    print(block.text)
                    print(f"{'='*60}")
            break

        if response.stop_reason != "tool_use":
            print(f"Stopped: {response.stop_reason}")
            break

        # Process tool calls
        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                if hasattr(block, "text") and block.text:
                    print(f"  → {block.text[:200]}")
                continue

            tool_name = block.name
            tool_input = block.input
            print(f"  [{tool_name}] {json.dumps(tool_input)[:120]}")

            fn = TOOL_MAP.get(tool_name)
            if fn:
                try:
                    result = fn(**tool_input)
                except Exception as e:
                    result = f"Tool error: {traceback.format_exc()}"
            else:
                result = f"Unknown tool: {tool_name}"

            preview = result[:200].replace("\n", " ")
            print(f"  ↳ {preview}{'…' if len(result) > 200 else ''}")

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result,
            })

        messages.append({"role": "user", "content": tool_results})

    else:
        print(f"\nReached max iterations ({MAX_ITERATIONS}).")

    # Show created files
    files = list(WORKSPACE.rglob("*"))
    if any(f.is_file() for f in files):
        print(f"\nFiles in workspace/:")
        for f in files:
            if f.is_file():
                size = f.stat().st_size
                print(f"  {f.relative_to(WORKSPACE)} ({size} bytes)")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY not set.")
        print("Run: export ANTHROPIC_API_KEY=your_key_here")
        sys.exit(1)

    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
    else:
        print("Autonomous AI Agent (Manus-style)")
        print("Type your task and press Enter:\n")
        task = input("> ").strip()
        if not task:
            print("No task provided.")
            sys.exit(1)

    run_agent(task)
