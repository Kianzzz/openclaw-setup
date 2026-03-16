#!/usr/bin/env python3
"""
openclaw-setup environment check v1.0
Scans current OpenClaw configuration and reports status of all configurable items.
Exit 0 = ready (no blocking issues), Exit 1 = blocking issues found.
Output: JSON report.
"""

import json
import os
import shutil
import subprocess
import sys

# --- Permission keys recognized by OpenClaw ---
PERMISSION_KEYS = [
    "read",       # Read files in workspace
    "write",      # Write/create files
    "exec",       # Execute shell commands
    "web",        # Web access (fetch, search)
    "mcp",        # MCP server connections
    "admin",      # Administrative operations (config, skills, cron)
]

# --- Known model providers ---
KNOWN_PROVIDERS = {
    "anthropic": ["claude-sonnet-4-5", "claude-opus-4", "claude-haiku-4-5"],
    "openai": ["gpt-4o", "gpt-4o-mini", "o3", "o4-mini"],
    "google": ["gemini-2.5-pro", "gemini-2.5-flash"],
    "custom": [],
}


def get_workspace_path():
    """Resolve workspace path from env or default."""
    env_path = os.environ.get("OPENCLAW_WORKSPACE")
    if env_path and os.path.isdir(env_path):
        return env_path
    default = os.path.expanduser("~/.openclaw/workspace")
    if os.path.isdir(default):
        return default
    return None


def get_config_path(workspace):
    """Find openclaw.json config file."""
    if not workspace:
        return None
    candidates = [
        os.path.join(os.path.dirname(workspace.rstrip("/")), "openclaw.json"),
        os.path.normpath(os.path.join(workspace, "..", "openclaw.json")),
        os.path.expanduser("~/.openclaw/openclaw.json"),
    ]
    for p in candidates:
        if os.path.isfile(p):
            return p
    return None


def load_config(config_path):
    """Load and parse openclaw.json."""
    if not config_path:
        return None
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def check_openclaw():
    """Check OpenClaw CLI availability and version."""
    path = shutil.which("openclaw")
    if not path:
        for loc in ["~/.openclaw/bin/openclaw", "/usr/local/bin/openclaw"]:
            expanded = os.path.expanduser(loc)
            if os.path.isfile(expanded) and os.access(expanded, os.X_OK):
                path = expanded
                break
    if not path:
        return {"status": "fail", "error": "openclaw CLI not found in PATH."}
    try:
        result = subprocess.run(
            [path, "--version"], capture_output=True, text=True, timeout=10
        )
        version = result.stdout.strip() or result.stderr.strip()
        return {"status": "pass", "version": version, "path": path}
    except Exception as e:
        return {"status": "warn", "path": path, "error": f"Version check failed: {e}"}


def check_config(workspace):
    """Check openclaw.json exists and is valid."""
    config_path = get_config_path(workspace)
    if not config_path:
        return {"status": "warn", "error": "openclaw.json not found."}
    config = load_config(config_path)
    if config is None:
        return {"status": "fail", "path": config_path, "error": "Invalid JSON in openclaw.json."}
    return {"status": "pass", "path": config_path}


def check_permissions(config):
    """Extract current permission settings."""
    if not config:
        return {k: None for k in PERMISSION_KEYS}
    perms_section = config.get("permissions", {})
    result = {}
    for key in PERMISSION_KEYS:
        val = perms_section.get(key)
        if isinstance(val, bool):
            result[key] = val
        elif isinstance(val, str):
            result[key] = val.lower() in ("true", "allow", "yes", "1")
        else:
            result[key] = None  # not configured
    return result


def check_models(config):
    """Extract model configuration."""
    if not config:
        return {"primary": None, "fallback": [], "maxTokens": None}
    agents = config.get("agents", {})
    defaults = agents.get("defaults", {})
    models = defaults.get("models", {})

    primary = models.get("primary") or models.get("default") or defaults.get("model")
    fallback_raw = models.get("fallback", [])
    if isinstance(fallback_raw, str):
        fallback_raw = [fallback_raw]
    max_tokens = defaults.get("maxTokens") or defaults.get("max_tokens") or config.get("maxTokens")

    return {
        "primary": primary,
        "fallback": fallback_raw,
        "maxTokens": max_tokens,
    }


def check_compaction(config):
    """Check context compaction settings."""
    if not config:
        return {"configured": False}
    compaction = config.get("compaction", {})
    if not compaction:
        # Also check under agents.defaults
        agents = config.get("agents", {})
        compaction = agents.get("defaults", {}).get("compaction", {})
    if not compaction:
        return {"configured": False}
    return {
        "configured": True,
        "strategy": compaction.get("strategy"),
        "threshold": compaction.get("threshold"),
        "model": compaction.get("model"),
    }


def check_heartbeat(config):
    """Check heartbeat configuration."""
    if not config:
        return {"configured": False}
    hb = config.get("heartbeat", {})
    if not hb or not hb.get("every"):
        return {"configured": False}
    return {
        "configured": True,
        "every": hb.get("every"),
        "target": hb.get("target"),
        "model": hb.get("model"),
        "directPolicy": hb.get("directPolicy"),
    }


def check_mcp_servers(config):
    """Check MCP server configurations."""
    if not config:
        return {"servers": [], "count": 0}
    mcp = config.get("mcp", {})
    servers = mcp.get("servers", {})
    if isinstance(servers, dict):
        server_list = list(servers.keys())
    elif isinstance(servers, list):
        server_list = [s.get("name", f"server-{i}") for i, s in enumerate(servers)]
    else:
        server_list = []
    return {"servers": server_list, "count": len(server_list)}


def check_cron(config):
    """Check cron job configurations."""
    if not config:
        return {"jobs": [], "count": 0}
    cron = config.get("cron", {})
    jobs = cron.get("jobs", [])
    if isinstance(jobs, list):
        job_names = [j.get("name", j.get("id", f"job-{i}")) for i, j in enumerate(jobs)]
    else:
        job_names = []
    return {"jobs": job_names, "count": len(job_names)}


def check_security(config):
    """Check security-related settings."""
    if not config:
        return {
            "dm_policy": None,
            "spending_limit": None,
            "thinking": None,
            "log_sanitize": None,
            "skill_policy": None,
        }
    security = config.get("security", {})
    dm = config.get("dm", {})
    thinking = config.get("thinking", {})

    return {
        "dm_policy": dm.get("policy") or security.get("dmPolicy"),
        "spending_limit": security.get("spendingLimit") or config.get("spendingLimit"),
        "thinking": thinking.get("level") or security.get("thinkingLevel"),
        "log_sanitize": security.get("logSanitize"),
        "skill_policy": security.get("skillPolicy"),
    }


def check_clawhub():
    """Check clawhub CLI availability."""
    path = shutil.which("clawhub")
    if path:
        return {"status": "pass", "path": path}
    for loc in ["~/.openclaw/bin/clawhub", "/usr/local/bin/clawhub"]:
        expanded = os.path.expanduser(loc)
        if os.path.isfile(expanded) and os.access(expanded, os.X_OK):
            return {"status": "pass", "path": expanded}
    return {
        "status": "warn",
        "error": "clawhub CLI not in PATH. Skill installation via clawhub unavailable.",
    }


def check_openclaw_soul(workspace):
    """Check if openclaw-soul skills are installed."""
    if not workspace:
        return {"installed": False}
    skills_dir = os.path.join(workspace, "skills")
    evoclaw = os.path.isfile(os.path.join(skills_dir, "evoclaw", "SKILL.md"))
    self_improving = os.path.isfile(os.path.join(skills_dir, "self-improving", "SKILL.md"))

    # Also check for SOUL.md and BOOTSTRAP.md
    soul_exists = os.path.isfile(os.path.join(workspace, "SOUL.md"))
    bootstrap_exists = os.path.isfile(os.path.join(workspace, "BOOTSTRAP.md"))

    return {
        "installed": evoclaw or self_improving,
        "evoclaw": evoclaw,
        "self_improving": self_improving,
        "soul_md": soul_exists,
        "bootstrap_md": bootstrap_exists,
    }


def main():
    report = {"checks": {}, "blocking": False, "version": "1.0.0"}

    workspace = get_workspace_path()
    config_path = get_config_path(workspace)
    config = load_config(config_path) if config_path else None

    # 1. OpenClaw CLI
    oc_result = check_openclaw()
    report["checks"]["openclaw"] = oc_result
    if oc_result["status"] == "fail":
        report["blocking"] = True

    # 2. Config file
    report["checks"]["config"] = check_config(workspace)

    # 3. Permissions
    report["checks"]["permissions"] = check_permissions(config)

    # 4. Models
    report["checks"]["models"] = check_models(config)

    # 5. Compaction
    report["checks"]["compaction"] = check_compaction(config)

    # 6. Heartbeat
    report["checks"]["heartbeat"] = check_heartbeat(config)

    # 7. MCP Servers
    report["checks"]["mcp_servers"] = check_mcp_servers(config)

    # 8. Cron
    report["checks"]["cron"] = check_cron(config)

    # 9. Security
    report["checks"]["security"] = check_security(config)

    # 10. clawhub
    report["checks"]["clawhub"] = check_clawhub()

    # 11. openclaw-soul
    report["checks"]["openclaw_soul"] = check_openclaw_soul(workspace)

    # Summary
    report["workspace_path"] = workspace
    report["config_path"] = config_path
    report["ready"] = not report["blocking"]

    print(json.dumps(report, indent=2, ensure_ascii=False))
    sys.exit(1 if report["blocking"] else 0)


if __name__ == "__main__":
    main()
