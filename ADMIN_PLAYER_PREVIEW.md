# Spider Net Admin & Player — Preview

## Purpose
`admin.html` is an early catalog-editing prototype and a direct-video playback test page. It is separate from the main design at `index.html`.

## Included
- Add, edit, delete, search, and filter catalog entries.
- Restrict poster/video links to HTTP or HTTPS.
- Native HTML5 video player with mobile `playsinline`.
- Import/export JSON for a local backup.
- Link to `connect.html` to open the real Jellyfin web interface hosted on the LAN.

## Limitations — important
- Data is saved in this browser's `localStorage`; it is not shared with other devices or visitors.
- There is no login, authorization system, shared database, or integration with the Jellyfin API in this prototype.
- Do not enter passwords, API keys, or credentials in this page.
- Direct video URLs only work when the URL is reachable and the server supports browser playback and range requests.
- Only store or stream content you are authorized to host and distribute.

## Preview paths
- Main design: `/spider-net-entertainment/`
- Local-server entry page: `/spider-net-entertainment/connect.html`
- Local admin prototype: `/spider-net-entertainment/admin.html`

GitHub Pages serves static files; it does not run Jellyfin or a shared backend. Follow `LAN_DEPLOYMENT_AR.md` for server setup.
