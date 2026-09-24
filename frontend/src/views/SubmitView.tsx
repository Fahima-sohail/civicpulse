import { FormEvent, useState } from "react";
import { api } from "../api/client";
import type { ApiError, Complaint } from "../api/types";
import { CategoryLabel, PriorityBadge } from "../components/Badge";
import { Loading } from "../components/Loading";

type FormState = { text: string; location: string; reporter_contact: string };
const initial: FormState = { text: "", location: "", reporter_contact: "" };

function validate(values: FormState) {
  const errors: Partial<Record<keyof FormState, string>> = {};
  if (values.text.trim().length < 10 || values.text.length > 2000) errors.text = "Please describe the issue in 10 to 2,000 characters.";
  if (values.location.trim().length < 3 || values.location.length > 200) errors.location = "Please provide a location in 3 to 200 characters.";
  return errors;
}

export function SubmitView() {
  const [values, setValues] = useState(initial);
  const [errors, setErrors] = useState<Partial<Record<keyof FormState, string>>>({});
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<Complaint | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const update = (name: keyof FormState, value: string) => setValues((current) => ({ ...current, [name]: value }));

  async function submit(event: FormEvent) {
    event.preventDefault();
    const nextErrors = validate(values);
    setErrors(nextErrors); setMessage(null); setResult(null);
    if (Object.keys(nextErrors).length) return;
    setSubmitting(true);
    try {
      setResult(await api.createComplaint({ ...values, reporter_contact: values.reporter_contact || undefined }));
      setValues(initial);
    } catch (caught) {
      const error = caught as ApiError;
      setMessage(error.status === 429 ? `We are receiving many reports right now. Please try again in ${error.retryAfter ?? "a moment"} seconds.` : error.detail);
    } finally { setSubmitting(false); }
  }

  return <section className="view submit-view">
    <div className="view-intro"><p className="eyebrow">Citizen intake</p><h1>Report what needs attention.</h1><p>Share what you see. CivicPulse will route it to the right team.</p></div>
    <div className="two-column">
      <form className="card complaint-form" onSubmit={submit} noValidate>
        <label htmlFor="text">What is happening?</label>
        <textarea id="text" value={values.text} onChange={(e) => update("text", e.target.value)} aria-invalid={Boolean(errors.text)} aria-describedby="text-help text-error" placeholder="For example: Water is leaking across the road near the school gate." />
        <div className="field-meta"><span id="text-help">10–2,000 characters</span><span>{values.text.length}/2000</span></div>
        {errors.text && <p className="field-error" id="text-error">{errors.text}</p>}
        <label htmlFor="location">Location</label>
        <input id="location" value={values.location} onChange={(e) => update("location", e.target.value)} aria-invalid={Boolean(errors.location)} placeholder="Street, block, landmark or neighbourhood" />
        {errors.location && <p className="field-error">{errors.location}</p>}
        <label htmlFor="contact">Contact <span className="optional">optional</span></label>
        <input id="contact" value={values.reporter_contact} onChange={(e) => update("reporter_contact", e.target.value)} placeholder="Phone or email, if you want an update" />
        {message && <p className="form-message" role="alert">{message}</p>}
        <button className="primary-button" disabled={submitting} type="submit">{submitting ? <Loading label="Triage is reviewing your report…" /> : "Submit report"}</button>
      </form>
      <aside className="help-card"><span className="help-number">01</span><h2>A clear note helps.</h2><p>Include the exact place, how long it has been happening, and whether anyone is in immediate danger.</p><span className="help-number">02</span><h2>We confirm the route.</h2><p>Your result shows the category and urgency chosen by the triage service.</p></aside>
    </div>
    {result && <section className="result-card" aria-live="polite"><p className="eyebrow">Report received</p><h2>Your report has been sent for action.</h2><div className="result-tags"><CategoryLabel category={result.category} /><PriorityBadge priority={result.priority} /></div><p className="summary">{result.ai_summary || "Your report is ready for the operations team."}</p><p className="provider-line">Triaged by <strong>{result.triaged_by}</strong> in {result.triage_latency_ms}ms</p></section>}
  </section>;
}
