export default function BarChart({ data, labelKey, valueKey, formatLabel = (value) => value, unit = 'min' }) {
  const max = Math.max(1, ...data.map((item) => item[valueKey]))

  return (
    <div className="flex h-40 items-end gap-1">
      {data.map((item) => {
        const value = item[valueKey]
        const height = Math.round((value / max) * 100)
        return (
          <div key={item[labelKey]} className="group relative flex flex-1 flex-col items-center justify-end">
            <div
              className="w-full rounded-t bg-gradient-to-t from-sky-600/40 to-sky-400 transition group-hover:from-sky-500/60"
              style={{ height: `${Math.max(height, value > 0 ? 4 : 1)}%` }}
            />
            <span className="pointer-events-none absolute -top-7 hidden whitespace-nowrap rounded bg-slate-800 px-2 py-1 text-[11px] text-slate-100 group-hover:block">
              {formatLabel(item[labelKey])}: {value} {unit}
            </span>
          </div>
        )
      })}
    </div>
  )
}
