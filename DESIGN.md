---
name: SJYssr Profile
colors:
  primary: "#1A1C1E"
  secondary: "#6C7278"
  accent: "#58A6FF"
  success: "#3FB950"
  warning: "#D29922"
  danger: "#F85149"
  bg: "#0D1117"
  surface: "#161B22"
  border: "#30363D"
  text: "#C9D1D9"
  textMuted: "#8B949E"
  link: "#58A6FF"
typography:
  h1:
    fontFamily: Inter
    fontSize: 2rem
  h2:
    fontFamily: Inter
    fontSize: 1.5rem
  h3:
    fontFamily: Inter
    fontSize: 1.25rem
  body:
    fontFamily: -apple-system, BlinkMacSystemFont, Segoe UI
    fontSize: 1rem
  mono:
    fontFamily: JetBrains Mono, Fira Code
    fontSize: 0.875rem
rounded:
  sm: 6px
  md: 12px
  lg: 24px
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px

---

# SJYssr Profile Design System

## Overview

Clean, modern GitHub profile page with dark theme and blue accent. The design prioritizes readability, fast-loading images (Shields.io badges), and dynamic data. Layout is fully centered and responsive.

## Design Principles

- **Clarity over decoration**: Every element serves a purpose
- **Data-driven**: Use dynamic Shields.io badges and services that auto-update
- **Performance**: Only use image-based badges, no JavaScript or iframes
- **GitHub-native**: Works within GitHub Markdown limitations

## Image Services

All external images must use reliable, widely-available services:

- **Shields.io** (`img.shields.io`) — Reliable static and dynamic badges
- **Readme Typing SVG** (`readme-typing-svg.demolab.com`) — Typing animation
- **Streak Stats** (`streak-stats.demolab.com`) — Contribution streak
- **Komarev** (`komarev.com/ghpvc/`) — Visitor counter
- **Skillicons** (`skillicons.dev`) — Tech stack icon grid
- **jsDelivr** (`cdn.jsdelivr.net`) — Reliable GitHub file CDN

## Sections

1. **Header** — Animated typing text, key status badges
2. **GitHub Stats** — Stars, repos, commits badges + streak stats
3. **My Skills** — Skillicons technology grid
4. **Contribution Graph** — Snake animation served from jsDelivr
5. **Projects** — Key projects with descriptions and status badges
6. **About Me** — Bio, education, interests
7. **Footer** — Signature with link
