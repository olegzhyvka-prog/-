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

# ── Config ────────────────────────────────────────────────────────────────────

MODEL = "claude-opus-4-7"
MAX_ITERATIONS = 50
WORKSPACE = Path("./workspace")
WORKSPACE.mkdir(exist_ok=True)
BASE_URL = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com")

# ── Auth ──────────────────────────────────────────────────────────────────────

def _get_auth() -> dict:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        return {"x-api-key": api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"}

    session_token_file = "/home/claude/.claude/remote/.session_ingress_token"
    if os.path.exists(session_token_file):
        token = Path(session_token_file).read_text().strip()
        return {"Authorization": f"Bearer {token}", "anthropic-version": "2023-06-01", "content-type": "application/json"}

    print("Error: no auth found. Set ANTHROPIC_API_KEY or run inside Claude Code.")
    sys.exit(1)

AUTH_HEADERS = _get_auth()
HTTP = httpx.Client(headers=AUTH_HEADERS, timeout=120)


def _call_api(messages: list, system: str, tools: list) -> dict:
    body = {"model": MODEL, "max_tokens": 8192, "system": system, "tools": tools, "messages": messages}
    r = HTTP.post(f"{BASE_URL}/v1/messages", json=body)
    r.raise_for_status()
    return r.json()

# ── Tool implementations ──────────────────────────────────────────────────────

def fetch_page(url: str, max_chars: int = 8000) -> str:
    """Fetch and parse a web page, returning readable text."""
    # Try Jina reader first (works on unrestricted networks)
    for fetch_url, headers in [
        (f"https://r.jina.ai/{url}", {"Accept": "text/plain", "User-Agent": "Mozilla/5.0"}),
        (url, {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}),
    ]:
        try:
            resp = httpx.get(fetch_url, headers=headers, timeout=15, follow_redirects=True)
            if resp.status_code == 200:
                if "jina.ai" in fetch_url:
                    return resp.text[:max_chars]
                soup = BeautifulSoup(resp.text, "lxml")
                for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                    tag.decompose()
                md = markdownify(str(soup), heading_style="ATX")
                md = "\n".join(line for line in md.splitlines() if line.strip())
                return md[:max_chars] + ("…[truncated]" if len(md) > max_chars else "")
        except Exception:
            continue
    return f"Could not fetch {url} — network restricted in this environment."


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
        return "\n".join(str(f.relative_to(WORKSPACE)) for f in files if f.is_file())
    except Exception as e:
        return f"List error: {e}"


# ── Tool definitions ──────────────────────────────────────────────────────────

# Anthropic built-in web search (runs on Anthropic's servers — no network restriction)
WEB_SEARCH_SERVER_TOOL = {"type": "web_search_20250305", "name": "web_search"}

CUSTOM_TOOLS = [
    {
        "name": "fetch_page",
        "description": "Fetch and read a full web page. Use after web_search to get the full content of a URL.",
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

ALL_TOOLS = [WEB_SEARCH_SERVER_TOOL] + CUSTOM_TOOLS

CUSTOM_TOOL_MAP = {
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
- web_search: search the internet in real-time (runs on Anthropic servers — always works)
- fetch_page: read the full content of a web page
- run_python: execute Python code (calculations, data processing, file generation)
- run_shell: run shell commands
- write_file: save files to workspace/
- read_file / list_files: manage files in workspace/

Rules:
1. Work AUTONOMOUSLY — don't ask the user questions, make decisions yourself
2. Use web_search for any information you need from the internet
3. Always VERIFY your results before reporting completion
4. Save important results to files in workspace/
5. If something fails, try an alternative approach
6. Be thorough — complete the task fully, not halfway
7. At the end, give a clear summary of what you did and what files were created

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

        resp = _call_api(messages, SYSTEM_PROMPT, ALL_TOOLS)
        content = resp["content"]
        stop_reason = resp["stop_reason"]

        # Show any web searches that happened server-side
        for block in content:
            btype = block.get("type", "")
            if btype == "server_tool_use":
                q = block.get("input", {}).get("query", "")
                print(f"  [web_search] {q}")
            elif btype == "web_search_tool_result":
                results = block.get("content", [])
                count = len(results) if isinstance(results, list) else "?"
                print(f"  ↳ Got {count} search results")

        # Add full assistant response to history (including server tool blocks)
        messages.append({"role": "assistant", "content": content})

        if stop_reason == "end_turn":
            for block in content:
                if block.get("type") == "text" and block.get("text"):
                    print(f"\n{'='*60}")
                    print("DONE:")
                    print(block["text"])
                    print(f"{'='*60}")
            break

        if stop_reason != "tool_use":
            print(f"Stopped: {stop_reason}")
            break

        # Execute custom tools
        tool_results = []
        has_custom_tool = False
        for block in content:
            if block.get("type") == "text" and block.get("text"):
                print(f"  → {block['text'][:200]}")
                continue
            if block.get("type") != "tool_use":
                continue

            has_custom_tool = True
            tool_name = block["name"]
            tool_input = block["input"]
            print(f"  [{tool_name}] {json.dumps(tool_input)[:120]}")

            fn = CUSTOM_TOOL_MAP.get(tool_name)
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
                "tool_use_id": block["id"],
                "content": result,
            })

        if tool_results:
            messages.append({"role": "user", "content": tool_results})
        elif not has_custom_tool:
            # Only server tools were used — continue without user turn
            continue

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
