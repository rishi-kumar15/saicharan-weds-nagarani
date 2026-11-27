# Wedding Website (local mirror)

Offline, runnable mirror of the Dev & Ananya wedding invitation from `www.dreamsinvite.com`.

## Quick start (Windows)

Double-click **`start.bat`** in this folder.

It starts the local server on port `8000` and opens:

```
http://localhost:8000/dev-weds-ananya098f.html?test=
```

Press `Ctrl+C` in the console window to stop the server.

## Other ways to run

From this folder:

```bat
python run.py
```

or, with a custom port:

```bat
python run.py 8080
```

If Python is not installed, use Node.js instead:

```bat
node server.js
node server.js 8080
```

Open the URL printed in the console. Use `python run.py 8080 --no-browser` if you do not want the browser opened automatically.

> Do **not** open the HTML file directly with `file://`. The site uses absolute paths such as `/_next/static/chunks/...`, so it must be served over HTTP.

## What was repaired

- Restored the original HTML pages after HTTrack mangled the Next.js/Turbopack response.
- Added the 27 template detail pages and their `.rsc` prefetch payloads so clean URLs resolve locally.
- Recreated the original chunk filenames and downloaded every CSS/JS chunk referenced by any page.
- Downloaded missing images, template previews, music, and videos, and repointed video URLs to local files.
- Substituted local images for a handful of assets that are also 404 on the live site (`hero_mockup.png` and several template backgrounds).
- Added clean-URL mappings, `.rsc` routing, HTTP `Range` support for media, and `browserconfig.xml`.
- Kept the original HTTrack HTML files in `hts-cache\original-html-backup` as a backup.

## Entry pages

| Page | URL |
| --- | --- |
| Invitation (main entry) | `/dev-weds-ananya098f.html?test=` |
| Home | `/` or `/index.html` |
| Dev & Ananya | `/dev-weds-ananya.html` |
| Ethan & Lily | `/ethan-weds-lily.html` |
| Templates | `/templates7f3d.html` |
| Services | `/services.html` |
| Contact | `/contact.html` |
| Privacy | `/privacy.html` |
| Refund | `/refund.html` |
| Template detail pages | `/<template-slug>.html` (27 included) |

## Troubleshooting

- **Port already in use:** pass another port, for example `python run.py 8080`.
- **Blank page:** make sure you are using one of the launchers above, not opening the file directly. Press `Ctrl+F5` to clear the browser cache.
- **Video/audio does not seek:** both launchers support HTTP Range requests; use one of them instead of another static server.
- **Python not found:** run `node server.js` instead.

## Verification

Both launchers were tested in headless Chrome across all 39 HTML pages. There are no local 404s and no broken images. The main invitation renders fully; the only console warning is a React hydration mismatch on `/advait-weds-ishani.html`, which also occurs on the live site.
