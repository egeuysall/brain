import * as React from "react"

import { cn } from "@/lib/utils"

export type FileTreeNode = {
  name: string
  path: string
  title?: string
  href?: string
  kind: "folder" | "file"
  children?: FileTreeNode[]
}

type FileTreeEntry = {
  title: string
  generatedPath: string
  href: string
}

type FileTreeProps = {
  nodes: FileTreeNode[]
  selectedPath?: string
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
    const segments = entry.generatedPath.split("/")
    let currentLevel = roots
    let currentPath = ""

    segments.forEach((segment, index) => {
      currentPath = currentPath ? `${currentPath}/${segment}` : segment
      const isLast = index === segments.length - 1

      if (isLast) {
        currentLevel.push({
          name: segment,
          path: entry.generatedPath,
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

function nodeContainsSelection(
  node: FileTreeNode,
  selectedPath?: string
): boolean {
  if (!selectedPath) {
    return false
  }

  if (node.path === selectedPath) {
    return true
  }

  return (
    node.children?.some(child => nodeContainsSelection(child, selectedPath)) ??
    false
  )
}

function FileTreeBranch({
  node,
  selectedPath,
  depth
}: {
  node: FileTreeNode
  selectedPath?: string
  depth: number
}) {
  const isActive = node.path === selectedPath
  const isExpanded = nodeContainsSelection(node, selectedPath) || depth === 0

  if (node.kind === "file") {
    return (
      <li className="list-none">
        <a
          href={node.href}
          data-active={isActive ? "true" : "false"}
          className="row-link block py-2"
        >
          <p className={cn("text-sm leading-tight", isActive && "font-medium")}>
            {node.title ?? node.name}
          </p>
          <p className="text-muted mt-0.5 font-mono text-[0.62rem] tracking-[0.14em] uppercase">
            {node.name}
          </p>
        </a>
      </li>
    )
  }

  return (
    <li className="list-none">
      <details open={isExpanded} className="group">
        <summary className="text-foreground cursor-pointer list-none py-1.5 font-mono text-[0.66rem] tracking-[0.16em] uppercase marker:hidden">
          <span className="inline-flex items-center gap-2">
            <span className="text-muted inline-block transition-transform duration-150 group-open:rotate-90">
              -
            </span>
            <span>{node.name}</span>
          </span>
        </summary>
        <ul className="border-line ml-2.5 border-l pl-3">
          {node.children?.map(child => (
            <FileTreeBranch
              key={child.path}
              node={child}
              selectedPath={selectedPath}
              depth={depth + 1}
            />
          ))}
        </ul>
      </details>
    </li>
  )
}

export function FileTree({ nodes, selectedPath }: FileTreeProps) {
  return (
    <ul className="space-y-0.5 px-4 pb-4">
      {nodes.map(node => (
        <FileTreeBranch
          key={node.path}
          node={node}
          selectedPath={selectedPath}
          depth={0}
        />
      ))}
    </ul>
  )
}
