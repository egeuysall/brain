import { getCollection, render } from "astro:content"

const RESOURCE_PREFIX = "resources/"
const EXCLUDED_ROUTE_PATHS = new Set(["resources/plans/case-study"])

export function normalizeDocPath(slug?: string | string[]) {
  if (!slug) {
    return undefined
  }

  const rawPath = Array.isArray(slug) ? slug.join("/") : slug
  const normalizedPath = rawPath
    .replace(/^\/+/, "")
    .replace(/^src\/content\/docs\//, "")
    .replace(/\.(md|mdx)$/i, "")

  return normalizedPath.startsWith(RESOURCE_PREFIX) ? normalizedPath : undefined
}

export function toRoutePath(path: string) {
  return path.replace(/^src\/content\/docs\//, "").replace(/\.(md|mdx)$/i, "")
}

export function toDocHref(path: string) {
  return `/${toRoutePath(path)}`
}

export function toTreePath(path: string) {
  const normalizedPath = toRoutePath(path)
  return normalizedPath.startsWith(RESOURCE_PREFIX)
    ? normalizedPath.slice(RESOURCE_PREFIX.length)
    : normalizedPath
}

export async function listDocs() {
  const docs = await getCollection("docs")

  return docs
    .filter(
      doc => !EXCLUDED_ROUTE_PATHS.has(toRoutePath(doc.filePath ?? doc.id))
    )
    .sort((left, right) =>
      (left.filePath ?? left.id).localeCompare(right.filePath ?? right.id)
    )
}

function fallbackTitle(filePath: string) {
  const fileName =
    filePath
      .split("/")
      .at(-1)
      ?.replace(/\.(md|mdx)$/i, "") ?? filePath

  return fileName.replace(/[-_]+/g, " ").replace(/\s+/g, " ").trim()
}

export async function getDocsView(selectedPath?: string) {
  const docs = await listDocs()

  const currentDoc =
    (selectedPath
      ? docs.find(doc => toRoutePath(doc.filePath ?? doc.id) === selectedPath)
      : undefined) ??
    docs[0] ??
    null

  const rendered = currentDoc ? await render(currentDoc) : null

  const sidebarDocs = docs.map(doc => ({
    title: doc.data.title ?? fallbackTitle(doc.filePath ?? doc.id),
    path: toTreePath(doc.filePath ?? doc.id),
    routePath: toRoutePath(doc.filePath ?? doc.id),
    href: toDocHref(doc.filePath ?? doc.id),
    description: doc.data.description ?? "",
    keywords: [
      doc.data.title,
      doc.data.description ?? "",
      doc.filePath ?? doc.id,
      toTreePath(doc.filePath ?? doc.id),
      toRoutePath(doc.filePath ?? doc.id),
      ...(Array.isArray(doc.data.tags) ? doc.data.tags : [])
    ]
      .join(" ")
      .toLowerCase()
  }))

  return {
    docs,
    currentDoc,
    rendered,
    sidebarDocs
  }
}
