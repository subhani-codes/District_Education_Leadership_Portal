// Navy primary + saffron secondary, sized to government e-governance style.
export default function Button({
  children,
  variant = 'primary',
  type = 'button',
  className = '',
  ...rest
}) {
  const base =
    'inline-flex items-center justify-center font-semibold rounded-md ' +
    'px-4 py-2 text-sm transition focus:outline-none focus:ring-2 ' +
    'focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';

  const variants = {
    primary:
      'bg-navy text-white hover:bg-[#08306e] focus:ring-navy',
    secondary:
      'bg-saffron text-white hover:bg-[#e6851f] focus:ring-saffron',
    ghost:
      'bg-white text-navy border border-navy hover:bg-navy hover:text-white focus:ring-navy',
    danger:
      'bg-red-600 text-white hover:bg-red-700 focus:ring-red-600',
  };

  return (
    <button
      type={type}
      className={`${base} ${variants[variant] || variants.primary} ${className}`}
      {...rest}
    >
      {children}
    </button>
  );
}
