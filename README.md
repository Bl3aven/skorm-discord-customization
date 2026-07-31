# TropicalSkorm

A dark and translucent BetterDiscord theme built around the tropical SKORM
visual identity.

![TropicalSkorm background](assets/main.png)

## Features

- Full-window tropical background
- Readable translucent chat, member and navigation panels
- Green accent colors matching the SKORM artwork
- Lightweight standalone CSS with no plugin dependency
- Remotely updated `main.png` background
- Optional per-server icon customization snippet
- Animated modern icon for the `SKORM - Agency` server rail entry
- Automatic animated-logo matching for the five bundled visual designs

## Installation

1. Download the latest
   [`TropicalSkorm.theme.css`](https://github.com/Bl3aven/tropical-skorm-theme/releases/latest/download/TropicalSkorm.theme.css).
2. Open Discord and go to **Settings → BetterDiscord → Themes**.
3. Select **Open Themes Folder**.
4. Copy `TropicalSkorm.theme.css` into that folder.
5. Enable **TropicalSkorm**.

The BetterDiscord theme folder on Windows is:

```text
%appdata%\BetterDiscord\themes
```

## Updating the background

The public theme always loads:

```text
assets/main.png
```

Replacing that file while keeping the same name updates the background for
everyone after GitHub's cache refresh and a Discord reload (`Ctrl+R`).

The repository synchronizes `main.png` and its matching animated logo from
Nextcloud approximately every 30 minutes. The private source URLs are stored in
repository secrets and are never committed.

For the five known designs, the workflow compares the SHA-256 of `main.png`
with [`assets/logos/design-map.json`](assets/logos/design-map.json) and selects
the corresponding WebP automatically. For an unknown or modified design, place
its animated logo at `logos/main.webp` in Nextcloud; this becomes the manual
fallback. Discord always loads the stable public path:

```text
assets/server-icon-main.webp
```

## Customizing one server icon

Copy [`snippets/server-icon.template.css`](snippets/server-icon.template.css)
into BetterDiscord's **Custom CSS** editor, then replace:

- `YOUR_SERVER_ID` with the Discord server ID
- `YOUR_ICON_URL` with a direct HTTPS image or animated image URL

This only changes the icon in your own Discord client. It does not modify the
server's real icon for other members.

The bundled `SKORM - Agency` customization uses
[`assets/server-icon-main.webp`](assets/server-icon-main.webp) and targets that
server's exact Discord guild ID.

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

TropicalSkorm is an independent community theme. It is not affiliated with or
endorsed by Discord or BetterDiscord.
