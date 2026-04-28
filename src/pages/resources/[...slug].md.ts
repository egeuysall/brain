import { readFile } from "node:fs/promises"
import path from "node:path"

import { listDocs, toRoutePath } from "@/lib/docs"

export async function getStaticPaths() {
  const docs = await listDocs()

  return docs.map(doc => {
    const filePath = doc.filePath ?? doc.id
    const resourceSlug = toRoutePath(filePath).replace(/^resources\/?/, "")

    return {
      params: {
        slug: resourceSlug
      },
      props: {
        sourcePath: filePath
      }
    }
  })
}

function resolveResourcePath(sourcePath: string) {
  const normalizedPath = sourcePath.replace(/\\/g, "/")

  if (
    normalizedPath.startsWith("/") ||
    normalizedPath.includes("../") ||
    !normalizedPath.startsWith("resources/")
  ) {
    throw new Error(`Unsafe resource path: ${sourcePath}`)
  }

  return path.join(process.cwd(), normalizedPath)
}

export async function GET({ props }: { props: { sourcePath: string } }) {
  const markdown = await readFile(resolveResourcePath(props.sourcePath), "utf8")

  return new Response(markdown, {
    headers: {
      "Content-Type": "text/markdown; charset=utf-8"
    }
  })
}
