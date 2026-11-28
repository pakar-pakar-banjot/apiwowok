import type { LatLngTuple } from 'leaflet';

/** Titik tengah dan zoom awal yang menampilkan kepulauan Indonesia. */
export const INDONESIA_CENTER: LatLngTuple = [-2.5, 118];
export const INDONESIA_ZOOM = 5;

/**
 * Penyedia basemap sementara: tile OpenStreetMap standar (ASSUMPTION).
 * Penyedia final dan kebijakan pemakaian tile dipilih tim sebelum dipublikasikan
 * (FR-G5 mewajibkan atribusi penyedia basemap).
 */
export const BASEMAP_URL = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';
export const BASEMAP_ATTRIBUTION =
  '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';
