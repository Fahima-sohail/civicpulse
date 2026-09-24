import { Component, type ErrorInfo, type ReactNode } from "react";

interface State { hasError: boolean; }
export class ErrorBoundary extends Component<{ children: ReactNode }, State> {
  state: State = { hasError: false };
  static getDerivedStateFromError(): State { return { hasError: true }; }
  componentDidCatch(_error: Error, _info: ErrorInfo) { /* reserved for an error reporter */ }
  render() {
    if (this.state.hasError) return <main className="error-screen"><p className="eyebrow">CivicPulse</p><h1>We need a quiet moment.</h1><p>The page did not load as expected. Your browser has not submitted anything automatically.</p><button onClick={() => window.location.reload()}>Try again</button></main>;
    return this.props.children;
  }
}
