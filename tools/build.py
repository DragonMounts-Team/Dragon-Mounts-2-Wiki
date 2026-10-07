#!/usr/bin/env python3
"""
Builds the DragonMounts 2 wiki into plain HTML files.

You do NOT need to run this to publish the site: the generated files are already
in the project root. Run it only if you want to change content in bulk:

    python3 tools/build.py
    python tools/build.py --url https://Grummboy2.github.io/TestWiki

Passing --url adds canonical links, social tags and a sitemap.xml.
"""
import argparse, json, os, re, html

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ap = argparse.ArgumentParser()
ap.add_argument("--url", default="", help="Public site URL, no trailing slash")
SITE_URL = ap.parse_args().url.rstrip("/")

VERSION = "1.2.5.1"
BEDROCK_VERSION = "26.40"
SITE = "DragonMounts 2 Wiki"
OFFICIAL_WIKI = "https://github.com/DragonMounts-Team/DragonMounts2-Bedrock/wiki"
OFFICIAL_DRAGONS = OFFICIAL_WIKI + "/Dragons"
OFFICIAL_ITEMS = OFFICIAL_WIKI + "/Items"
OFFICIAL_RECIPES = OFFICIAL_WIKI + "/Recipes"
OFFICIAL_BLOCKS = OFFICIAL_WIKI + "/Blocks"
OFFICIAL_FILES = "https://www.curseforge.com/minecraft-bedrock/addons/dragon-mounts-2/files/all"
DOWNLOAD_SOURCES = [
    ("CurseForge", "https://www.curseforge.com/minecraft-bedrock/addons/dragon-mounts-2"),
    ("MCPEDL", "https://mcpedl.com/dragon-mounts-2/"),
    ("Vatonage", "https://vatonage.com/mods/dragon-mounts-2"),
    ("ModBay", "https://modbay.org/mods/4446-dragon-mounts-2.html"),
]
GITHUB_RELEASES = [
    {
        "version": "2.0 Pre-Release 3.4",
        "date": "2025-10-29",
        "stage": "Pre-release",
        "tag": "2.0-Pre-Release-3.4",
        "summary": "Egg conversion and Dragon Core spawning fixes, invisible dragon fixes, shield animation fixes, and Dragon Essence removed from command and Creative visibility.",
        "changes": [
            "Restored egg conversion and fixed issues introduced in Pre-Release 3.3.",
            "Fixed dragons appearing invisible.",
            "Removed the ten-tick delay when the Dragon Core spawns a dragon.",
            "Fixed first- and third-person shield animations.",
            "Made Dragon Essence unavailable through commands and the Creative inventory.",
        ],
    },
    {
        "version": "2.0 Pre-Release 3.3",
        "date": "2025-10-28",
        "stage": "Pre-release",
        "tag": "2.0-Pre-Release-3.3",
        "summary": "Water Dragon armor display, flight, and egg conversion fixes.",
        "changes": [
            "Fixed armor display on Water Dragons.",
            "Fixed flight.",
            "Updated egg conversion.",
        ],
    },
    {
        "version": "3.7.3",
        "date": "2025-08-07",
        "stage": "Release",
        "tag": "3.7.3",
        "summary": "Vibrant Visuals support, a rare Aether Dragon, Storm Dragon particles, Nether Dragon fixes, and egg acquisition changes.",
        "changes": [
            "Added Vibrant Visuals support, a rare Aether Dragon, and new Storm Dragon particles.",
            "Fixed Nether Dragon issues and stretched textures.",
            "Removed the Ender Dragon Egg recipe; crouch-interact with flint and steel while holding a vanilla Dragon Egg to hatch an Ender Dragon.",
            "Changed the Dark Dragon Egg method: strike a Moonlight Dragon Egg on a lightning rod with lightning.",
            "Changed identifiers to the dragonmountsplus namespace.",
        ],
    },
    {
        "version": "3.7.2 Hotfix",
        "date": "2025-07-26",
        "stage": "Hotfix",
        "tag": "3.7.2-hotfix",
        "summary": "Fixes for rare Storm glow, dragon glows, the Forest Dragon, and shears enchantments; updated the rare Ender Dragon texture.",
        "changes": [
            "Fixed rare Storm glow and incorrect dragon glow display.",
            "Updated the rare Ender Dragon texture.",
            "Fixed the Forest Dragon and shears enchantments.",
        ],
    },
    {
        "version": "3.7.2",
        "date": "2025-07-25",
        "stage": "Release",
        "tag": "3.7.2",
        "summary": "Three rare dragons, dragon head blocks, Copper Dragon Armor, an updated Nether design, animated Dragon Core, faster egg hatching, and Dragon Flutes.",
        "changes": [
            "Added rare Ender, Storm, and Nether Dragons, plus their three dragon heads.",
            "Added Copper Dragon Armor and a redesigned Nether Dragon.",
            "Added an animated Dragon Core block and Emerald-assisted egg hatching.",
            "Renamed Dragon Whistles to Dragon Flutes and updated their sounds.",
            "Reduced baby dragon growl volume, organized dropped heads by species, and adjusted rare dragon frequency.",
            "Introduced a new dragon armor system.",
        ],
    },
    {
        "version": "3.7.1 Hotfix",
        "date": "2025-07-22",
        "stage": "Hotfix",
        "tag": "3.7.1-hotfix",
        "summary": "Re-added rare dragons, fixed invisible Skeleton and Wither Dragons, improved dragon head drops and placement, and fixed missing files and tooltips.",
        "changes": [
            "Re-added rare dragons and fixed invisible Skeleton and Wither Dragons.",
            "Fixed dragons dropping the correct heads; added 16 head rotations and wall placement states.",
            "Fixed missing files and removed Diamond Scissors enchantments that could duplicate items.",
            "Updated tooltips to display colors.",
        ],
    },
    {
        "version": "3.7.0 Hotfix 1",
        "date": "2025-07-20",
        "stage": "Hotfix",
        "tag": "3.7.0-hotfix.1",
        "summary": "Enabled Dragon Shears on sheep and fixed an Amulet weakness effect, Ender Dragon Head texture, and Ice Dragon nest generation; dragon head limitations remained.",
        "changes": [
            "Allowed Dragon Shears to shear sheep.",
            "Fixed the Amulet weakness effect, Ender Dragon Head texture, and Ice Dragon nest generation.",
            "The release notes listed remaining Dragon Head limitations: redstone response, shadows, diagonal ground placement, wall attachment, break particles, head size, and mouth animation while players walk.",
        ],
    },
    {
        "version": "3.7.0",
        "date": "2025-07-20",
        "stage": "Release",
        "tag": "3.7.0",
        "summary": "Added Dragon Core and Dragon Head blocks and Dragon Essence Gems; Dragon Egg textures became animated. The release notes warned that the build had bugs.",
        "changes": [
            "Added the Dragon Core block for reviving dragons and Dragon Head blocks.",
            "Added Dragon Essence Gems for use with the Dragon Core.",
            "Changed all Dragon Egg textures to animated textures.",
            "The original release notes warned that this build had bugs and could cause unexpected behavior.",
        ],
    },
]

DRAGON_ROSTER = [
    ("Aether", "Levitation", "Natural nest", "Most biomes except Mesa", "aether"),
    ("Dark", "Dark", "Lightning transformation", "Moonlight egg struck by lightning", "dark"),
    ("Enchant", "Fire", "Block transformation", "Bookshelves (Ender egg only)", "enchanted"),
    ("Ender", "Ender", "Vanilla egg", "Convert the vanilla Ender Dragon egg", "ender"),
    ("Fire", "Fire", "Natural nest", "Desert, plains, dripstone caves and plateaus", "fire"),
    ("Forest", "Poison", "Natural nest", "Forests, jungles and flower forests", "forest"),
    ("Ice", "Ice", "Natural nest", "Frozen biomes", "ice"),
    ("Moonlight", "Dark", "Natural nest", "Cold and deep oceans, and rivers", "moonlight"),
    ("Nether", "Nether", "Natural nest", "All Nether biomes", "nether"),
    ("Sculk", "Wither", "Natural nest", "Underground in the Deep Dark", "sculk"),
    ("Skeleton", "Melee only", "Natural nest", "All Nether biomes", "skeleton"),
    ("Storm", "Air", "Lightning transformation", "Water egg struck by lightning", "storm"),
    ("Sunlight", "Fire", "Natural nest", "Desert and desert hills", "sunlight"),
    ("Terra", "Fire", "Natural nest", "Mesa / Badlands", "terra"),
    ("Water", "Water", "Natural nest", "Oceans and swamps", "water"),
    ("Wither", "Wither", "Lightning transformation", "Skeleton egg struck by lightning", "wither"),
    ("Zombie", "Poison", "Natural nest", "All Nether biomes", "zombie"),
]

DRAGON_APPEARANCES = [
    ("Aether", [("Aethra", "aether_normal"), ("Breeze", "aether_breeze"), ("Wind", "aether_wind")]),
    ("Dark", [("Bloodmoon", "dark_bloodmoon"), ("Demon", "dark_demon"), ("Imp", "dark_imp"), ("Underworld", "dark_underworld")]),
    ("Forest", [("Nature", "forest_base"), ("Cold", "forest_cold"), ("Jungle", "forest_jungle"), ("Warm", "forest_dry")]),
    ("Ice", [("Alpine", "ice_alpine"), ("Frost", "ice_frost"), ("Iceberg", "ice_iceberg")]),
    ("Nether", [("Volcanic", "nether_volcanic"), ("Magma", "nether_ash"), ("Soul Fire", "nether_soul_fire")]),
    ("Sculk", [("Warden", "sculk_warden"), ("Amethyst", "sculk_amythest"), ("Beta", "sculk_mutated")]),
    ("Skeleton", [("Skeleton", "skeleton"), ("Bogged", "bogged"), ("Stray", "stray")]),
    ("Storm", [("Lightning", "storm_lightning"), ("Bronzed", "storm_bronzed"), ("Thunder", "storm_thunder")]),
    ("Water", [("Tidal", "water_tidel"), ("Brine", "water_ocean"), ("Pond", "water_pond")]),
    ("Zombie", [("Zombie", "zombie"), ("Drowned", "zombie_drowned"), ("Husk", "zombie_husk")]),
]

def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def e(s):
    return html.escape(s, quote=True)

# ---------------------------------------------------------------- content
# name, group, icon, note
ITEMS = [
    ("Dragon Scales", "Materials", "i-scale", "Shear an adult tamed dragon with Diamond or Netherite Shears. There is a 60-second cooldown; Skeleton and Wither dragons do not produce scales."),
    ("Dragon Swords and Tools", "Equipment", "i-scepter", "15 scale-producing dragon types have swords, axes, pickaxes, shovels, hoes, bows, and shields. Aether swords deal 9 damage; other dragon swords deal 7."),
    ("Humanoid Armor", "Armor", "i-chest", "15 four-piece sets. The documented piece values are helmet 5, chestplate 8, leggings 7, and boots 4."),
    ("Dragon Armor", "Armor", "i-chest", "Six material types equip on the dragon. All types prevent fall damage; damage reduction depends on material and dragon."),
    ("Dragon Flutes", "Equipment", "i-flute", "Crouch and interact with a tamed dragon while holding a flute to bind it. Use the flute to teleport it to you; 16 dye colors are listed."),
    ("Dragon Scepter", "Equipment", "i-scepter", "Use while riding a dragon to activate its breath attack."),
    ("Amulets", "Equipment", "i-core", "Tame a dragon, then hit it with an amulet to bind the two together. The item reference lists 18 types."),
    ("Variation Orb", "Equipment", "i-disc", "Changes the visual variant of a tamed dragon."),
    ("Essence Gems", "Materials", "i-bone", "Used with a Dragon Core to revive a tamed dragon as a hatchling."),
    ("Eggs and Nests", "Eggs and blocks", "i-egg", "The roster covers 17 dragon eggs. Find nests or use the documented block and lightning transformations."),
    ("Dragon Core", "Eggs and blocks", "i-core", "A revival block dropped when a tamed dragon dies; it is not used to hatch eggs."),
    ("Dragon Meat", "Food", "i-bone", "Raw dragon meat gives 3 nutrition; cooked dragon meat gives 6. Cook raw meat in a furnace."),
]

FAQ = [
    ("Getting started", [
        ("Which version does this wiki cover?", f"The latest public CurseForge file listed is v{VERSION} for Minecraft Bedrock {BEDROCK_VERSION}+. Check the <a href=\"{OFFICIAL_FILES}\">official files page</a> before downloading."),
        ("How do I install the add-on?", 'Follow the <a href="install.html#steps">install steps</a>. In short: import the add-on file, then turn on both the Behavior Pack and the Resource Pack in your world.'),
        ("Where can I find current instructions?", f'Use the guides on this site, then check the <a href="{OFFICIAL_FILES}">release notes</a> for version-specific changes.'),
    ]),
    ("Eggs and taming", [
        ("How do I find a dragon egg?", f'Eggs occur in naturally generated nests across the Overworld, Nether and End. See the official <a href="{OFFICIAL_DRAGONS}">dragon guide</a> for species-specific locations.'),
        ("How long does hatching take?", "Interact with an egg until particles appear; allow about 20 minutes for it to hatch."),
        ("How do I tame a wild dragon?", "Feed it raw fish other than pufferfish. The documented tame chance is 10% per attempt."),
        ("What food is used for breeding?", "Use raw fish other than pufferfish. Check release notes if this mechanic changes in a later version."),
        ("Can eggs change into other breeds?", f'Yes. Some eggs transform when placed on specific blocks; others require lightning. See the official <a href="{OFFICIAL_DRAGONS}">egg transformation table</a>.'),
    ]),
    ("Riding and items", [
        ("How do I ride a dragon?", "For keyboard and mouse, equip a saddle, interact to mount, press Jump to take off, and use arrow keys to steer. Touch and controller inputs differ."),
        ("What does the Dragon Core do?", f'The Dragon Core is for revival, not egg hatching. See the official <a href="{OFFICIAL_BLOCKS}">blocks guide</a>.'),
        ("Where are item recipes?", f'The official <a href="{OFFICIAL_RECIPES}">recipes guide</a> is the source for crafting grids and ingredients.'),
    ]),
]

GLOSSARY = [
    ("Dragon egg", "An egg block found in a generated nest. Breaking it drops an egg item."),
    ("Egg transformation", "Changing an egg into another breed by placing it on a documented block or striking it with lightning."),
    ("Dragon Core", "A block dropped when a tamed dragon dies; use it with the dropped Essence Gems to revive the dragon as a hatchling."),
    ("Dragon flute", "A bindable item used to teleport a tamed dragon to its owner."),
    ("Raw fish", "Raw fish other than pufferfish is used to tame and breed dragons."),
]

# ------------------------------------------------------------ svg pieces
SPRITE = """<svg class="svg-sprite" width="0" height="0" aria-hidden="true"><defs>
<symbol id="head" viewBox="0 0 160 120"><path d="M58 40C44 28 28 22 10 24c14 6 26 16 34 30z"/><path d="M80 38C70 22 56 12 40 8c12 10 20 24 24 38z"/><path d="M28 90C20 66 34 44 62 40c22-4 50 4 78 22 10 6 8 16-2 18l-26 2c-6 12-22 16-36 12-14 8-30 4-48-4z"/><path d="M30 92l-14 14 22-6zM46 98l-6 16 18-12z"/><path d="M86 52c10-8 26-4 36 6-12 2-26 0-36-6z" class="dragon-eye-accent"/><ellipse cx="104" cy="55" rx="2.6" ry="5.5" transform="rotate(-62 104 55)" class="dragon-eye-pupil"/><circle cx="138" cy="66" r="2" class="dragon-eye-accent"/><path d="M82 80l50-8" fill="none" stroke="var(--eyec,#fff)" stroke-width="2" stroke-linecap="round"/></symbol>
<symbol id="i-core" viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/><path d="M12 7.5l3.5 4.5-3.5 4.5L8.5 12z"/></symbol>
<symbol id="i-scepter" viewBox="0 0 24 24"><path d="M4 20l9-9"/><path d="M17 3l4 4-4 4-4-4z"/></symbol>
<symbol id="i-flute" viewBox="0 0 24 24"><path d="M3 17L17 3l4 4L7 21z"/><path d="M9 15v.01M12 12v.01M15 9v.01"/></symbol>
<symbol id="i-shears" viewBox="0 0 24 24"><circle cx="6" cy="6" r="2.5"/><circle cx="6" cy="18" r="2.5"/><path d="M8 7.5L21 17M8 16.5L21 7"/></symbol>
<symbol id="i-chest" viewBox="0 0 24 24"><path d="M8 3L3 7l2 5 3-1v10h8V11l3 1 2-5-5-4c-1 2-2 3-4 3S9 5 8 3z"/></symbol>
<symbol id="i-feather" viewBox="0 0 24 24"><path d="M20 4C10 4 5 9 5 15l-2 6M5 16c7 0 13-4 15-12-4 2-8 2-11 5"/></symbol>
<symbol id="i-bone" viewBox="0 0 24 24"><path d="M8.5 15.5l7-7"/><circle cx="6.5" cy="14.5" r="2.2"/><circle cx="9.5" cy="17.5" r="2.2"/><circle cx="14.5" cy="6.5" r="2.2"/><circle cx="17.5" cy="9.5" r="2.2"/></symbol>
<symbol id="i-scale" viewBox="0 0 24 24"><path d="M12 3c4 0 8 3 8 8 0 5-4 9-8 10-4-1-8-5-8-10 0-5 4-8 8-8z"/><path d="M12 7v10"/></symbol>
<symbol id="i-disc" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="2.5"/><path d="M12 5a7 7 0 0 1 7 7"/></symbol>
<symbol id="i-egg" viewBox="0 0 24 24"><path d="M12 3c4 0 7 6 7 11 0 4-3 7-7 7s-7-3-7-7c0-5 3-11 7-11z"/><path d="M7.5 14c3 1.5 6 1.5 9 0"/></symbol>
<symbol id="i-wing" viewBox="0 0 24 24"><path d="M2 19C3 10 9 5 22 4c-1 4-3 6-6 7 2 0 3 0 5 0-2 4-6 6-10 6 1 0 2 0 3-1-4 0-8 1-12 3z"/></symbol>
<symbol id="i-follow" viewBox="0 0 24 24"><circle cx="6" cy="12" r="2.5"/><circle cx="17" cy="12" r="2.5"/><path d="M9 12h5M12 9l3 3-3 3"/></symbol>
</defs></svg>"""

MARK = '<img class="mark" src="textures/pack_icon.png" alt="">'

PAGES = [  # file, nav label, title
    ("install.html", "Install", "Install"),
    ("dragons.html", "Dragons", "Dragons"),
    ("breeding.html", "Breeding", "Breeding"),
    ("flight.html", "Flight", "Riding and flight"),
    ("items.html", "Items", "Items"),
    ("changelog.html", "Changelog", "Changelog"),
    ("faq.html", "FAQ", "FAQ and glossary"),
]

GUIDE_GROUPS = [
    ("Start here", [("index.html", "Overview"), ("install.html", "Install")]),
    ("Dragon guide", [("dragons.html", "Dragons"), ("breeding.html", "Eggs and taming"),
                      ("flight.html", "Riding and flight")]),
    ("Reference", [("items.html", "Items and equipment"), ("changelog.html", "Changelog"),
                   ("faq.html", "FAQ and glossary")]),
]

EDITION_SCRIPT = """<script>
(() => {
  const key = "dm2-edition";
  const picker = document.querySelector("#edition-picker");
  const bedrock = document.querySelector("#bedrock-content");
  const params = new URLSearchParams(window.location.search);
  let saved = null;
  try { saved = localStorage.getItem(key); } catch (error) {}
  const showBedrock = (remember) => {
    picker.hidden = true;
    bedrock.hidden = false;
    if (remember) { try { localStorage.setItem(key, "bedrock"); } catch (error) {} }
  };
  if (params.get("choose") === "1") {
    try { localStorage.removeItem(key); } catch (error) {}
  } else if (params.get("edition") === "bedrock" || window.location.hash) {
    showBedrock(true);
  } else if (saved === "java") {
    window.location.replace("java.html");
  } else if (saved === "bedrock") {
    showBedrock(false);
  }
  document.querySelector("#select-bedrock").addEventListener("click", () => showBedrock(true));
  document.querySelector("#select-java").addEventListener("click", () => {
    try { localStorage.setItem(key, "java"); } catch (error) {}
  });
  document.querySelector("#change-edition").addEventListener("click", () => {
    try { localStorage.removeItem(key); } catch (error) {}
    bedrock.hidden = true;
    picker.hidden = false;
    window.history.replaceState(null, "", window.location.pathname);
    picker.scrollIntoView({ block: "start" });
  });
  if (window.location.hash && !bedrock.hidden) {
    const target = document.getElementById(decodeURIComponent(window.location.hash.slice(1)));
    if (target) requestAnimationFrame(() => target.scrollIntoView());
  }
})();
</script>
"""

INDEX = []  # search index entries

def idx(title, page, anchor, kind, extra=""):
    INDEX.append({"t": title, "p": page, "a": anchor, "k": kind, "x": extra})

def h2(i, title, page=None, kind=None):
    if page:
        idx(title, page, i, kind or "Section")
    return f'<h2 id="{i}"><a class="anchor" href="#{i}" aria-label="Link to this section">#</a>{title}</h2>'

def h3(i, title, page=None, kind=None):
    if page:
        idx(title, page, i, kind or "Section")
    return f'<h3 id="{i}"><a class="anchor" href="#{i}" aria-label="Link to this section">#</a>{title}</h3>'

def guide_navigation(file):
    groups = []
    for title, links in GUIDE_GROUPS:
        items = "".join(
            f'<li><a href="{target}"' +
            (' aria-current="page"' if target == file else '') +
            f'>{label}</a></li>'
            for target, label in links)
        groups.append(f'<section class="guide-group"><h2>{title}</h2><ul>{items}</ul></section>')
    return "".join(groups)

# ------------------------------------------------------------ page shell
def head(file, title, desc, theme_hero=False):
    full_title = SITE if file == "index.html" else f"{title} | {SITE}"
    canon = f'<link rel="canonical" href="{SITE_URL}/{"" if file == "index.html" else file}">' if SITE_URL else ""
    og = ""
    if SITE_URL:
        og = (f'<meta property="og:type" content="website"><meta property="og:title" content="{e(full_title)}">'
              f'<meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{SITE_URL}/{"" if file == "index.html" else file}">')
    return f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="theme-color" content="#21152d">
<link rel="icon" href="textures/pack_icon.png" type="image/png">
{canon}{og}
<script>try{{var t=localStorage.getItem("dm2-theme");if(t==="dark"||t==="light")document.documentElement.setAttribute("data-theme",t)}}catch(x){{}}</script>
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
{SPRITE}
"""

def header(file, sections=()):
    section_links = "".join(f'<li><a href="#{e(i)}">{e(label)}</a></li>' for i, label in sections)
    section_nav = (f'<section class="drawer-section"><h2>On this page</h2><ul>{section_links}</ul></section>'
                   if section_links else "")
    return f"""<header class="site"><div class="wrap bar">
<a class="brand" href="index.html" aria-label="DragonMounts 2 Wiki, home">{MARK}<span>DragonMounts 2</span></a>
<div class="tools">
<button class="ibtn menu-toggle" id="nav-toggle" type="button" aria-label="Open guide menu" aria-controls="nav-drawer" aria-expanded="false"><svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h16"/></svg></button>
<button class="sbtn" id="sbtn" type="button" aria-label="Search the wiki"><svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg><span>Search</span><kbd>/</kbd></button>
<button class="ibtn" id="theme" type="button" aria-label="Switch between light and dark mode"><svg class="ico moon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg><svg class="ico sun" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M5 5l1.5 1.5M17.5 17.5L19 19M5 19l1.5-1.5M17.5 6.5L19 5"/></svg></button>
</div></div></header>
<dialog class="nav-drawer" id="nav-drawer" aria-labelledby="nav-title">
<div class="drawer-head"><b id="nav-title">Explore the wiki</b><button class="ibtn" id="nav-close" type="button" aria-label="Close guide menu"><svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18"/></svg></button></div>
<nav aria-label="Guide pages">{guide_navigation(file)}</nav>
{section_nav}
</dialog>
"""

def guide_sidebar(file, sections):
    section_links = "".join(
        f'<li><a href="#{e(i)}">{e(label)}</a></li>' for i, label in sections)
    contents = (
        f'<section class="guide-group"><h2>On this page</h2><ul>{section_links}</ul></section>'
        if section_links else "")
    return f'<aside class="guide-sidebar"><nav aria-label="Wiki chapters">{guide_navigation(file)}</nav>{contents}</aside>'

def footer():
    nav = "".join(f'<li><a href="{f}">{l}</a></li>' for f, l, _ in PAGES)
    return f"""<footer class="foot"><div class="wrap">
<div class="footgrid">
<div><a class="brand" href="index.html">{MARK}<span>DragonMounts 2 Wiki</span></a><p>Project wiki for the public Minecraft Bedrock v{VERSION} release.</p></div>
<div><h4>Guide</h4><ul>{nav}</ul></div>
<div><h4>Official sources</h4><ul>
<li><a href="{OFFICIAL_WIKI}">Project wiki</a></li>
<li data-link="curseforge" hidden><a href="#">CurseForge page</a></li>
<li data-link="discord" hidden><a href="#">Discord</a></li></ul></div>
<div><h4>This wiki</h4><ul>
<li data-link="issues" hidden><a href="#">Report a mistake</a></li>
<li data-link="repo" hidden><a href="#">Source on GitHub</a></li></ul></div>
</div>
<small>The gameplay guides describe v{VERSION}; the Changelog also archives historical project releases. Check the official download listing for current game-version support.</small>
</div></footer>
<div id="sx" hidden><div class="sbox" role="dialog" aria-modal="true" aria-label="Search the wiki"><input id="sq" type="search" placeholder="Search dragons, eggs, taming, riding, equipment" aria-label="Search the wiki" autocomplete="off"><div id="sres"></div><div class="sfoot">Arrow keys to move, Enter to open, Esc to close</div></div></div>
<script src="assets/config.js"></script>
<script src="assets/data.js"></script>
<script src="assets/app.js"></script>
</body>
</html>
"""

def inner_page(file, title, lede, desc, sections, body_html, extra_layout_class=""):
    """sections: list of (id, label) for page contents navigation."""
    idx(title, file, "", "Page", lede)
    return (head(file, title, desc) + header(file, sections) + f"""<main id="main">
<div class="phead"><div class="wrap"><h1>{title}</h1><p class="lede">{lede}</p></div></div>
<div class="wrap layout has-sidebar{extra_layout_class}">
{guide_sidebar(file, sections)}
<article>
{body_html}
</article>
</div>
</main>
""" + footer())

def legacy(text):
    return f'<div class="note old"><p><strong>From earlier versions (v1.2.x).</strong> {text}</p></div>'

def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)

def build_home():
    f = "index.html"
    task_groups = [
        ("Get started", [
            ("Install the add-on", "Set up the packs in a Bedrock world.", "install.html"),
            ("Download options", "Choose from the listed Dragon Mounts 2 download sites.", "install.html#downloads"),
            ("Find an egg", "Look for nests in the Overworld, Nether, and End.", "dragons.html#species"),
            ("Hatch an egg", "Interact until particles appear; hatching takes about 20 minutes.", "breeding.html#hatching"),
        ]),
        ("Raise and ride", [
            ("Tame a dragon", "Feed a wild dragon raw fish, except pufferfish.", "breeding.html#taming"),
            ("Ride and fly", "Equip a saddle, mount, then press Jump to take off.", "flight.html#controls"),
            ("Breed and transform eggs", "Use fish to breed dragons; use blocks or lightning to transform eggs.", "breeding.html#transformations"),
        ]),
        ("Look things up", [
            ("Browse all 17 dragons", "Compare egg images, breath types, natural nests, and transformations.", "dragons.html#species"),
            ("Items and equipment", "Dragon scales, armor, tools, flutes, and more.", "items.html"),
            ("FAQ and glossary", "Find quick answers and common terms.", "faq.html"),
            ("Release details", "Check supported game versions and current release notes.", OFFICIAL_FILES),
        ]),
    ]
    tasks_html = "".join(
        f'<section class="task-group"><h3>{title}</h3><div class="tasks">' +
        "".join(f'<a href="{url}"><b>{label}</b><span>{description}</span></a>'
                for label, description, url in tasks) +
        '</div></section>'
        for title, tasks in task_groups)
    body = head(f, "", f"Dragon Mounts 2 Wiki for Minecraft Bedrock and Java editions.") + header(f, [("tasks", "Browse the guide"), ("meet", "Meet the dragons"), ("help", "Contribute")]) + f"""<main id="main">
<section class="edition-picker" id="edition-picker" aria-labelledby="edition-title">
<div class="wrap edition-picker-inner">
<p class="eyebrow">DRAGON MOUNTS 2 WIKI</p>
<h1 id="edition-title">Which Minecraft edition do you play?</h1>
<p class="lede">Choose your edition to open the right guide. We’ll remember your choice on this device, and you can change it whenever you like.</p>
<div class="edition-options">
<button class="edition-card" id="select-bedrock" type="button">
<span class="edition-tag">GUIDES AVAILABLE</span>
<strong>Minecraft Bedrock</strong>
<span>Open the Bedrock guides for installing the add-on, dragons, eggs, flight, and more.</span>
</button>
<a class="edition-card" id="select-java" href="java.html">
<span class="edition-tag">STARTER SECTION</span>
<strong>Minecraft Java</strong>
<span>Open the Java section. It is a blank area ready for Java-specific guides.</span>
</a>
</div>
</div>
</section>
<div id="bedrock-content" hidden>
<div class="edition-status"><span>Showing Minecraft Bedrock guides</span><button id="change-edition" type="button">Change edition</button></div>
<section class="home-hero">
<div class="wrap home-hero-inner">
<div class="home-hero-copy">
<p class="eyebrow">BEDROCK FIELD GUIDE</p>
<h1>DragonMounts 2 Wiki</h1>
<p class="lede">A field guide to finding, raising, and flying dragons in Minecraft Bedrock.</p>
<div class="hero-actions"><a class="btn" href="dragons.html#species">Explore the dragons</a><a class="btn ghost" href="breeding.html#hatching">Start with an egg</a><a class="btn ghost" href="install.html#downloads">Download options</a></div>
<p class="hero-release"><span>PUBLIC RELEASE</span><b>v{VERSION}</b><span>Minecraft Bedrock {BEDROCK_VERSION}+</span></p>
</div>
<figure class="home-hero-art"><img src="textures/dragon.egg/dragonmounts2.dragon_egg_ender.png" alt="Ender Dragon egg from the Dragon Mounts 2 pack" width="512" height="512"><figcaption>ENDER DRAGON EGG</figcaption></figure>
</div>
</section>
<div class="wrap home-note"><p class="note"><strong>Dragon Mounts 2 project guide.</strong> Mechanics and species are documented for the public v{VERSION} release. Check the <a href="{OFFICIAL_WIKI}">project development wiki</a> for technical notes and the <a href="{OFFICIAL_FILES}">official download listing</a> for current game-version support.</p></div>
<div class="wrap home-content">
{h2("tasks", "Browse the guide by goal", f, "Section")}
{tasks_html}

{h2("meet", "Meet the dragons", f, "Section")}
<div class="three">
<div><h3>Forest Dragon</h3><p>Preview Nature, Cold, Jungle, and Warm appearances.</p><a href="dragons.html#forest">Explore the Forest Dragon</a></div>
<div><h3>Aether Dragon</h3><p>Preview Aethra, Breeze, and Wind appearances.</p><a href="dragons.html#aether">Explore the Aether Dragon</a></div>
<div><h3>All 17 species</h3><p>Compare eggs, breath types, natural nests, and transformations.</p><a href="dragons.html#species">Browse the roster</a></div>
</div>

{h2("help", "Contribute", f, "Section")}
<p>Report missing or outdated information to help keep the guide accurate.</p>
<p class="cta contribute-actions"><span data-link="issues" hidden><a class="btn sm" href="#">Report a mistake</a></span> <span data-link="discord" hidden><a class="btn sm ghost" href="#">Ask on Discord</a></span></p>
</div>
</div>
</main>
""" + EDITION_SCRIPT + footer()
    write(f, body)

def build_java():
    f = "java.html"
    body = head(f, "Minecraft Java", "The Java edition section of the DragonMounts 2 Wiki, ready for future Java-specific guides.") + """<header class="site">
  <div class="wrap bar">
    <a class="brand" href="index.html?choose=1"><img class="mark" src="textures/pack_icon.png" alt=""><span>DragonMounts 2 Wiki</span></a>
    <a class="btn sm" href="index.html?choose=1">Change edition</a>
  </div>
</header>
<main id="main">
  <div class="phead"><div class="wrap"><p class="eyebrow">MINECRAFT JAVA</p><h1>Java Edition guides</h1><p class="lede">This is the Java section of the Wiki. It is a starter area ready for Java-specific guides.</p></div></div>
  <section class="wrap java-empty" aria-labelledby="java-empty-title">
    <h2 id="java-empty-title">This section is ready for future guides</h2>
    <p>There are no Java guides here yet. The existing Dragon Mounts 2 guides are for Minecraft Bedrock; this section is kept separate for Java information.</p>
    <p class="cta"><a class="btn" href="index.html?edition=bedrock">Open the Bedrock guides</a><a class="btn ghost" href="index.html?choose=1">Choose another edition</a></p>
  </section>
</main>
<footer class="foot"><div class="wrap"><p>Dragon Mounts 2 Wiki · <a href="index.html?choose=1">Choose edition</a> · <a href="https://github.com/DragonMounts-Team/DragonMounts2-Bedrock/wiki">Project wiki</a></p></div></footer>
<script>try { localStorage.setItem("dm2-edition", "java"); } catch (error) {}</script>
</body></html>"""
    write(f, body)

# ------------------------------------------------------------ INSTALL
def build_install():
    f = "install.html"
    steps = [
        ("Download the current file", f'Choose a page from the <a href="install.html#downloads">download options</a> and check that the release supports your Minecraft version.'),
        ("Import the add-on", "Open the downloaded file with Minecraft Bedrock and wait for the import to finish."),
        ("Apply it to a world", "In the world settings, enable the imported Dragon Mounts 2 packs, then load the world."),
        ("Review the release notes", f'Check the notes for your <a href="{OFFICIAL_FILES}">selected release</a> before installing.'),
    ]
    steps_html = "".join(f'<li><label><input type="checkbox"><span>{t}<small>{d}</small></span></label></li>' for t, d in steps)
    for t, d in steps:
        idx(t, f, "steps", "Install step", re.sub("<[^>]+>", "", d))
    trouble = [
        ("I can't find the add-on in my world's settings",
            "Confirm Minecraft finished importing the file, then check the world's Resource Packs and Behavior Packs lists."),
        ("Dragons or items are missing",
            "Check that every pack included with the download is enabled for the world."),
           ("The file will not import",
            f'Confirm your Minecraft version is supported by the selected <a href="{OFFICIAL_FILES}">release file</a>, then follow the official <a href="{OFFICIAL_WIKI}">installation notes</a>.'),
           ("A mechanic differs from this guide",
            f'Check the notes attached to your exact <a href="{OFFICIAL_FILES}">release file</a>, then report the difference.'),
    ]
    tr_html = ""
    for q, a in trouble:
        i = "t-" + slug(q)
        idx(q, f, i, "Troubleshooting", re.sub("<[^>]+>", "", a))
        tr_html += f'<details class="q" id="{i}"><summary>{q}</summary><div class="body"><p>{a}</p></div></details>'
    download_links = "".join(
        f'<li><a href="{e(url)}">{e(name)}</a></li>' for name, url in DOWNLOAD_SOURCES)
    secs = [("before", "Before you start"), ("downloads", "Download options"), ("steps", "Install steps"), ("version", "Version scope"), ("troubleshooting", "Troubleshooting")]
    body = f"""
{h2("before", "Before you start", f)}
<ul>
<li>This is the <b>Minecraft Bedrock</b> add-on; check the exact supported game version on the selected file.</li>
<li>Back up your world before adding or updating packs.</li>
<li>Use the notes attached to the selected release for version-specific steps.</li>
</ul>
{h2("downloads", "Download options", f)}
<p>Choose a download page and confirm the file supports your Minecraft version before installing.</p>
<ul class="download-sources">{download_links}</ul>

{h2("steps", "Install steps", f)}
<p>Tick each step as you go. Your progress is saved in this browser.</p>
<div class="panel">
<div class="prog"><i id="pbar"></i></div><p id="ptxt"></p>
<ol class="steps">{steps_html}</ol>
<p><button class="btn ghost sm" id="preset" type="button">Start over</button></p>
</div>

{h2("version", "Version scope", f)}
<dl class="facts">
<dt>Latest public file</dt><dd>v{VERSION}</dd>
<dt>Listed game version</dt><dd>Minecraft Bedrock {BEDROCK_VERSION}+</dd>
<dt>Edition</dt><dd>Minecraft Bedrock</dd>
<dt>Download sources</dt><dd>{", ".join(f'<a href="{e(url)}">{e(name)}</a>' for name, url in DOWNLOAD_SOURCES)}</dd>
</dl>

{h2("troubleshooting", "Troubleshooting", f)}
{tr_html}
<p class="mute troubleshooting-note">Still stuck? <span data-link="discord" hidden><a href="#">Ask on Discord</a></span><span data-link="issues" hidden> or <a href="#">report it on GitHub</a></span></p>
"""
    write(f, inner_page(f, "Install", "Get DragonMounts 2 running in a Bedrock world, update from an older build, and fix the usual problems.",
                        "Step-by-step install guide for the DragonMounts 2 Bedrock add-on, with update steps and troubleshooting.", secs, body))

# ------------------------------------------------------------ DRAGONS
def build_dragons():
    f = "dragons.html"
    secs = [("appearances", "Dragon appearances"), ("species", "All 17 species")]
    roster_rows = ""
    for name, breath, source_type, source, egg in DRAGON_ROSTER:
        idx(name + " Dragon", f, "species", "Dragon", breath + " breath; " + source_type + ": " + source)
        roster_rows += f'<tr><th scope="row">{e(name)} Dragon</th><td><img class="dragon-roster-thumb" src="textures/dragon.egg/dragonmounts2.dragon_egg_{egg}.png" alt="{e(name)} Dragon egg" width="64" height="64" loading="lazy"></td><td>{e(breath)}</td><td>{e(source_type)}</td><td>{e(source)}</td></tr>'
    appearances = [{
        "name": name,
        "variants": [{"name": variant, "src": f"textures/dragon.entity/dragonmounts2.{asset}.png"}
                     for variant, asset in variants],
    } for name, variants in DRAGON_APPEARANCES]
    appearance_json = e(json.dumps(appearances, separators=(",", ":")))
    appearance_cards = "".join(
        f'<section class="appearance-card" id="{slug(item["name"])}" data-appearance="{slug(item["name"])}">'
        f'<h3>{e(item["name"])} Dragon</h3>'
        f'<figure><img data-appearance-image src="{e(item["variants"][0]["src"])}" '
        f'alt="{e(item["name"])} Dragon, {e(item["variants"][0]["name"])} appearance" '
        f'width="818" height="392" loading="lazy">'
        f'<figcaption><b>{e(item["name"])} Dragon</b><span data-appearance-variant>{e(item["variants"][0]["name"])}</span></figcaption></figure>'
        f'<label>Appearance<select data-appearance-select aria-label="{e(item["name"])} Dragon appearance">'
        + "".join(f'<option value="{index}">{e(variant["name"])}</option>'
                  for index, variant in enumerate(item["variants"])) +
        '</select></label></section>'
        for item in appearances)
    body = f"""
{h2("appearances", "Dragon appearances", f, "Gallery")}
<p>Scroll through the dragons and choose a variant to preview it.</p>
<div class="appearance-explorer" id="appearance-explorer" data-appearances="{appearance_json}">
{appearance_cards}
</div>

{h2("species", "All 17 species", f, "Roster")}
<p>Quick reference for each dragon’s egg, breath, and how to find or create it. <a href="breeding.html#transformations">See egg transformations</a> or the <a href="{OFFICIAL_DRAGONS}">official dragon guide</a>.</p>
<div class="tbl"><table class="dragon-roster"><thead><tr><th scope="col">Dragon</th><th scope="col">Egg</th><th scope="col">Breath</th><th scope="col">Source type</th><th scope="col">Location or method</th></tr></thead><tbody>{roster_rows}</tbody></table></div>
"""
    write(f, inner_page(f, "Dragons", f"Browse all 17 dragons in the public v{VERSION} release, with egg images, breath types, natural nests, and transformations.",
                        f"Browse dragon appearance variants and compare egg sources, breath types, natural nests, and transformations.", secs, body))

# ------------------------------------------------------------ BREEDING
def build_breeding():
    f = "breeding.html"
    secs = [("hatching", "Hatching"), ("taming", "Taming and breeding"), ("transformations", "Block transformations"), ("lightning", "Lightning transformations")]
    block_changes = [
        ("Lava", "Fire"), ("Water", "Water"), ("Snow, Ice, Blue Ice, Packed Ice", "Ice"),
        ("Bone Block", "Skeleton"), ("Mossy Cobblestone or Soul Sand", "Zombie"),
        ("Terracotta or Sand", "Terra"), ("End Stone", "Ender"),
        ("Daylight Sensor (day mode)", "Sunlight"), ("Inverted Daylight Sensor (night mode)", "Moonlight"),
        ("Bookshelves (Ender egg only)", "Enchant"),
    ]
    block_rows = "".join(f"<tr><th scope=\"row\">{e(block)}</th><td>{e(dragon)} Dragon Egg</td></tr>" for block, dragon in block_changes)
    lightning_rows = "".join(f"<tr><th scope=\"row\">{e(start)} Dragon Egg</th><td>{e(result)} Dragon Egg</td></tr>" for start, result in [("Water", "Storm"), ("Skeleton", "Wither"), ("Moonlight", "Dark")])
    body = f"""
{h2("hatching", "Hatching an egg", f)}
<p>Dragon eggs are found in naturally generated nests across the Overworld, Nether, and End. Interact with an egg until particles appear; allow about 20 minutes for it to hatch.</p>
<p><a href="{OFFICIAL_DRAGONS}">Official dragon and nest guide</a></p>

{h2("taming", "Taming and breeding", f)}
<dl class="facts"><dt>Taming food</dt><dd>Any raw fish except pufferfish</dd><dt>Tame chance</dt><dd>10% per attempt</dd><dt>Breeding food</dt><dd>Any raw fish except pufferfish</dd><dt>Healing</dt><dd>Any meat; 2-4 HP</dd></dl>
<p>These values come from the <a href="{OFFICIAL_DRAGONS}">official Dragons guide</a>.</p>

{h2("transformations", "Block transformations", f)}
<p>Place an egg on the listed block and wait about 5 minutes. Unless noted, any egg can be the starting egg.</p>
<div class="tbl"><table><thead><tr><th scope="col">Block</th><th scope="col">Result</th></tr></thead><tbody>{block_rows}</tbody></table></div>

{h2("lightning", "Lightning transformations", f)}
<p>Lightning transforms these eggs in about 2 seconds. A natural storm or a Trident with Channeling can provide the strike.</p>
<div class="tbl"><table><thead><tr><th scope="col">Starting egg</th><th scope="col">Result</th></tr></thead><tbody>{lightning_rows}</tbody></table></div>
<p class="source-line">Source: <a href="{OFFICIAL_DRAGONS}">Official Dragon Mounts 2 Dragons guide</a>.</p>
"""
    write(f, inner_page(f, "Eggs and taming", f"How to hatch, tame, and transform eggs in public release v{VERSION}.",
                        "Official egg hatching, raw-fish taming and breeding food, and egg transformation reference for Dragon Mounts 2.", secs, body))

# ------------------------------------------------------------ FLIGHT
def build_flight():
    f = "flight.html"
    secs = [("controls", "Mount and take off"), ("inventory", "Dragon inventory")]
    body = f"""
{h2("controls", "Mount and take off", f)}
<ol><li>Place a saddle on your dragon.</li><li>Interact with the dragon to mount it.</li><li>Press Jump to take off.</li><li>Use the arrow keys to steer while airborne.</li></ol>
<p>These steps describe keyboard-and-mouse controls. Touch and controller inputs vary by platform and are not listed here.</p>

{h2("inventory", "Dragon inventory", f)}
<p>Open the dragon's inventory while riding to manage its equipment. The inventory has saddle, dragon armor, and chest slots; a chest unlocks 18 storage slots.</p>
<p class="source-line">Source: <a href="{OFFICIAL_DRAGONS}">Official Dragon Mounts 2 Dragons guide</a>.</p>
"""
    write(f, inner_page(f, "Riding and flight", "Mount with a saddle, press Jump to take off, and steer with the arrow keys.",
                        "Official saddle, riding, takeoff, steering, and dragon inventory instructions for Dragon Mounts 2.", secs, body))

# ------------------------------------------------------------ ITEMS
def build_items():
    f = "items.html"
    secs = [("all", "Items and equipment"), ("sources", "Official references")]
    cards = ""
    for name, group, icon, note in ITEMS:
        i = slug(name)
        idx(name, f, i, "Item", group)
        cards += (f'<li class="item" id="{i}" data-group="{group}">'
                  f'<svg viewBox="0 0 24 24" aria-hidden="true"><use href="#{icon}"/></svg><div><b>{name}</b><p>{note}</p></div></li>')
    groups = ["Equipment", "Armor", "Materials", "Eggs and blocks", "Food"]
    gbtn = '<button type="button" data-group="all" aria-pressed="true">All</button>' + "".join(
        f'<button type="button" data-group="{g}" aria-pressed="false">{g}</button>' for g in groups)
    body = f"""
{h2("all", "All items", f)}
<p>Quick summaries of documented equipment and materials. Recipes and full item details are maintained in the official project wiki.</p>
<div class="finder"><input id="iq" type="search" placeholder="Search items" aria-label="Search items"></div>
<div class="chipset" id="igroups" role="group" aria-label="Filter by type">{gbtn}</div>
<p class="count" id="icount" aria-live="polite"></p>
<ul class="items wide" id="itemlist">{cards}</ul>
<div class="empty" id="iempty" hidden>No items match. Clear the search or choose All.</div>

{h2("sources", "Official references")}
<ul><li><a href="{OFFICIAL_ITEMS}">Items and equipment</a></li><li><a href="{OFFICIAL_RECIPES}">Crafting recipes</a></li><li><a href="{OFFICIAL_BLOCKS}">Blocks and eggs</a></li></ul>
"""
    write(f, inner_page(f, "Items and equipment", "Dragon Mounts 2 equipment, materials, and food.",
                        f"Documented items for Dragon Mounts 2 v{VERSION}, with direct links to official equipment and recipe guides.", secs, body))

# ------------------------------------------------------------ CHANGELOG
def build_changelog():
    f = "changelog.html"
    secs = [("coverage", "Wiki coverage"), ("releases", "Published release history"),
            ("prereleases", "2.0 prereleases"), ("sources", "Official release pages")]
    release_entries = []
    prerelease_entries = []
    for release in GITHUB_RELEASES:
        anchor = slug("release-" + release["tag"])
        changes = "".join(f"<li>{e(change)}</li>" for change in release["changes"])
        entry = (
            f'<details class="release-entry" id="{e(anchor)}">'
            f'<summary><span><b>{e(release["version"])}</b>'
            f'<small>{e(release["date"])} · {e(release["stage"])}</small></span>'
            f'<span class="release-summary">{e(release["summary"])}</span></summary>'
            f'<ul>{changes}</ul>'
            f'<p class="release-source"><a href="https://github.com/DragonMounts-Team/DragonMounts2-Bedrock/releases/tag/{e(release["tag"])}">Official release notes</a></p>'
            f'</details>'
        )
        (prerelease_entries if release["stage"] == "Pre-release" else release_entries).append(entry)
        idx(release["version"], f, anchor, "Release note", release["summary"])
    coverage_body = (
        f'<dl class="facts"><dt>Documented guide</dt><dd>Dragon Mounts 2 v{VERSION}</dd>'
        f'<dt>Platform</dt><dd>Minecraft Bedrock</dd>'
        f'<dt>Listed game version</dt><dd>{BEDROCK_VERSION}+</dd></dl>'
        f'<p>This Wiki’s gameplay guides describe v{VERSION}. The archive below records published project releases and prereleases from GitHub; it does not mean their mechanics are covered by this guide. Older or platform-specific notes may also be attached to download files.</p>'
        f'<p><a class="btn" href="{OFFICIAL_FILES}">Check current download files</a></p>'
    )
    body = f"""
{h2("coverage", "Wiki coverage", f)}
{coverage_body}

{h2("releases", "Published release history", f)}
<p>These entries summarize every published stable release and hotfix currently listed on the project’s GitHub Releases page. Open an entry for its changes and source.</p>
<div class="release-list">{''.join(release_entries)}</div>

{h2("prereleases", "2.0 prereleases", f)}
<p>These are prerelease notes, not a stable-release compatibility guarantee.</p>
<div class="release-list">{''.join(prerelease_entries)}</div>

{h2("sources", "Official release pages")}
<ul>{''.join(f'<li><a href="{e(url)}">{e(name)}</a></li>' for name, url in DOWNLOAD_SOURCES)}<li><a href="https://github.com/DragonMounts-Team/DragonMounts2-Bedrock/releases">GitHub Releases</a></li><li><a href="{OFFICIAL_WIKI}">Project wiki</a></li></ul>
"""
    write(f, inner_page(f, "Changelog", "Browse published Dragon Mounts 2 releases, hotfixes, and 2.0 prerelease notes.",
                        "Chronological Dragon Mounts 2 changelog with summarized GitHub release notes and direct source links.", secs, body))

# ------------------------------------------------------------ FAQ
def build_faq():
    f = "faq.html"
    secs = [("questions", "Questions")] + [(slug(g), g) for g, _ in FAQ] + [("glossary", "Glossary")]
    groups = ""
    for g, qs in FAQ:
        inner = ""
        for q, a in qs:
            i = "q-" + slug(q)
            idx(q, f, i, "FAQ", re.sub("<[^>]+>", "", a))
            inner += f'<details class="q" id="{i}"><summary>{q}</summary><div class="body"><p>{a}</p></div></details>'
        groups += f'<div class="fgroup"><h3 id="{slug(g)}">{g}</h3>{inner}</div>'
    gl = "".join(f"<dt>{t}</dt><dd>{d}</dd>" for t, d in GLOSSARY)
    for t, d in GLOSSARY:
        idx(t, f, "glossary", "Glossary", d)
    body = f"""
{h2("questions", "Questions", f)}
<div class="finder"><input id="fq" type="search" placeholder="Search the questions" aria-label="Search the questions"></div>
<p class="count" id="fcount" aria-live="polite"></p>
<div id="faqlist">{groups}</div>
<div class="empty" id="fempty" hidden>No answers match. Try a shorter word, or use the site search.</div>

{h2("glossary", "Glossary", f)}
<dl class="facts">{gl}</dl>
"""
    write(f, inner_page(f, "FAQ and glossary", "Quick answers about installing, raising, breeding and flying dragons.",
                        "Frequently asked questions and a glossary for the DragonMounts 2 Bedrock add-on.", secs, body))

# ------------------------------------------------------------ 404 + assets
def build_404():
    f = "404.html"
    write(f, head(f, "Page not found", "Page not found.") + header(f) + """<main id="main"><div class="wrap not-found">
<h1>Page not found</h1>
<p class="lede">This address does not match a page in the guide.</p>
<p class="cta"><a class="btn" href="index.html">Home</a> <a class="btn ghost" href="dragons.html">Browse dragons</a></p>
</div></main>""" + footer())

def build_assets():
    js = "window.DM_INDEX=" + json.dumps(INDEX, ensure_ascii=False) + ";\n"
    write("assets/data.js", js)
    write("assets/favicon.svg", """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 120"><rect width="160" height="120" rx="26" fill="#f97316"/><g fill="#1d1008" transform="translate(16 12) scale(.8)"><path d="M58 40C44 28 28 22 10 24c14 6 26 16 34 30z"/><path d="M80 38C70 22 56 12 40 8c12 10 20 24 24 38z"/><path d="M28 90C20 66 34 44 62 40c22-4 50 4 78 22 10 6 8 16-2 18l-26 2c-6 12-22 16-36 12-14 8-30 4-48-4z"/><path d="M30 92l-14 14 22-6zM46 98l-6 16 18-12z"/><path d="M86 52c10-8 26-4 36 6-12 2-26 0-36-6z" fill="#f97316"/></g></svg>""")
    write(".nojekyll", "")
    write("robots.txt", "User-agent: *\nAllow: /\n" + (f"Sitemap: {SITE_URL}/sitemap.xml\n" if SITE_URL else ""))
    if SITE_URL:
        urls = ["index.html", "java.html"] + [p[0] for p in PAGES]
        sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
            f'<url><loc>{SITE_URL}/{"" if u == "index.html" else u}</loc></url>\n' for u in urls) + "</urlset>\n"
        write("sitemap.xml", sm)

if __name__ == "__main__":
    build_home(); build_java(); build_install(); build_dragons(); build_breeding(); build_flight()
    build_items(); build_changelog(); build_faq(); build_404()
    idx("Home", "index.html", "", "Page", "DragonMounts 2 guide")
    build_assets()
    print("Built", len(INDEX), "search entries")
