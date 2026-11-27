# AIDOS Home 0.9.0

Home Assistant app with independent AIDOS interface. Uses Home Assistant API to read entities and send controls.

## Installation / update

Copy the contents of this folder into the `AIDOS-Home` GitHub repository, commit and push. Refresh the Home Assistant Apps catalog and update AIDOS.

## Features

- Persistent bottom navigation, light dashboard and amber accents
- Card manager tabs: Cards, Popup, Chips, Badges, Community
- Searchable categories and interactive preview with compatible entity counts
- 25 built-in templates, linked to live Home Assistant entity states
- Card notifications managed in Settings and independently on each card
- AI chat using Home Assistant Conversation
- Config stored inside AIDOS app data; fresh installs begin with zero cards

## Licensing and provenance

AIDOS source in this package is independently developed. No proprietary third-party application runtime is bundled. Any required third-party notices must remain intact.

## Limits

This version does **not** implement the proprietary Oikos runtime or all its specialized card functionality. Avoid publishing private Home Assistant configuration, access tokens or data files.
