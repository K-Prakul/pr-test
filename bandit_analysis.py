import subprocess
import json
from models import Finding

def bandit_result_to_finding(result):
    return Finding(
        file=result["filename"].lstrip(".\\/"),
        line=result["line_number"],
        severity=result["issue_severity"].lower(),
        category="security",
        message=result["issue_text"]
    )

def run_bandit(filepath):
    process = subprocess.run(["bandit", "-f", "json", filepath], capture_output=True, text=True)
    data = json.loads(process.stdout)
    return [bandit_result_to_finding(r) for r in data["results"]]

findings = run_bandit("git.py")
for f in findings:
    print(f)