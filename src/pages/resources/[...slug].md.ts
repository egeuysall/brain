import { listDocs, toRoutePath } from "@/lib/docs"

const resourceFiles = import.meta.glob("../../../resources/**/*.{md,mdx}", {
  eager: true,
  import: "default",
  query: "?raw"
}) as Record<string, string>

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

  return `../../../${normalizedPath}`
}

export async function GET({ props }: { props: { sourcePath: string } }) {
  const markdown = resourceFiles[resolveResourcePath(props.sourcePath)]

  if (!markdown) {
    return new Response("Not found", { status: 404 })
  }

  return new Response(markdown, {
    headers: {
      "Content-Type": "text/markdown; charset=utf-8"
    }
  })
}
