import { mkdir, readdir, readFile, rm, stat, writeFile } from "node:fs/promises"
import path from "node:path"

import matter from "gray-matter"

const repoRoot = process.cwd()
const excludedDirs = new Set([
  ".astro",
  ".git",
  ".venv",
  "dist",
  "node_modules",
  "src"
])
const excludedFiles = new Set(["AGENTS.md"])

function humanizeSegment(value) {
  return value
    .replace(/\.[^.]+$/, "")
    .replace(/[-_]+/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/\b\w/g, letter => letter.toUpperCase())
}

function inferTitle(relativePath, content, existingTitle) {
  if (typeof existingTitle === "string" && existingTitle.trim()) {
    return existingTitle.trim()
  }

  const labeledTitleMatch = content.match(/^Title:\s+(.+)$/m)

  if (labeledTitleMatch?.[1]) {
    return labeledTitleMatch[1].trim()
  }

  const headingMatch = content.match(/^#\s+(.+)$/m)

  if (headingMatch?.[1]) {
    return headingMatch[1].trim()
  }

  return humanizeSegment(path.basename(relativePath))
}

function inferDescription(content, existingDescription) {
  if (typeof existingDescription === "string" && existingDescription.trim()) {
    return existingDescription.trim()
  }

  const cleaned = content
    .replace(/^---[\s\S]*?---\s*/m, "")
    .split("\n")
    .map(line => line.trim())
    .find(
      line =>
        line &&
        line !== "---" &&
        !line.startsWith("#") &&
        !line.startsWith("- ") &&
        !line.startsWith("* ") &&
        !line.startsWith(">") &&
        !line.startsWith("```") &&
        !line.startsWith("Source:") &&
        !line.startsWith("Saved:") &&
        !line.startsWith("Title:") &&
        !line.startsWith("URL Source:") &&
        !line.startsWith("Published Time:") &&
        !line.startsWith("Markdown Content:")
    )

  return cleaned || undefined
}

function inferDate(relativePath, existingDate) {
  if (typeof existingDate === "string" && existingDate.trim()) {
    return existingDate.trim()
  }

  const match = relativePath.match(/\b(\d{4}-\d{2}-\d{2})\b/)
  return match?.[1]
}

function isExternalLink(href) {
  return /^(?:[a-z]+:|#|\/\/)/i.test(href)
}

function normalizeRelativeTarget(sourcePath, href, knownFiles) {
  const [targetPath] = href.split(/[?#]/)

  if (!targetPath) {
    return null
  }

  const normalized = targetPath.startsWith("/")
    ? targetPath.slice(1)
    : path.normalize(path.join(path.dirname(sourcePath), targetPath))

  const direct = normalized.replace(/\\/g, "/")

  if (knownFiles.has(direct)) {
    return direct
  }

  if (!path.extname(direct)) {
    const asMd = `${direct}.md`
    const asReadme = path.join(direct, "README.md").replace(/\\/g, "/")

    if (knownFiles.has(asMd)) {
      return asMd
    }

    if (knownFiles.has(asReadme)) {
      return asReadme
    }
  }

  return null
}

function rewriteMarkdownLinks(content, sourcePath, knownFiles, renamedTargets) {
  return content.replace(
    /(?<!!)\[([^\]]+)\]\(([^)]+)\)/g,
    (full, label, rawHref) => {
      const href = rawHref.trim()

      if (!href || isExternalLink(href)) {
        return full
      }

      const target = normalizeRelativeTarget(sourcePath, href, knownFiles)

      if (!target) {
        return full
      }

      const hashIndex = href.indexOf("#")
      const hash = hashIndex >= 0 ? href.slice(hashIndex) : ""
      const rewrittenTarget = renamedTargets.get(target) ?? target

      if (href.startsWith("/")) {
        return `[${label}](/${rewrittenTarget}${hash})`
      }

      const relativeTarget = path
        .relative(path.dirname(renamedTargets.get(sourcePath) ?? sourcePath), rewrittenTarget)
        .replace(/\\/g, "/")

      const normalizedRelativeTarget = relativeTarget.startsWith(".")
        ? relativeTarget
        : `./${relativeTarget}`

      return `[${label}](${normalizedRelativeTarget}${hash})`
    }
  )
}

function escapeForMdx(content) {
  const lines = content.split("\n")
  let inFence = false

  return lines
    .map(line => {
      if (/^```/.test(line.trim())) {
        inFence = !inFence
        return line
      }

      if (inFence) {
        return line
      }

      return line
        .replace(/</g, "&lt;")
        .replace(/{/g, "&#123;")
        .replace(/}/g, "&#125;")
    })
    .join("\n")
}

async function collectMarkdownFiles(currentDir, files = []) {
  const entries = await readdir(currentDir, { withFileTypes: true })

  for (const entry of entries) {
    if (excludedDirs.has(entry.name)) {
      continue
    }

    const absolutePath = path.join(currentDir, entry.name)
    const relativePath = path.relative(repoRoot, absolutePath).replace(/\\/g, "/")

    if (entry.isDirectory()) {
      await collectMarkdownFiles(absolutePath, files)
      continue
    }

    if (
      entry.isFile() &&
      absolutePath.endsWith(".md") &&
      !excludedFiles.has(relativePath)
    ) {
      files.push(relativePath)
    }
  }

  return files
}

async function main() {
  const sourceFiles = (await collectMarkdownFiles(repoRoot)).sort()
  const knownFiles = new Set([...sourceFiles, ...excludedFiles])
  const renamedTargets = new Map(
    sourceFiles.map(file => [file, file.replace(/\.md$/, ".mdx")])
  )

  for (const relativePath of sourceFiles) {
    const absolutePath = path.join(repoRoot, relativePath)
    const raw = await readFile(absolutePath, "utf8")
    const parsed = matter(raw)
    const fileStat = await stat(absolutePath)
    const title = inferTitle(relativePath, parsed.content, parsed.data.title)
    const description = inferDescription(
      parsed.content,
      parsed.data.description
    )
    const date = inferDate(relativePath, parsed.data.date)
    const content = escapeForMdx(
      rewriteMarkdownLinks(
        parsed.content,
        relativePath,
        knownFiles,
        renamedTargets
      )
    )
    const targetRelativePath = renamedTargets.get(relativePath)

    if (!targetRelativePath) {
      continue
    }

    const data = Object.fromEntries(
      Object.entries({
        ...parsed.data,
        title,
        description,
        date,
        updatedAt: fileStat.mtime.toISOString()
      }).filter(([, value]) => value !== undefined)
    )

    const targetPath = path.join(repoRoot, targetRelativePath)

    await mkdir(path.dirname(targetPath), { recursive: true })
    await writeFile(targetPath, matter.stringify(content, data))
    await rm(absolutePath)
  }
}

main().catch(error => {
  console.error(error)
  process.exitCode = 1
})
