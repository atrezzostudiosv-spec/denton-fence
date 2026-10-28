# Denton Fence — Phase 4 Implementation Plan
State: IN PROGRESS (planning and approved source baseline), 2026-10-28.

## Scope and non-negotiables
- Home V1 visual direction explicitly approved; preserve its layout, typography, colour, original-image placement, and native-scroll rhythm.
- Develop directly in Atrezzo; no Gemini or external generative handoffs.
- Build from the supplied approved ZIP prototype with separate shared CSS/JS, semantic HTML, responsive navigation, and a 15-route architecture. Do not present an unfinished navigation as functional.
- Original six pages: Home, About Us, Services, Specials, Gallery, Contact.
- Nine individual services: Wood Privacy, Ornamental Iron, Chain Link, Ranch Style, Vinyl, Fence Staining, Fence Repairs, Driveway Gates, Gate Operators.
- Preserve all verified commercial facts; distinguish owner's 35+ years experience from company age. Specials must not be labelled current until verified.
- New internal pages use their own editorial composition, not cloned Home sections.
- Responsive checks at 375, 768, 1024, 1440 and selected intermediate widths; keyboard navigation, reduced motion, focus states, contrast, anchor/scroll.
- Demo and previews noindex until publication explicitly authorized; robots/OG/metadata per route after commercial validation.
- No public repo upload of original business images until license/permission for reuse is verified; source graphics can stay local/private in design review in the meantime.

## First implementation slice
1. Audit approved preview source and current main branch before any code changes.
2. Establish maintainable frontend foundation and working internal route skeleton without copying stale template UI.
3. Port approved Home composition and interactions unchanged, with asset provenance recorded and safe image strategy.
4. Build services and other routes with full source-grounded information; validate form destination and test submits before claiming operational status.
5. Browser visual and functional QA, then publish demo only with suitable permissions and noindex.

## Current repository condition
At approval time repo is PUBLIC. GitHub Pages may be user-configured, but deployment and source availability have not been independently checked. Do not equate repository writes with live publication.