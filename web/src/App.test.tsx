import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import App from './App';
import { BASEMAP_ATTRIBUTION, BASEMAP_URL, INDONESIA_CENTER } from './constants';

describe('App (D-P4-001)', () => {
  it('menampilkan judul dan peta dasar berbahasa Indonesia', () => {
    render(<App />);
    expect(screen.getByRole('heading', { name: 'NusaFire' })).toBeInTheDocument();
    expect(screen.getByLabelText('Peta dasar Indonesia')).toBeInTheDocument();
  });

  it('menampilkan atribusi penyedia basemap (FR-G5)', () => {
    render(<App />);
    expect(screen.getByRole('link', { name: 'OpenStreetMap' })).toHaveAttribute(
      'href',
      'https://www.openstreetmap.org/copyright',
    );
  });

  it('tidak memakai kata "kebakaran" di teks antarmuka (FR-G1)', () => {
    const { container } = render(<App />);
    expect(container.textContent?.toLowerCase()).not.toContain('kebakaran');
  });
});

describe('konstanta peta', () => {
  it('berpusat di wilayah Indonesia dan memakai URL tile + atribusi', () => {
    const [lat, lng] = INDONESIA_CENTER;
    expect(lat).toBeGreaterThan(-11);
    expect(lat).toBeLessThan(6);
    expect(lng).toBeGreaterThan(95);
    expect(lng).toBeLessThan(141);
    expect(BASEMAP_URL).toContain('{z}/{x}/{y}');
    expect(BASEMAP_ATTRIBUTION).toContain('OpenStreetMap');
  });
});
