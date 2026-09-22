import os
import requests
from crewai import Agent, Crew, Process, Task

# --- Custom Tool: GitHub Repo Metrics Collector ---
def get_github_metrics(repo_full_name: str) -> dict:
    """Fetches basic repository stats from GitHub REST API."""
    url = f"https://api.github.com/repos/{repo_full_name}"
    headers = {}
    
    # Optional GitHub token for higher rate limits
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
        
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return {"error": f"Failed to fetch data: {response.status_code}"}
        
    data = response.json()
    return {
        "name": data.get("full_name"),
        "stars": data.get("stargazers_count"),
        "forks": data.get("forks_count"),
        "open_issues": data.get("open_issues_count"),
        "license": data.get("license", {}).get("spdx_id", "Unknown"),
        "archived": data.get("archived", False),
        "description": data.get("description")
    }

# --- 1. Agents Definition ---
data_collector = Agent(
    role="OSPO Metrics Analyst",
    goal="Collect and evaluate quantitative health and maintenance risk of open source repositories.",
    backstory="You are an expert data analyst in open source governance, skilled at analyzing repository metrics, activity levels, and licensing risks.",
    verbose=True
)

partnership_advisor = Agent(
    role="OSPO Partnership & Strategy Lead",
    goal="Synthesize repo metrics into actionable enterprise partnership recommendations and ROI evaluations.",
    backstory="You are an OSPO director experienced in building sustainable relationships with foundation projects, maintainers, and key ecosystem partners.",
    verbose=True
)

# --- 2. Tasks Definition ---
collect_metrics_task = Task(
    description=(
        "Analyze the project '{repo_name}'. "
        "Summarize maintenance activity, license compliance suitability, and sustainability concerns."
    ),
    expected_output="A structured summary of repository health and risk assessment.",
    agent=data_collector
)

partnership_task = Task(
    description=(
        "Using the repository health report for '{repo_name}', provide a strategic recommendation: "
        "1. Should we sponsor or partner with this project? (Tier recommendation: Foundation, Direct Sponsorship, Contributor-only) "
        "2. Identify key strategic benefits and risks for our organization."
    ),
    expected_output="An executive briefing document with clear partnership recommendations.",
    agent=partnership_advisor
)

# --- 3. Crew Execution ---
def run_ospo_engine(repo_name: str):
    crew = Crew(
        agents=[data_collector, partnership_advisor],
        tasks=[collect_metrics_task, partnership_task],
        process=Process.sequential
    )
    result = crew.kickoff(inputs={"repo_name": repo_name})
    return result

if __name__ == "__main__":
    # Example target repository
    target_repo = "kubernetes/kubernetes"
    print(f"--- Running OSPO Engine for {target_repo} ---")
    summary = run_ospo_engine(target_repo)
    print("\n--- Strategy Report ---")
    print(summary)
