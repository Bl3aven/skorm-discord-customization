# SKORM Discord Customization

Auditable BetterDiscord themes, animated backgrounds and SKORM server icons with a live
Nextcloud synchronizer. The live edition applies the active design to every
connected client within a few seconds, but only while SKORM is open.

| Theme | Visual identity | Download |
|---|---|---|
| Cyberpunk | Neon pulse, rain and scanline glitches | [`SkormCyberpunk.theme.css`](https://github.com/Bl3aven/skorm-discord-customization/releases/latest/download/SkormCyberpunk.theme.css) |
| Galaxy | Star warp and violet cosmic glow | [`SkormGalaxy.theme.css`](https://github.com/Bl3aven/skorm-discord-customization/releases/latest/download/SkormGalaxy.theme.css) |
| Greek | Moving sun rays, mist and golden particles | [`SkormGreek.theme.css`](https://github.com/Bl3aven/skorm-discord-customization/releases/latest/download/SkormGreek.theme.css) |
| Hell | Rising embers, heat glow and red smoke | [`SkormHell.theme.css`](https://github.com/Bl3aven/skorm-discord-customization/releases/latest/download/SkormHell.theme.css) |
| Tropical | Drifting mist, fireflies and green halo | [`SkormTropical.theme.css`](https://github.com/Bl3aven/skorm-discord-customization/releases/latest/download/SkormTropical.theme.css) |
| Live | Active global Nextcloud design | [`SkormDynamic.theme.css`](https://github.com/Bl3aven/skorm-discord-customization/releases/latest/download/SkormDynamic.theme.css) |

![Active SKORM background](assets/main.png)

## Live installation

The live edition needs two small, readable files:

1. Download [`SkormDynamic.theme.css`](https://github.com/Bl3aven/skorm-discord-customization/releases/latest/download/SkormDynamic.theme.css).
2. Download [`SkormThemeSync.plugin.js`](https://github.com/Bl3aven/skorm-discord-customization/releases/latest/download/SkormThemeSync.plugin.js).
3. Copy the CSS file to **Settings → BetterDiscord → Themes → Open Themes Folder**.
4. Copy the plugin to **Settings → BetterDiscord → Plugins → Open Plugins Folder**.
5. Enable `SkormDynamic` and `SkormThemeSync`.

On Windows, the folders are:

```text
%appdata%\BetterDiscord\themes
%appdata%\BetterDiscord\plugins
```

`TropicalSkorm.theme.css` remains available as a legacy filename for existing
installations. It contains the same standalone CSS as `SkormDynamic`.

## How live synchronization works

`/theme appliquer` writes the active selection to Nextcloud, then SKORMBOT
publishes a read-only atomic snapshot at
`https://skormdemo.tournayre.ovh/theme-live/`. The synchronizer:

- polls the small public `theme-live/active.json` state every three seconds;
- downloads the palette only when the state version changes;
- selects the animated WebP or static PNG declared by SKORMBOT;
- updates CSS variables without reloading Discord;
- activates the background, palette and transparent panels only on the SKORM
  server (`1523407172514349097`);
- keeps the matching animated SKORM icon visible in the server rail while
  browsing direct messages or another server;
- adds that version to the background and logo URLs, bypassing browser and
  reverse-proxy caches.

The GitHub Actions workflow still mirrors the active assets into this
repository as a backup, but live clients do not wait for GitHub Actions or the
GitHub raw-content cache.

Discord navigation is detected locally from the `/channels/<guild-id>/...`
route. No Discord message, token or account data is inspected.

The plugin performs GET requests only to this public read-only HTTPS endpoint.
The editable Nextcloud share token is never distributed. The plugin does not
read Discord messages, credentials or tokens, and it does not send data
anywhere. Its complete source is
[`SkormThemeSync.plugin.js`](SkormThemeSync.plugin.js).

## Fixed themes

The five named themes do not require the synchronizer. Each `.theme.css` is
standalone: the shared layout and palette are embedded at build time to avoid
Chromium rejecting GitHub raw CSS served as `text/plain; nosniff`.

Their backgrounds are seamless 1280×720 animated WebP loops: 96 frames,
24 FPS and four seconds. The original PNG posters remain available as
low-resource fallbacks.

To rebuild and verify all generated files:

```bash
python scripts/build_themes.py
python scripts/build_themes.py --check
python scripts/build_animated_backgrounds.py
node --check SkormThemeSync.plugin.js
```

## Server icon scope

The bundled animated icon targets the `SKORM - Agency` guild ID. It changes
the server rail icon locally for people using one of these themes; it does not
replace the official Discord server icon for members without BetterDiscord.

To target another server, use
[`snippets/server-icon.template.css`](snippets/server-icon.template.css).

## Compatibility

- BetterDiscord Stable
- Discord dark themes
- Windows, macOS and Linux

Discord class names can change over time. If a Discord update breaks a panel,
open an issue with a screenshot and the affected Discord version.

## License

The theme code is released under the [MIT License](LICENSE).
The SKORM artwork is covered by the terms in
[`ASSET-LICENSE.md`](ASSET-LICENSE.md).

## Disclaimer

SKORM customization is an independent community project. It is not affiliated
with or endorsed by Discord or BetterDiscord.
