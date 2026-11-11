# Dragon Mounts 2 Wiki

The Dragon Mounts 2 project wiki documents the public Minecraft Bedrock v1.2.5.1 release.

- [Official CurseForge files](https://www.curseforge.com/minecraft-bedrock/addons/dragon-mounts-2/files/all)
- [Official project wiki](https://github.com/DragonMounts-Team/DragonMounts2-Bedrock/wiki)
- [Report a wiki issue](https://github.com/DragonMounts-Team/Dragon-Mounts-2-Wiki/issues/new)

## Automatic changelog

`.github/workflows/changelog.yml` runs every 6 hours (and on demand from the Actions tab), calls `tools/update-changelog.py`, and commits any new GitHub releases to `assets/releases.json`, `changelog.html` and the search index. Entries marked `"curated": true` in `assets/releases.json` keep their hand-written text. Run it locally with `python tools/update-changelog.py`.

## Wiki features

`assets/wiki.js` adds breadcrumbs, the right-hand "On this page" list, Previous/Next links and "Edit this page" links to every guide page. It reads the page order from `assets/config.js`, so add a new page to `navigation` there and it is picked up automatically. `assets/live.js` shows new GitHub releases, pre-releases and commits immediately in the browser (cached for 10 minutes); the hourly workflow keeps the saved copies current.

## Look and feel

The site uses a flat, minecraft.net-style UI with the pixel font in `assets/fonts/`; the only game textures on the site are the dragon, egg and nest images in `textures/`. (`assets/mc/` is used only by the local editor tool.) The local editor (`Start-Wiki-Editor.bat`) shares the same style and has a **Site files** workspace for editing any file, uploading images and running the changelog update.
