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
    "Benchmark IO performance and reduce latency",
    "Optimize database indexing and query plans",
    "Modularize utility helpers and format exports",
    "Update CI/CD build matrix and action versions",
    "Fix edge-case null pointer handling",
    "Profile memory allocations under peak load",
    "Improve configuration parsing and environment fallback",
    "Refine request validation logic and sanitization",
    "Clean up deprecated helper functions and dead code",
    "Add retry mechanism with exponential backoff",
    "Format code style according to lint conventions",
    "Standardize HTTP error response structures",
    "Upgrade telemetry exporter and metric collection",
    "Optimize payload serialization and buffer sizes"
]

def run(cmd, check=True, env=None):
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    res = subprocess.run(cmd, cwd=REPO_DIR, shell=True, capture_output=True, text=True, env=full_env)
    if check and res.returncode != 0:
        print(f"Error running '{cmd}':\n{res.stderr}", file=sys.stderr)
        raise RuntimeError(f"Command failed with code {res.returncode}")
    return res.stdout.strip()

def generate_commit_times(now, num_commits):
    # Check if there was already a commit today to maintain strictly ascending chronology
    last_commit_dt = None
    try:
        last_commit_str = run("git log -1 --format=%cI", check=False)
        if last_commit_str:
            last_commit_dt = datetime.fromisoformat(last_commit_str).astimezone(IST)
    except Exception:
        last_commit_dt = None

    day_start = datetime(now.year, now.month, now.day, 0, 0, 0, tzinfo=IST)
    day_end = datetime(now.year, now.month, now.day, 23, 50, 0, tzinfo=IST)

    if last_commit_dt and last_commit_dt.date() == now.date():
        # If a commit already happened today, start after the last commit
        start_time = last_commit_dt + timedelta(minutes=random.randint(5, 20))
    else:
        # First batch of the day: start at a random morning hour (08:30 - 10:30)
        start_time = datetime(
            now.year, now.month, now.day,
            random.randint(8, 10),
            random.randint(15, 55),
            random.randint(0, 59),
            tzinfo=IST
        )

    # Target evening time between 19:30 and 22:45
    end_time = datetime(
        now.year, now.month, now.day,
        random.randint(19, 22),
        random.randint(15, 55),
        random.randint(0, 59),
        tzinfo=IST
    )

    # Boundary checks
    if start_time >= end_time:
        end_time = min(day_end, start_time + timedelta(hours=random.uniform(2, 4)))
    if start_time >= end_time:
        start_time = max(day_start, end_time - timedelta(minutes=num_commits * 10))

    total_seconds = max(1, int((end_time - start_time).total_seconds()))

    if total_seconds >= num_commits * 60:
        sec_offsets = sorted(random.sample(range(total_seconds), num_commits))
    else:
        step = max(1, total_seconds // num_commits)
        sec_offsets = sorted([
            min(total_seconds, i * step + random.randint(1, max(2, step)))
            for i in range(num_commits)
        ])

    return [start_time + timedelta(seconds=s) for s in sec_offsets]

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
    
    # Random number of commits between 1 and 10
    num_commits = random.randint(1, 10)
    now = datetime.now(IST)
    commit_times = generate_commit_times(now, num_commits)
    
    print(f"Executing {num_commits} daily commit(s) with randomized timestamps for {now.strftime('%Y-%m-%d')}...")
    
    shuffled_messages = MESSAGES.copy()
    random.shuffle(shuffled_messages)
    
    for i, commit_dt in enumerate(commit_times):
        entry_time_str = commit_dt.strftime("%Y-%m-%d %H:%M:%S IST")
        git_date_str = commit_dt.strftime("%Y-%m-%d %H:%M:%S +0530")
        task_desc = shuffled_messages[i % len(shuffled_messages)]
        
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{entry_time_str}] Run {i+1}/{num_commits}: {task_desc}\n")
            
        run("git add activity.log daily_commit.py")
        commit_msg = f"{task_desc} ({entry_time_str})"
        run(
            f'git commit --date="{git_date_str}" -m "{commit_msg}"',
            env={"GIT_COMMITTER_DATE": git_date_str}
        )
        print(f"Committed [{i+1}/{num_commits}]: {commit_msg}")
        
    # Push changes
    print("Pushing commits to remote origin main...")
    run("git push origin main")
    print("Successfully pushed daily activity to GitHub!")

if __name__ == "__main__":
    main()
