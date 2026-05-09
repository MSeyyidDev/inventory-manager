export type DeviceType = "laptop" | "monitor" | "smartphone" | "server" | "accessory";
export type DeviceStatus = "available" | "assigned" | "maintenance" | "retired";

export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface Device {
  id: number;
  type: DeviceType;
  manufacturer: string;
  model: string;
  serial_number: string;
  status: DeviceStatus;
  purchase_date: string | null;
  warranty_end: string | null;
  notes: string | null;
  location_id: number | null;
  assigned_to_id: number | null;
  assigned_to_name: string | null;
}

export interface DevicePayload {
  type: DeviceType;
  manufacturer: string;
  model: string;
  serial_number: string;
  status?: DeviceStatus;
  purchase_date?: string | null;
  warranty_end?: string | null;
  notes?: string | null;
  location_id?: number | null;
}

export interface Employee {
  id: number;
  first_name: string;
  last_name: string;
  full_name: string;
  email: string;
  department: string;
  role: string;
  location_id: number | null;
}

export interface EmployeePayload {
  first_name: string;
  last_name: string;
  email: string;
  department: string;
  role: string;
  location_id?: number | null;
}

export interface Location {
  id: number;
  name: string;
  city: string;
  country: string;
  address: string | null;
}

export interface Assignment {
  id: number;
  device_id: number;
  employee_id: number;
  assigned_at: string;
  returned_at: string | null;
  note: string | null;
  is_active: boolean;
  device_model?: string | null;
  device_serial?: string | null;
  employee_name?: string | null;
}

export interface StatsOverview {
  total_devices: number;
  total_employees: number;
  total_locations: number;
  active_assignments: number;
  devices_by_type: { key: string; count: number }[];
  devices_by_status: { key: string; count: number }[];
  devices_by_location: { key: string; count: number }[];
}
