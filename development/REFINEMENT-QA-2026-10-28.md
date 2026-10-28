# Denton Fence — Design Refinement QA 2026-10-28

**Requested changes integrated, with email delivery still pending verification.**

## Visual and interaction changes
1. All 15 HTML routes use assets/refinements.css and assets/refinements.js; old arrow text removed in favor of drawn icons.
2. Overlays over hero, services photographs, cinematic chapters, background-image CTA and image captions use black/charcoal, not the previous green.
3. `assets/app.js`: native-scroll zoom works on desktop, tablets and phones; subtle text entry and no scroll hijacking; prefers-reduced-motion respected.
4. CTA design uses asymmetric editorial button treatment, hover underline and small iconography.
5. Inner-page pre-footer CTAs use full-bleed original photography with dark overlays. Home retains its photograph.
6. Home 'Our Work' moved to immediately after owner/story content; photographs composed in an editorial gallery.
7. Old Jotform embed removed. The contact page includes a bespoke accessible inline form, and `Request a Quote` CTAs open a responsive native dialog.
8. FormSubmit preview receiver configured to atrezzostudiosv@gmail.com with clear user-facing disclosure. Native HTML POST fallback works without JS. Network errors preserve typed values. Timed out AJAX requests abort after 18 s.

## Test evidence
- Initial false-positive gallery placeholder fixed in test harness (no production gallery image issue).
- Branch refinement QA **304/304 passed**: https://github.com/atrezzostudiosv-spec/denton-fence/actions/runs/40681861944
- Live GitHub Pages regression **304/304 passed**: https://github.com/atrezzostudiosv-spec/denton-fence/actions/runs/40682178984
- Follow-on form timeout safeguard regression **passed**: https://github.com/atrezzostudiosv-spec/denton-fence/actions/runs/40682689339
- PR #2: https://github.com/atrezzostudiosv-spec/denton-fence/pull/2
- PR #3: https://github.com/atrezzostudiosv-spec/denton-fence/pull/3
- Original 15-page/54-photo live QA previously passed.

## The one unresolved operational blocker
One synthetic FormSubmit POST sent from GitHub CI received **no HTTP response** before a 35-second read timeout; the provider's receipt and inbox delivery remain unproven.
Probe evidence: https://github.com/atrezzostudiosv-spec/denton-fence/actions/runs/40682491860
Do not claim a live contact form is production-ready. If retries to FormSubmit remain unreliable, connect a user-authorized verified endpoint. Do not simulate success.

## Publication safety
All 15 routes remain noindex; demo is publicly viewable by URL but has not been authorized for final client launch.
Before completion, verify destination mailbox receipt, client data, performance, accessibility, legal/privacy pages and production SEO.