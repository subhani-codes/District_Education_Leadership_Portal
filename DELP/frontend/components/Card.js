// White card with a subtle border + shadow. Used for grouping on dashboards.
export default function Card({ title, action, children, className = '' }) {
  return (
    <section
      className={`bg-white border border-line rounded-lg shadow-sm ${className}`}
    >
      {(title || action) && (
        <header className="flex items-center justify-between border-b border-line px-5 py-3">
          {title && <h2 className="text-base font-semibold text-navy">{title}</h2>}
          {action}
        </header>
      )}
      <div className="p-5">{children}</div>
    </section>
  );
}
