# Spider Net Admin & Player — Preview

This change adds an independent Arabic RTL admin prototype at `/admin.html` without replacing the existing homepage.

## Included
- Add, edit, delete, filter, and search catalog entries.
- Safe URL allowlist limited to HTTP/HTTPS for poster and direct-video URLs.
- HTML video player with native controls and mobile `playsinline`.
- JSON export/import for a local catalog backup.
- GitHub Actions checks for required files and basic HTML safety invariants.

## Important limitations
- This is a browser-local prototype using `localStorage`; it is not authentication and does not sync between visitors or devices.
- Do not enter passwords, API keys, or private credentials.
- A shared admin system needs a trusted backend/authentication and storage, or integration with a media server such as Jellyfin.
- Video playback depends on a directly accessible, browser-compatible media URL and appropriate server CORS/range support.
- Only add media you are authorized to host and stream.

## Preview
After the branch is merged and GitHub Pages finishes publishing, open `/admin.html` on the published site. The current homepage is not modified by this branch.
