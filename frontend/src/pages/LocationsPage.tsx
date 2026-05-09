import { PageHeader } from "@/components/PageHeader";
import { useLocations } from "@/features/locations/useLocations";

export function LocationsPage() {
  const locations = useLocations();

  return (
    <div>
      <PageHeader title="Locations" subtitle="Offices, sites and remote pools." />
      {locations.isLoading ? (
        <div>Loading…</div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {(locations.data ?? []).map((l) => (
            <div key={l.id} className="card">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold">{l.name}</h3>
                <span className="text-xs uppercase tracking-wide text-slate-500">
                  {l.country}
                </span>
              </div>
              <p className="mt-1 text-sm text-slate-500">{l.city}</p>
              {l.address ? (
                <p className="mt-3 text-xs text-slate-500">{l.address}</p>
              ) : null}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
