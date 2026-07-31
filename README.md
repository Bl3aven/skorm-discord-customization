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

## Installation

1. Download [`TropicalSkorm.theme.css`](TropicalSkorm.theme.css).
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

The repository includes an optional GitHub Actions workflow that can synchronize
`main.png` from a private source URL stored in the
`NEXTCLOUD_MAIN_URL` repository secret. The source URL is never committed.

## Customizing one server icon

Copy [`snippets/server-icon.template.css`](snippets/server-icon.template.css)
into BetterDiscord's **Custom CSS** editor, then replace:

- `YOUR_SERVER_ID` with the Discord server ID
- `YOUR_ICON_URL` with a direct HTTPS image or animated image URL

This only changes the icon in your own Discord client. It does not modify the
server's real icon for other members.

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
