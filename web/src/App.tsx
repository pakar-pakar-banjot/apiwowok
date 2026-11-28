import BaseMap from './components/BaseMap';

/**
 * Kerangka awal aplikasi (D-P4-001): hanya peta dasar statis dengan atribusi.
 * Data deteksi, filter, disclaimer final (HD-25), dan atribusi FIRMS/BIG ditambahkan
 * di tugas Fase 6 setelah kontrak API (openapi.yaml) disetujui.
 */
export default function App() {
  return (
    <main className="app">
      <header className="app__header">
        <h1>NusaFire</h1>
        <p>Peta dasar Indonesia</p>
      </header>
      <BaseMap />
    </main>
  );
}
