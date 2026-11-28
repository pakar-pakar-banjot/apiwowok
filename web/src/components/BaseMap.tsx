import { MapContainer, TileLayer } from 'react-leaflet';
import { BASEMAP_ATTRIBUTION, BASEMAP_URL, INDONESIA_CENTER, INDONESIA_ZOOM } from '../constants';

/** Peta dasar statis; belum ada titik deteksi. Atribusi penyedia basemap wajib tampil (FR-G5). */
export default function BaseMap() {
  return (
    <section className="base-map" aria-label="Peta dasar Indonesia">
      <MapContainer center={INDONESIA_CENTER} zoom={INDONESIA_ZOOM} className="base-map__canvas">
        <TileLayer url={BASEMAP_URL} attribution={BASEMAP_ATTRIBUTION} />
      </MapContainer>
    </section>
  );
}
