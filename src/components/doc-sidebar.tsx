"use client"

import * as React from "react"

import { buildFileTree, FileTree } from "@/components/file-tree"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"

type SidebarDoc = {
  title: string
  path: string
  routePath: string
  href: string
  description: string
  keywords: string
}

type DocSidebarProps = {
  docs: SidebarDoc[]
  selectedPath?: string
}

const TREE_STORAGE_KEY = "ryva-brain:file-tree-expanded:v1"
const DEFAULT_EXPANDED_PATHS = new Set([
  "posts",
  "threads",
  "threads/reddit",
  "threads/twitter"
])

function getAncestorPaths(path?: string) {
  if (!path) {
    return []
  }

  const segments = path.split("/")
  const folderSegments = segments.slice(0, -1)

  return folderSegments.map((_, index) =>
    folderSegments.slice(0, index + 1).join("/")
  )
}

export function DocSidebar({ docs, selectedPath }: DocSidebarProps) {
  const [query, setQuery] = React.useState("")
  const [isReady, setIsReady] = React.useState(false)
  const [expandedPaths, setExpandedPaths] = React.useState<Set<string>>(
    () => new Set(DEFAULT_EXPANDED_PATHS)
  )
  const deferredQuery = React.useDeferredValue(query)
  const tokens = deferredQuery
    .trim()
    .toLowerCase()
    .split(/\s+/)
    .filter(Boolean)

  const filteredDocs =
    tokens.length === 0
      ? docs
      : docs.filter(doc => tokens.every(token => doc.keywords.includes(token)))

  React.useEffect(() => {
    const savedValue = window.localStorage.getItem(TREE_STORAGE_KEY)

    if (!savedValue) {
      setIsReady(true)
      return
    }

    try {
      const parsedPaths = JSON.parse(savedValue)

      if (Array.isArray(parsedPaths)) {
        setExpandedPaths(new Set(parsedPaths))
      }
    } catch {
      window.localStorage.removeItem(TREE_STORAGE_KEY)
    }

    setIsReady(true)
  }, [])

  React.useEffect(() => {
    if (!isReady) {
      return
    }

    window.localStorage.setItem(
      TREE_STORAGE_KEY,
      JSON.stringify([...expandedPaths])
    )
  }, [expandedPaths, isReady])

  const tree = buildFileTree(
    filteredDocs.map(doc => ({
      title: doc.title,
      path: doc.path,
      routePath: doc.routePath,
      href: doc.href
    }))
  )

  const selectedAncestors = getAncestorPaths(selectedPath)
  const searchExpandedPaths =
    tokens.length === 0
      ? []
      : filteredDocs.flatMap(doc => getAncestorPaths(doc.path))
  const effectiveExpandedPaths = new Set([
    ...expandedPaths,
    ...selectedAncestors,
    ...searchExpandedPaths
  ])

  return (
    <aside className="border border-line bg-panel flex h-full min-h-0 flex-col overflow-hidden">
      <div className="border-b border-line p-2.5">
        <Input
          value={query}
          onChange={event => setQuery(event.target.value)}
          type="search"
          placeholder="search files..."
          aria-label="Search files"
          autoComplete="off"
          spellCheck={false}
        />
      </div>

      <ScrollArea className="min-h-0 flex-1">
        {tree.length > 0 ? (
          <FileTree
            nodes={tree}
            selectedPath={selectedPath}
            expandedPaths={effectiveExpandedPaths}
            onExpandedChange={setExpandedPaths}
          />
        ) : (
          <div className="p-3 font-mono text-[0.65rem] tracking-[0.04em] text-muted">
            no files
          </div>
        )}
      </ScrollArea>
    </aside>
  )
}
