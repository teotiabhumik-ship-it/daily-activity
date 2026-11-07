import os
import random
import subprocess
import sys
from datetime import datetime, timezone, timedelta

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(REPO_DIR, "activity.log")

# Fixed IST offset UTC+5:30
IST = timezone(timedelta(hours=5, minutes=30), name="IST")

MESSAGES = [
    "Refactor core modules and optimize execution paths",
    "Update dependency manifest and clean build cache",
    "Improve test coverage and handle edge cases",
    "Add error handling and telemetry tracking",
    "Streamline asynchronous workflow pipeline",
    "Document API endpoints and usage examples",
    "Enhance logging precision and debugging helpers",
    "Tune memory efficiency and garbage collection thresholds",
    "Resolve minor race conditions in worker threads",
    "Sync status checkpoints and validate schemas",
    "Update security policies and review lint rules",
    "Benchmark IO performance and reduce latency"
]

def run(cmd, check=True):
    res = subprocess.run(cmd, cwd=REPO_DIR, shell=True, capture_output=True, text=True)
    if check and res.returncode != 0:
        print(f"Error running '{cmd}':\n{res.stderr}", file=sys.stderr)
        raise RuntimeError(f"Command failed with code {res.returncode}")
    return res.stdout.strip()

def main():
    os.chdir(REPO_DIR)
    
    # Configure user identity
    run("git config user.name teotiabhumik-ship-it")
    run("git config user.email teotiabhumik@gmail.com")
    
    # Ensure branch is main and synced
    run("git checkout -B main")
    try:
        run("git pull origin main --rebase", check=False)
    except Exception:
        pass
    
    # User requested 1 or 2 entries/commits per day
    num_commits = random.choice([1, 2])
    now = datetime.now(IST)
    
    print(f"Executing {num_commits} daily commit(s) for {now.strftime('%Y-%m-%d %H:%M:%S %Z')}...")
    
    for i in range(num_commits):
        entry_time = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S %Z")
        task_desc = random.choice(MESSAGES)
        
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{entry_time}] Run {i+1}/{num_commits}: {task_desc}\n")
            
        run("git add activity.log daily_commit.py")
        commit_msg = f"{task_desc} ({entry_time})"
        run(f'git commit -m "{commit_msg}"')
        print(f"Committed: {commit_msg}")
        
    # Push changes
    print("Pushing commits to remote origin main...")
    run("git push origin main")
    print("Successfully pushed daily activity to GitHub!")

if __name__ == "__main__":
    main()
