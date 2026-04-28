import {
  createRouteManifestPayload,
  listRouteManifestEntries
} from "@/lib/route-manifest"

export async function GET() {
  const entries = await listRouteManifestEntries()

  return new Response(
    JSON.stringify(createRouteManifestPayload(entries), null, 2),
    {
      headers: {
        "Content-Type": "application/json; charset=utf-8"
      }
    }
  )
}
