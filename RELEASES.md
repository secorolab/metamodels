# Publishing metamodel releases

Stable tags named `vMAJOR.MINOR.PATCH` publish frozen `.json`, `.ttl`, and license files,
including recursively pinned submodules. The highest numeric stable version supplies `/stable/`.
`/latest/` and unversioned URLs track main, including unreleased changes. Prereleases are excluded.
All versions are rebuilt into a single Pages artifact on each deployment;
historical browser presentation follows the current templates on gh-pages.

Before the first release:

- Keep GitHub Pages configured for GitHub Actions.
- Allow gh-pages, main, and stable version tags in the github-pages deployment environment.
- Protect release tags against updates and deletion. Never move or delete a published release tag:
  deployments reconstruct snapshots from these tags.
- Merge the website changes into gh-pages and install `.github/workflows/publish-model-updates.yml`
  on main, then create and push the first stable tag.
  Without stable tags, root and `/latest/` still publish main; `/stable/` and its dropdown option
  appear after the first stable release.
- Verify the university domain serves nested paths such as `/metamodels/v1.0.0/`.

Push a new stable tag to publish a release. Manual dispatch rebuilds all releases.
Every push to main refreshes `/latest/`, unversioned model files, and their browsers;
`/stable/` continues to follow the highest stable tag. Existing RDF namespace IRIs remain unchanged.

The main-branch trigger calls the reusable publishing workflow on gh-pages.
Changes to gh-pages and manual dispatch also rebuild the site. The old branch-sync workflow is no longer needed.

Local assembly: `git fetch origin +refs/heads/main:refs/remotes/origin/main --tags`,
then `python3 scripts/assemble_releases.py` (requires access to submodule repositories).
Output is `_release_site/`; configure Jekyll with baseurl `/metamodels` when building locally.
The Pages build configures the deployment base URL.

Checks: `python3 -m unittest discover -s tests -p test_release_versions.py`.
