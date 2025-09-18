Title: Investigate replacing pip with uv for dependency management

Story:
As a development team,
we want to research and evaluate using uv as a replacement for pip in our Python projects,
so that we can determine whether adopting uv will improve performance, reproducibility, and developer experience.

🎯 Acceptance Criteria

 Document key differences between pip and uv (speed, lockfiles, reproducibility, compatibility).

 Verify compatibility of uv with our existing workflows:

requirements.txt–based installs

Virtual environment creation

Editable installs (pip install -e .)

CI/CD pipelines

Private package indexes (if applicable)

 Create a prototype migration of one existing project from pip → uv:

Option A: Use uv pip sync with current requirements.txt

Option B: Convert to pyproject.toml + uv.lock

 Document setup steps for local development and CI.

 Identify risks, blockers, or incompatibilities (e.g., tooling that only expects pip).

 Provide a recommendation:

Proceed with uv fully

Use uv as a drop-in speedup only

Stay with pip

📚 Research Tasks

Install uv locally and test on small sandbox project.

Measure install speed vs pip (cold + cached).

Evaluate lockfile behavior and reproducibility across OS (Linux, Windows, Mac).

Test uv in CI pipeline (replace pip install -r requirements.txt with uv sync or uv pip sync).

Check community adoption, stability, and maintenance of uv.

Summarize pros/cons and migration path in a short report.