import clsx from "clsx";
import type { DeviceStatus } from "@/api/types";

const STATUS_COLORS: Record<DeviceStatus, string> = {
  available:
    "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-200",
  assigned: "bg-brand-100 text-brand-800 dark:bg-brand-900/40 dark:text-brand-200",
  maintenance:
    "bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-200",
  retired: "bg-slate-200 text-slate-700 dark:bg-slate-800 dark:text-slate-300",
};

export function Badge({
  children,
  status,
  className,
}: {
  children: React.ReactNode;
  status?: DeviceStatus;
  className?: string;
}) {
  return (
    <span
      className={clsx(
        "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium capitalize",
        status
          ? STATUS_COLORS[status]
          : "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300",
        className
      )}
    >
      {children}
    </span>
  );
}
