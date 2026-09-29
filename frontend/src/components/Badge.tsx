import type { Category, Priority, Status } from "../api/types";

const categoryIcons: Record<Category, string> = { water: "◈", electricity: "ϟ", sanitation: "♲", roads: "◆", streetlights: "☼", other: "•" };

export function CategoryLabel({ category }: { category: Category }) {
  return <span className={`category category-${category}`}><span aria-hidden="true">{categoryIcons[category]}</span>{category}</span>;
}

export function PriorityBadge({ priority }: { priority: Priority }) {
  return <span className={`priority priority-${priority}`}>{priority} priority</span>;
}

export function StatusBadge({ status }: { status: Status }) {
  return <span className={`status status-${status}`}>{status.replace("_", " ")}</span>;
}
