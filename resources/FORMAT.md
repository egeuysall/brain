# Resource File Format (Simple)

Use plain Markdown unless you need another format.

## Minimal convention

- First line: title (`# ...`)
- Optional metadata block at top (YAML front matter)
- Then body content

## Recommended metadata fields

```yaml
---
type: note | doc | article | newsletter | decision-log | transcript
date: 2026-03-21
author: Your Name
tags: [topic-a, topic-b]
source: optional URL
---
```

## Example: Article

```md
---
type: article
date: 2026-03-21
author: Ege
tags: [ai, product]
source: https://example.com/post
---

# Why Weekly Context Reviews Matter

Main points...
```

## Example: Newsletter

```md
---
type: newsletter
date: 2026-03-21
author: Ege
tags: [weekly, updates]
---

# Weekly Product Update #12

## Wins

- ...

## Risks

- ...

## Next Week

- ...
```

## Naming guidance

- Prefer dated filenames for time-sensitive files.
- Examples:
- `articles/2026-03-21-context-engineering.md`
- `newsletters/2026-03-21-weekly-update.md`
- `notes/customer-call-acme-2026-03-21.md`
