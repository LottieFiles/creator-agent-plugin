#!/usr/bin/env bash
# Run deterministic public distribution checks. No network or secrets are required.
set -euo pipefail

script_dir="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
repository_dir="$(CDPATH='' cd -- "$script_dir/.." && pwd)"
cd "$repository_dir"

python3 scripts/generate.py --check
python3 scripts/validate.py
python3 scripts/check-json.py
python3 scripts/check-content.py
python3 scripts/check-public.py
python3 scripts/check-provenance.py
python3 scripts/check-contract.py
python3 scripts/check-paths.py
python3 scripts/check-platforms.py
python3 scripts/check-package.py

for tool in actionlint zizmor shellcheck gitleaks; do
  if command -v "$tool" >/dev/null 2>&1; then
    case "$tool" in
      actionlint) actionlint .github/workflows/*.yml ;;
      zizmor) zizmor .github ;;
      shellcheck) shellcheck scripts/check.sh ;;
      gitleaks) gitleaks detect --source . --no-banner --redact ;;
    esac
  else
    echo "Optional local tool not installed: $tool" >&2
  fi
done
