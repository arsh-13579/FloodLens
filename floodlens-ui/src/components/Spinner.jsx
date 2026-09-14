export default function Spinner({ label }) {
  return (
    <div className="fl-spinner-row">
      <span className="fl-spinner" />
      {label && <span className="fl-spinner-label">{label}</span>}
    </div>
  )
}
