import { defineCollection } from "astro:content"
import { glob } from "astro/loaders"
import { z } from "zod"

const docs = defineCollection({
  loader: glob({
    base: "./",
    pattern: ["resources/**/*.mdx"],
    generateId: ({ entry }) => entry.replace(/\\/g, "/")
  }),
  schema: z
    .object({
      title: z.string().optional(),
      description: z.string().optional(),
      date: z.string().optional(),
      tags: z.array(z.string()).optional(),
      kind: z.string().optional(),
      updatedAt: z.string().optional()
    })
    .catchall(z.unknown())
})

export const collections = { docs }
