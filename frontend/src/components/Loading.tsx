export function Loading({ label = "Working carefully…" }: { label?: string }) {
  return <span className="loading" role="status"><span className="loading-orb" aria-hidden="true" />{label}</span>;
}
