# Dragon Mounts 2 Wiki

The Dragon Mounts 2 project wiki starts by asking whether you play Minecraft Bedrock or Java. Bedrock has the current guides for the public v1.2.5.1 release; Java has a separate starter section ready for future guides.

- [Official CurseForge files](https://www.curseforge.com/minecraft-bedrock/addons/dragon-mounts-2/files/all)
- [Official project wiki](https://github.com/DragonMounts-Team/DragonMounts2-Bedrock/wiki)
- [Report a wiki issue](https://github.com/DragonMounts-Team/Dragon-Mounts-2-Wiki/issues/new)

## Automatic changelog

`.github/workflows/changelog.yml` runs every 6 hours (and on demand from the Actions tab), calls `tools/update-changelog.py`, and commits any new GitHub releases to `assets/releases.json`, `changelog.html` and the search index. Entries marked `"curated": true` in `assets/releases.json` keep their hand-written text. Run it locally with `python tools/update-changelog.py`.

## Look and feel

The UI uses Minecraft GUI textures from `assets/mc/` and the pixel font in `assets/fonts/`. The local editor (`Start-Wiki-Editor.bat`) shares the same style and has a **Site files** workspace for editing any file, uploading images and running the changelog update.
