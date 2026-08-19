from github import Github
from github import Auth
from unidiff import PatchSet
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
from models import Finding
from pydantic import ValidationError
from bandit_analysis import run_bandit

load_dotenv()

auth = Auth.Token(os.environ["GITHUB_TOKEN"])
g = Github(auth=auth)
repo = g.get_repo("K-Prakul/pr-test")

pr_number= int(os.environ["PR_NUMBER"])
pr = repo.get_pull(pr_number)
print((pr.title))

existing_comments = list(pr.get_review_comments())
already_commented = {(c.path, c.line) for c in existing_comments}

first_file = list(pr.get_files())[0]

diff_text = f"--- a/{first_file.filename}\n+++ b/{first_file.filename}\n{first_file.patch}"
patch_set = PatchSet(diff_text)
print(first_file.patch)

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

prompt = f"""You are reviewing a code diff for a pull request.

File: {first_file.filename}
Diff:
{first_file.patch}

Identify any security risks, performance issues, or missing test coverage introduced by this diff.

Return ONLY a JSON array (no markdown, no explanation) where each item has exactly these fields:
- file: string
- line: integer (the line number in the new file)
- severity: one of "low", "medium", "high"
- category: string (e.g. "security", "performance", "testing")
- message: string (a short explanation)

If there are no issues, return an empty array.
"""

model = genai.GenerativeModel("gemini-flash-lite-latest")
response = model.generate_content(prompt)
print(response.text)

data = json.loads(response.text)
findings = []
for item in data:
    try:
        findings.append(Finding(**item))
    except ValidationError as e:
        print(f"Skipped invalid finding: {e}")

for f in findings:
    print(f)

commit = pr.get_commits().reversed[0]


def post_finding(pr, commit, finding):
    pr.create_review_comment(
        body=finding.message,
        commit=commit,
        path=finding.file,
        line=finding.line,
        side="RIGHT"
    )

bandit_findings = run_bandit(first_file.filename)

all_findings = findings + bandit_findings

for finding in all_findings:
    if (finding.file, finding.line) in already_commented:
        print(f"Skipping duplicate: {finding.file}:{finding.line}")
        continue
    print(f"Posting: file={finding.file}, line={finding.line}, message={finding.message}")
    try:
        post_finding(pr, commit, finding)
    except Exception as e:
        print(f"Failed to post finding: {e}")