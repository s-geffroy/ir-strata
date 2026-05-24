import React from 'react';

export default function ConfidenceBadge({label}: {label?: string}) {
  const text = label ?? 'unknown';
  const cls = text === 'very_high' ? 'badge-validated' : text === 'high' ? 'badge-reviewed' : text === 'medium' ? 'badge-draft' : 'badge-contested';
  return <span className={`badge ${cls}`}>{text}</span>;
}
