#!/usr/bin/env python3
import subprocess, sys
cmds = [
    [sys.executable, 'scripts/validate_model.py'],
    [sys.executable, 'scripts/compute_scores.py'],
    [sys.executable, 'scripts/generate_exports.py'],
    [sys.executable, 'scripts/generate_mdx.py'],
]
for cmd in cmds:
    subprocess.check_call(cmd)
print('Pre-build pipeline OK. Run npm run build next.')
