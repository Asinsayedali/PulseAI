#!/usr/bin/env python3
"""
PreToolUse hook: blocks Claude Code from reading .env files.

Blocks:
  - Read tool where file_path points to .env or .env.<sensitive-variant>
  - Bash tool where the command references .env as a file argument
  - Grep tool where path targets .env

Allows:
  - .env.example, .env.template, .env.sample (safe placeholder files)
  - Any command that doesn't reference .env as a file
"""
import json
import re
import sys

# Matches .env or .env.<word> but NOT .env.example / .env.template / .env.sample
ENV_FILE_RE = re.compile(
    r'(?:^|[/\\])\.env(?:\.(?!example|template|sample)\w+)?$'
)

# Matches .env as a file argument inside a shell command
CMD_ENV_RE = re.compile(
    r'(?:^|[\s|&;<`(])(?:[^\s]*/)?\.env(?:\.(?!example|template|sample)\w+)?(?=\s|$|[|>&;`)])'
)

data = json.load(sys.stdin)
tool = data.get("tool_name", "")
inp = data.get("tool_input", {})

blocked = False

if tool == "Read":
    blocked = bool(ENV_FILE_RE.search(inp.get("file_path", "") or ""))
elif tool == "Bash":
    blocked = bool(CMD_ENV_RE.search(inp.get("command", "") or ""))
elif tool == "Grep":
    blocked = bool(ENV_FILE_RE.search(inp.get("path", "") or ""))

if blocked:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                ".env file access blocked — secrets must not enter LLM context. "
                "Use .env.example to check variable names."
            ),
        }
    }))
