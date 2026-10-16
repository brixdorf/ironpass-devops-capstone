// The IronPass mark: a lime tile with a barbell cut into it.
export default function Logo({ size = 36 }) {
  return (
    <svg
      className="logo-mark"
      width={size}
      height={size}
      viewBox="0 0 64 64"
      role="img"
      aria-label="IronPass logo"
    >
      <rect x="2" y="2" width="60" height="60" rx="16" fill="#C6FF3D" />
      <rect x="11" y="23" width="7" height="18" rx="2.5" fill="#0B1020" />
      <rect x="20" y="18" width="7" height="28" rx="2.5" fill="#0B1020" />
      <rect x="37" y="18" width="7" height="28" rx="2.5" fill="#0B1020" />
      <rect x="46" y="23" width="7" height="18" rx="2.5" fill="#0B1020" />
      <rect x="27" y="29" width="10" height="6" fill="#0B1020" />
    </svg>
  );
}
