"""Reviewed first-time aid guidance and shared checklist definitions."""

import json
from pathlib import Path


STEP_PREFIX = 'first-aid-'
GUIDANCE = json.loads(Path(__file__).with_name('aid_guidance.json').read_text(encoding='utf-8'))
