"use client"

import * as React from "react"

import { cn } from "@/lib/utils"

export type FileTreeNode = {
  name: string
  path: string
  routePath?: string
  title?: string
  href?: string
  kind: "folder" | "file"
  children?: FileTreeNode[]
}

type FileTreeEntry = {
  title: string
  path: string
  routePath: string
  href: string
}

type FileTreeProps = {
  nodes: FileTreeNode[]
  selectedPath?: string
  expandedPaths?: Set<string>
  onExpandedChange?: (expandedPaths: Set<string>) => void
}

function sortNodes(nodes: FileTreeNode[]) {
  return nodes.sort((left, right) => {
    if (left.kind !== right.kind) {
      return left.kind === "folder" ? -1 : 1
    }

    return left.name.localeCompare(right.name)
  })
}

export function buildFileTree(entries: FileTreeEntry[]): FileTreeNode[] {
  const roots: FileTreeNode[] = []
  const folders = new Map<string, FileTreeNode>()

  for (const entry of entries) {
    const segments = entry.path.split("/")
    let currentLevel = roots
    let currentPath = ""

    segments.forEach((segment, index) => {
      currentPath = currentPath ? `${currentPath}/${segment}` : segment
      const isLast = index === segments.length - 1

      if (isLast) {
        currentLevel.push({
          name: segment,
          path: entry.path,
          routePath: entry.routePath,
          title: entry.title,
          href: entry.href,
          kind: "file"
        })
        return
      }

      let folder = folders.get(currentPath)

      if (!folder) {
        folder = {
          name: segment,
          path: currentPath,
          kind: "folder",
          children: []
        }
        folders.set(currentPath, folder)
        currentLevel.push(folder)
      }

      currentLevel = folder.children ?? []
    })
  }

  const visit = (nodes: FileTreeNode[]) => {
    for (const node of nodes) {
      if (node.children) {
        visit(node.children)
        sortNodes(node.children)
      }
    }

    sortNodes(nodes)
  }

  visit(roots)

  return roots
}

function FileTreeBranch({
  node,
  selectedPath,
  expandedPaths,
  onExpandedChange
}: {
  node: FileTreeNode
  selectedPath?: string
  expandedPaths: Set<string>
  onExpandedChange: (expandedPaths: Set<string>) => void
}) {
  const isActive = node.path === selectedPath
  const isExpanded = expandedPaths.has(node.path)

  const toggleFolder = React.useCallback(() => {
    const nextExpandedPaths = new Set(expandedPaths)

    if (isExpanded) {
      nextExpandedPaths.delete(node.path)
    } else {
      nextExpandedPaths.add(node.path)
    }

    onExpandedChange(nextExpandedPaths)
  }, [expandedPaths, isExpanded, node.path, onExpandedChange])

  if (node.kind === "file") {
    return (
      <li className="list-none">
        <a
          href={node.href}
          data-active={isActive ? "true" : "false"}
          className="row-link block py-1"
        >
          <p className={cn("text-[0.86rem] leading-tight", isActive && "font-medium")}>
            {node.title ?? node.name}
          </p>
          <p className="text-muted mt-0.5 font-mono text-[0.6rem] tracking-[0.04em]">
            {node.name}
          </p>
        </a>
      </li>
    )
  }

  return (
    <li className="list-none">
      <div className="group">
        <button
          type="button"
          onClick={toggleFolder}
          className="text-foreground flex w-full cursor-pointer items-center gap-2 py-0.5 text-left font-mono text-[0.66rem] tracking-[0.04em]"
          aria-expanded={isExpanded}
        >
          <span
            className={cn(
              "text-muted inline-flex size-3 items-center justify-center transition-transform duration-150",
              isExpanded && "rotate-90"
            )}
          >
            -
          </span>
          <span>{node.name}</span>
        </button>
        <ul
          className={cn(
            "border-line ml-1.5 border-l pl-2",
            !isExpanded && "hidden"
          )}
        >
          {node.children?.map(child => (
            <FileTreeBranch
              key={child.path}
              node={child}
              selectedPath={selectedPath}
              expandedPaths={expandedPaths}
              onExpandedChange={onExpandedChange}
            />
          ))}
        </ul>
      </div>
    </li>
  )
}

export function FileTree({
  nodes,
  selectedPath,
  expandedPaths = new Set(),
  onExpandedChange = () => {}
}: FileTreeProps) {
  return (
    <ul className="space-y-0 px-3 py-1.5">
      {nodes.map(node => (
        <FileTreeBranch
          key={node.path}
          node={node}
          selectedPath={selectedPath}
          expandedPaths={expandedPaths}
          onExpandedChange={onExpandedChange}
        />
      ))}
    </ul>
  )
}
