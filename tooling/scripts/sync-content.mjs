import { mkdir, readdir, readFile, rm, stat, writeFile } from "node:fs/promises"
import path from "node:path"

import matter from "gray-matter"

const repoRoot = process.cwd()
const sourceRoot = repoRoot
const targetRoot = path.join(repoRoot, "src", "content", "docs")
const excludedDirs = new Set([
  ".astro",
  ".git",
  ".venv",
  "dist",
  "node_modules"
])

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

function rewriteMarkdownLinks(content, sourcePath, knownFiles) {
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
      const docId = target.replace(/\.md$/, ".mdx")
      const destination = `/?doc=${encodeURIComponent(docId)}${hash}`

      return `[${label}](${destination})`
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
    const relativePath = path
      .relative(sourceRoot, absolutePath)
      .replace(/\\/g, "/")

    if (relativePath.startsWith("src/content/docs/")) {
      continue
    }

    if (entry.isDirectory()) {
      await collectMarkdownFiles(absolutePath, files)
      continue
    }

    if (entry.isFile() && absolutePath.endsWith(".md")) {
      files.push(relativePath)
    }
  }

  return files
}

async function main() {
  const sourceFiles = (await collectMarkdownFiles(sourceRoot)).sort()
  const knownFiles = new Set(sourceFiles)

  await rm(targetRoot, { recursive: true, force: true })
  await mkdir(targetRoot, { recursive: true })

  for (const relativePath of sourceFiles) {
    const absolutePath = path.join(sourceRoot, relativePath)
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
      rewriteMarkdownLinks(parsed.content, relativePath, knownFiles)
    )
    const generatedPath = relativePath.replace(/\.md$/, ".mdx")
    const targetPath = path.join(targetRoot, generatedPath)

    const data = {
      ...parsed.data,
      title,
      description,
      date,
      generatedPath,
      sourcePath: relativePath,
      sourceDir: path.dirname(relativePath).replace(/\\/g, "/"),
      kind: relativePath.includes("/") ? relativePath.split("/")[0] : "root",
      generated: true,
      updatedAt: fileStat.mtime.toISOString()
    }
    const normalizedData = Object.fromEntries(
      Object.entries(data).filter(([, value]) => value !== undefined)
    )

    await mkdir(path.dirname(targetPath), { recursive: true })
    await writeFile(targetPath, matter.stringify(content, normalizedData))
  }

  const summaryPath = path.join(
    repoRoot,
    "src",
    "content",
    "docs",
    "_meta.json"
  )
  await writeFile(
    summaryPath,
    JSON.stringify(
      {
        generatedAt: new Date().toISOString(),
        count: sourceFiles.length
      },
      null,
      2
    )
  )
}

main().catch(error => {
  console.error(error)
  process.exitCode = 1
})
