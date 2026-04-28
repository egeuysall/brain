import {
  createRouteManifestPayload,
  listRouteManifestEntries,
  ROUTES_PER_PAGE
} from "@/lib/route-manifest"

export async function getStaticPaths() {
  const entries = await listRouteManifestEntries()
  const totalPages = Math.max(1, Math.ceil(entries.length / ROUTES_PER_PAGE))

  return Array.from({ length: totalPages - 1 }, (_, index) => ({
    params: {
      page: String(index + 2)
    },
    props: {
      page: index + 2
    }
  }))
}

export async function GET({ props }: { props: { page: number } }) {
  const entries = await listRouteManifestEntries()

  return new Response(
    JSON.stringify(createRouteManifestPayload(entries, props.page), null, 2),
    {
      headers: {
        "Content-Type": "application/json; charset=utf-8"
      }
    }
  )
}
