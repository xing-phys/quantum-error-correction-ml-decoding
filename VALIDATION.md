# Validation record

Local validation for the 23 October 2026 research edition:

- Quarto 1.10.18 successfully rendered all 20 HTML pages and the 140-page combined PDF.
- All 92 bibliography entries parse and resolve; 199 source labels are unique and resolve.
- The local publication checker verified every HTML link, fragment, image, script, PDF download, and search index against its target.
- All 2,158 rendered mathematical expressions parsed successfully with MathJax 3.2.2 and the book's shared macros. This is a syntax check, complemented by independent scientific review.
- Representative PDF pages were rendered with Poppler and visually reviewed for title, mathematics, code, figures, solutions, and bibliography layout.
- Dependency-free Julia tests exhaust all 128 X-error patterns of the Steane example and verify GF(2) solves, commutation, stabilizer equivalence, and product-code dimensions.
- Julia and Python exact probabilities agree across the saved parameter grid. JavaScript's interactive posterior calculation agrees with the same oracle, including probability endpoints.
- The neural example reached the exact optimum for its explicitly defined seven-qubit mixture model; independent testing recorded 7,421 failures in 100,000 shots. This is a pedagogical result, not a scaling claim.
- The circuit-level example completed 300,000 shots across 15 distance/noise points; counts, seeds, versions, and Wilson intervals are checked into `data/surface-memory.csv`.
- All chapter-owned executable demonstrations were run by their authors/reviewers. Independent reviews checked the qLDPC hypotheses, noise conventions, decoder definitions, diffusion identities, and benchmark interpretation.
- `node --check`, Python compilation, interactive numerical checks, and `git diff --check` pass.

Browser automation was unavailable in this session. HTML was checked through static structure, local HTTP responses, equation parsing, and numerical unit checks; complete visual and interaction testing in a real browser remains an explicit verification limit. The responsive layout, dark theme, search UI, and keyboard controls should receive browser QA on future revisions.

The GitHub Actions workflow repeats HTML/PDF rendering, source/scientific/publication checks, and the JavaScript numerical checks on pushes to `main`. Numerical data regeneration remains explicit, preventing stochastic rebuilds of the published edition.
