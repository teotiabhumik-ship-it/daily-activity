import os
import json
import subprocess
import sys
from datetime import datetime, timezone, timedelta

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(REPO_DIR, "issues_history.json")
WORKSPACES_DIR = os.path.join(REPO_DIR, "repos")

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def run(cmd, check=True):
    res = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=REPO_DIR
    )
    if check and res.returncode != 0:
        print(f"Error running command: {cmd}\n{res.stderr}", file=sys.stderr)
        raise RuntimeError(f"Command failed with code {res.returncode}")
    return (res.stdout or "").strip()

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history(entry):
    history = load_history()
    history.append(entry)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

def get_processed_urls():
    history = load_history()
    return {h.get("url") for h in history if "url" in h}

def find_candidate_issues(label="good first issue", limit=10):
    processed = get_processed_urls()
    print(f"Searching GitHub for open, unassigned issues with label '{label}'...")
    cmd = f'gh search issues --state=open --no-assignee --label="{label}" --limit={limit + 15} --json number,title,url,repository,labels,updatedAt'
    output = run(cmd)
    issues = json.loads(output) if output else []
    
    candidates = []
    for issue in issues:
        url = issue.get("url")
        if url in processed:
            continue
        candidates.append(issue)
        if len(candidates) >= limit:
            break
            
    return candidates

def view_issue(issue_url):
    cmd = f'gh issue view "{issue_url}" --json number,title,body,repository,labels,comments,url'
    output = run(cmd)
    return json.loads(output) if output else None

def clone_or_fork(repo_name_with_owner):
    os.makedirs(WORKSPACES_DIR, exist_ok=True)
    repo_name = repo_name_with_owner.split("/")[-1]
    target_path = os.path.join(WORKSPACES_DIR, repo_name)
    
    if os.path.exists(target_path):
        print(f"Repository already cloned at {target_path}")
        return target_path
        
    print(f"Cloning {repo_name_with_owner} into {target_path}...")
    run(f'gh repo clone "{repo_name_with_owner}" "{target_path}"')
    return target_path

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--find":
        label = sys.argv[2] if len(sys.argv) > 2 else "good first issue"
        candidates = find_candidate_issues(label=label, limit=5)
        print(f"\nFound {len(candidates)} candidate issues:")
        for idx, c in enumerate(candidates, 1):
            repo = c["repository"]["nameWithOwner"]
            print(f"{idx}. [{repo}] #{c['number']}: {c['title']}")
            print(f"   URL: {c['url']}\n")
    else:
        print("Auto Issue Solver")
        print("Usage:")
        print("  python auto_issue_solver.py --find [label]")
        print("  python auto_issue_solver.py --solve <issue-url>")

if __name__ == "__main__":
    main()
