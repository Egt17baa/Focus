const RADIUS = 92
const CIRCUMFERENCE = 2 * Math.PI * RADIUS

export default function TimerRing({ progress, label, caption }) {
  return (
    <div className="relative mx-auto h-56 w-56">
      <svg viewBox="0 0 200 200" className="h-full w-full -rotate-90">
        <circle cx="100" cy="100" r={RADIUS} className="fill-none stroke-white/10" strokeWidth="12" />
        <circle
          cx="100"
          cy="100"
          r={RADIUS}
          className="fill-none stroke-sky-400 transition-[stroke-dashoffset] duration-500"
          strokeWidth="12"
          strokeLinecap="round"
          strokeDasharray={CIRCUMFERENCE}
          strokeDashoffset={CIRCUMFERENCE * (1 - progress)}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-mono text-4xl font-bold tabular-nums">{label}</span>
        {caption ? <span className="mt-1 text-xs text-slate-400">{caption}</span> : null}
      </div>
    </div>
  )
}
