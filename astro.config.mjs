import mdx from "@astrojs/mdx"
import react from "@astrojs/react"
import tailwindcss from "@tailwindcss/vite"
import { defineConfig } from "astro/config"

export default defineConfig({
  integrations: [mdx(), react()],
  markdown: {
    shikiConfig: {
      theme: "github-light"
    }
  },
  server: {
    host: "0.0.0.0",
    port: 3000
  },
  vite: {
    plugins: [tailwindcss()],
    resolve: {
      alias: {
        "@": new URL("./src", import.meta.url).pathname
      }
    }
  }
})
