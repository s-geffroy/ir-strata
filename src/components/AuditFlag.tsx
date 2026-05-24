import React from 'react';

export default function AuditFlag({status}: {status?: string}) {
  if (!status) return null;
  return <span className="badge badge-draft">⚠️ {status}</span>;
}
