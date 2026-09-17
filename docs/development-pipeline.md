# HidayahMF — Development Pipeline

> Code-grounded maintenance and publishing guide for the GitHub profile repository. Reviewed from `main` at `9ae6037d4170` on 2026-09-17.

This repository is the public GitHub profile itself. The primary product is `README.md`: profile introduction, selected projects, technology icons, badges, and contact links.

## 1. Publishing architecture

```mermaid
flowchart LR
    EDIT[Edit README.md] --> MD[Markdown + HTML]
    MD --> EXT[External badges / images]
    MD --> LINKS[Project + contact links]
    LINKS --> GH[GitHub Profile Renderer]
    EXT --> GH
```

## 2. Profile update pipeline

```mermaid
flowchart TD
    CHANGE[New project / skill / profile change] --> VERIFY[Verify claim from real work]
    VERIFY --> README[Update README]
    README --> LINKS[Check links]
    LINKS --> MEDIA[Check icons/images/badges]
    MEDIA --> MOBILE[Preview desktop/mobile]
    MOBILE --> REVIEW[Review diff]
    REVIEW --> MERGE[Merge]
```

## 3. Content ownership

| Area | Source of truth |
| --- | --- |
| Bio / introduction | `README.md` |
| Featured projects | `README.md` project sections |
| Technology stack | README icons/badges |
| Contact links | README links |
| Rendering | GitHub profile README feature |

## 4. Verification gates

Before publishing:

- Project descriptions match actual repository capabilities.
- Private/internal implementation details are not exposed accidentally.
- Repository links resolve to the intended project.
- Contact links are valid.
- Image/badge URLs render correctly.
- Alt text or readable labels exist where appropriate.
- HTML tables and Markdown render acceptably on desktop and narrow screens.

## 5. Release pipeline

```mermaid
flowchart LR
    BRANCH[Documentation Branch] --> PREVIEW[Markdown Preview]
    PREVIEW --> DIFF[Review Diff]
    DIFF --> PR[Pull Request]
    PR --> MERGE[Merge to main]
    MERGE --> PROFILE[GitHub Profile Updated]
```

There is no application runtime, package manifest, server, database, or conventional CI requirement in the reviewed snapshot.

## 6. Reliability notes

```mermaid
flowchart TD
    README[README Content] --> GITHUB[GitHub Rendering]
    README --> EXTERNAL[External Image / Badge Services]
    EXTERNAL --> FAIL{Service available?}
    FAIL -->|Yes| OK[Asset renders]
    FAIL -->|No| BROKEN[Asset may appear broken]
```

External media can fail independently even when the README syntax is correct.

## 7. Source map

- [`README.md`](https://github.com/HidayahMF/HidayahMF/blob/9ae6037d4170d41c38acf4ba9d4defe5ea11e7d3/README.md)

Keep this guide synchronized when the profile structure, public project selection, or external media strategy changes.