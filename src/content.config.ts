import { defineCollection } from "astro:content"
import { glob } from "astro/loaders"
import { z } from "zod"

const docs = defineCollection({
  loader: glob({
    pattern: "**/*.mdx",
    base: "./src/content/docs"
  }),
  schema: z
    .object({
      title: z.string(),
      description: z.string().optional(),
      date: z.string().optional(),
      tags: z.array(z.string()).optional(),
      generatedPath: z.string(),
      sourcePath: z.string(),
      sourceDir: z.string(),
      kind: z.string(),
      generated: z.boolean().default(true)
    })
    .catchall(z.unknown())
})

export const collections = { docs }
