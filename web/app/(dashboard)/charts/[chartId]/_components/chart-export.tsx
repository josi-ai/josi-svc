'use client';

import { useState } from 'react';
import { Download, Printer } from 'lucide-react';
import type { ChartDetail, ChartDetailPerson } from '@/types';
import { generateChartText, getExportFilename } from '@/lib/chart-export-text';
import { generateChartHTML } from '@/lib/chart-export-pdf';

interface ChartExportProps {
  chart: ChartDetail;
  person?: ChartDetailPerson | null;
}

const btnBase: React.CSSProperties = {
  display: 'inline-flex',
  alignItems: 'center',
  gap: 5,
  padding: '7px 12px',
  fontSize: 12,
  fontWeight: 500,
  background: 'transparent',
  border: '1px solid var(--gold-bg, #d4a843)',
  borderRadius: 8,
  cursor: 'pointer',
  color: 'var(--gold, #c9a23a)',
  transition: 'background 0.15s, color 0.15s',
};

export function ChartExport({ chart, person }: ChartExportProps) {
  const [downloading, setDownloading] = useState(false);

  const handleTextExport = () => {
    setDownloading(true);
    try {
      const text = generateChartText(chart, person);
      const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = getExportFilename(person);
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } finally {
      setDownloading(false);
    }
  };

  const handlePrint = () => {
    const html = generateChartHTML(chart, person);
    // Use a data URI in an iframe to avoid document.write
    const blob = new Blob([html], { type: 'text/html;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const win = window.open(url, '_blank');
    // Clean up blob URL after the window loads
    if (win) {
      win.addEventListener('load', () => URL.revokeObjectURL(url));
    } else {
      URL.revokeObjectURL(url);
    }
  };

  return (
    <>
      <button
        onClick={handleTextExport}
        disabled={downloading}
        style={{
          ...btnBase,
          opacity: downloading ? 0.6 : 1,
          cursor: downloading ? 'not-allowed' : 'pointer',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.background = 'var(--gold-bg-subtle, rgba(201,162,58,0.08))';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.background = 'transparent';
        }}
      >
        <Download style={{ width: 13, height: 13 }} />
        {downloading ? 'Exporting...' : 'Export Text'}
      </button>
      <button
        onClick={handlePrint}
        style={btnBase}
        onMouseEnter={(e) => {
          e.currentTarget.style.background = 'var(--gold-bg-subtle, rgba(201,162,58,0.08))';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.background = 'transparent';
        }}
      >
        <Printer style={{ width: 13, height: 13 }} />
        Print / PDF
      </button>
    </>
  );
}
