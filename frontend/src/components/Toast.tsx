export function Toast({ message, onDismiss }: { message: string; onDismiss: () => void }) {
  return <div className="toast" role="alert"><span>{message}</span><button aria-label="Dismiss message" onClick={onDismiss}>×</button></div>;
}
