# Changelog

All notable changes to SKORM Discord Customization are documented in this
file.

## 2.0.0 — 2026-07-31

- Rename the public project to `skorm-discord-customization`.
- Generate every BetterDiscord theme as standalone CSS so Chromium no longer
  rejects `raw.githubusercontent.com` CSS imports served as `text/plain`.
- Add `SkormDynamic.theme.css` as the general live theme name while preserving
  `TropicalSkorm.theme.css` for existing installations.
- Add the auditable `SkormThemeSync` companion plugin.
- Poll Nextcloud state every three seconds and use versioned asset URLs so
  every connected client applies the new background, logo and palette without
  reloading Discord or waiting for GitHub Actions.

## 1.6.0 — 2026-07-31

- Support the dynamic Nextcloud catalogue managed by SKORMBOT.
- Synchronize unknown themes with both `logos/main.webp` and
  `palettes/main.css`.
- Reduce the scheduled synchronization interval from 30 to 5 minutes.

## 1.5.0 — 2026-07-31

- Publish Cyberpunk, Galaxy, Greek, Hell and Tropical as five independent
  BetterDiscord theme files.
- Add fixed public backgrounds and matching animated logos for every theme.
- Extract the shared Discord layout into `SkormCore.css`.
- Synchronize the dynamic theme's accent palette with the recognized design.

## 1.4.0 — 2026-07-31

- Add five animated SKORM logos matching the Cyberpunk, Galaxy, Greek, Hell
  and Tropical backgrounds.
- Select the active logo automatically when `main.png` matches a known design.
- Add `assets/server-icon-main.webp` as the stable active-logo URL.
- Fall back to Nextcloud `logos/main.webp` for new or modified designs.

## 1.3.0 — 2026-07-31

- Add the animated modern SKORM icon.
- Apply it locally to the `SKORM - Agency` entry in the Discord server rail.
- Target the exact Discord guild ID for reliable matching.

## 1.2.0 — 2026-07-31

- Publish the standalone BetterDiscord theme.
- Increase background visibility through lighter translucent panels.
- Serve the public background from the stable `assets/main.png` path.
- Add an optional single-server icon customization snippet.
- Add a private Nextcloud-to-GitHub synchronization workflow.
