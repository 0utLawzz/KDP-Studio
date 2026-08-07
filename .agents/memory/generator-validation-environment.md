---
name: Generator validation environment
description: Environment setup requirements for running the Python generator matrix and API workflow.
---

The generator matrix requires the declared Python requirements (`reportlab` and
`pillow`) and the workspace Node dependencies before workflow verification.
Using the package installer can create root-level `main.py`, `pyproject.toml`,
and `uv.lock`; these are environment artifacts unless the project explicitly
adopts uv.

**Why:** A clean imported workspace may have neither Python packages nor
`node_modules`, causing validation and workflow checks to fail before reaching
application code.

**How to apply:** Install from the existing requirements and lockfiles, remove
only installer-generated root artifacts that are not part of the project, and
verify the final Git diff before committing.