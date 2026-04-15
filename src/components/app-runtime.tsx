"use client"

import * as React from "react"

import { toast, Toaster } from "sonner"

export function AppRuntime() {
  React.useEffect(() => {
    const cleanups: Array<() => void> = []
    const blocks = document.querySelectorAll<HTMLElement>("[data-doc-body] pre")
    const links = document.querySelectorAll<HTMLAnchorElement>("[data-doc-body] a[href]")
    const docNavRoot = document.querySelector<HTMLElement>("[data-doc-nav]")
    const previousHref = docNavRoot?.dataset.prevHref
    const nextHref = docNavRoot?.dataset.nextHref

    for (const link of links) {
      const href = link.getAttribute("href")

      if (!href || href.startsWith("#") || href.startsWith("http")) {
        continue
      }

      const normalizedHref = href
        .replace(/^\/?src\/content\/docs\/resources\//, "/resources/")
        .replace(/\.(md|mdx)(?=$|#|\?)/i, "")

      if (normalizedHref !== href) {
        link.setAttribute("href", normalizedHref)
      }
    }

    const handleArrowNavigation = (event: KeyboardEvent) => {
      if (event.defaultPrevented || event.metaKey || event.ctrlKey || event.altKey) {
        return
      }

      const target = event.target as HTMLElement | null
      const tagName = target?.tagName?.toLowerCase()
      const isTypingTarget =
        target?.isContentEditable ||
        tagName === "input" ||
        tagName === "textarea" ||
        tagName === "select"

      if (isTypingTarget) {
        return
      }

      if (event.key === "ArrowLeft" && previousHref) {
        window.location.assign(previousHref)
      }

      if (event.key === "ArrowRight" && nextHref) {
        window.location.assign(nextHref)
      }
    }

    window.addEventListener("keydown", handleArrowNavigation)
    cleanups.push(() => window.removeEventListener("keydown", handleArrowNavigation))

    for (const block of blocks) {
      const code = block.querySelector("code")

      if (!code || block.dataset.copyBound === "true") {
        continue
      }

      block.dataset.copyBound = "true"
      block.classList.add("copy-code-surface")
      block.tabIndex = 0
      block.setAttribute("role", "button")
      block.setAttribute("aria-label", "Copy code block")

      const copyCode = async () => {
        try {
          await navigator.clipboard.writeText(code.textContent ?? "")
          toast.success("Code copied", { duration: 1200 })
        } catch {
          toast.error("Copy failed", { duration: 1200 })
        }
      }

      const handleClick = () => {
        void copyCode()
      }

      const handleKeyDown = (event: KeyboardEvent) => {
        if (event.key !== "Enter" && event.key !== " ") {
          return
        }

        event.preventDefault()
        void copyCode()
      }

      block.addEventListener("click", handleClick)
      block.addEventListener("keydown", handleKeyDown)
      cleanups.push(() => {
        block.removeEventListener("click", handleClick)
        block.removeEventListener("keydown", handleKeyDown)
      })
    }

    return () => {
      for (const cleanup of cleanups) {
        cleanup()
      }
    }
  }, [])

  return (
    <Toaster
      theme="light"
      className="toaster group"
      position="top-center"
      richColors={false}
      toastOptions={{
        unstyled: false
      }}
      style={
        {
          "--normal-bg": "rgba(255, 252, 245, 0.96)",
          "--normal-text": "var(--foreground)",
          "--normal-border": "var(--line)",
          "--border-radius": "0px"
        } as React.CSSProperties
      }
    />
  )
}
