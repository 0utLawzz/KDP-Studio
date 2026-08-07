---
name: GitHub app imports
description: Replit preview registration considerations when importing a public GitHub app into an existing workspace
---

When importing a public GitHub repository that contains a Replit artifact, preserve the repository source while ensuring the artifact preview is registered in the current workspace.

**Why:** GitHub files can include artifact metadata without that metadata being registered in the current Replit workspace, leaving the app code present but the preview workflow unavailable.

**How to apply:** Verify the imported app's managed preview exists, restore the repository source into the registered artifact, install dependencies, and restart dependent API/frontend workflows before presenting the result.