import React, {useState} from 'react';
import profilesData from '../data/canonical/weight_profiles.json';

export default function WeightControlPanel() {
  const profiles = (profilesData as any).profiles;
  const [profileId, setProfileId] = useState('default');
  const profile = profiles.find((p: any) => p.profile_id === profileId) ?? profiles[0];
  return (
    <div className="atlas-card">
      <h3>Profil de pondération</h3>
      <select value={profileId} onChange={(e) => setProfileId(e.target.value)}>
        {profiles.map((p: any) => <option key={p.profile_id} value={p.profile_id}>{p.label_fr}</option>)}
      </select>
      <ul>
        {Object.entries(profile.weights).map(([k, v]: any) => <li key={k}><code>{k}</code> : {(v * 100).toFixed(0)}%</li>)}
      </ul>
      <p><strong>Note :</strong> le recalcul avancé côté navigateur est prévu, mais volontairement séparé du canonique.</p>
    </div>
  );
}
