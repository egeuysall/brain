import { listDocs, toDocHref, toRoutePath, toTreePath } from "@/lib/docs"

export const SITE_URL = "https://brain.egeuysal.com"

export function toAbsoluteUrl(href: string) {
  return new URL(href, SITE_URL).toString()
}

export function toMarkdownHref(routePath: string) {
  const resourcePath = routePath.replace(/^resources\/?/, "")
  return `/resources/${resourcePath}.md`
}

export async function listRouteManifestEntries() {
  const docs = await listDocs()

  return docs.map(doc => {
    const filePath = doc.filePath ?? doc.id
    const routePath = toRoutePath(filePath)
    const href = toDocHref(filePath)
    const legacyHref = `/${routePath.replace(
      /^resources\//,
      "src/content/docs/resources/"
    )}`
    const markdownHref = toMarkdownHref(routePath)

    return {
      id: doc.id,
      title: doc.data.title ?? null,
      description: doc.data.description ?? null,
      date: doc.data.date ?? null,
      tags: Array.isArray(doc.data.tags) ? doc.data.tags : [],
      kind: doc.data.kind ?? null,
      updatedAt: doc.data.updatedAt ?? null,
      sourcePath: filePath,
      treePath: toTreePath(filePath),
      routePath,
      href,
      url: toAbsoluteUrl(href),
      legacyHref,
      legacyUrl: toAbsoluteUrl(legacyHref),
      markdownHref,
      markdownUrl: toAbsoluteUrl(markdownHref)
    }
  })
}
