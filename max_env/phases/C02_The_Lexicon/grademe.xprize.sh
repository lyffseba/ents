#!/usr/bin/env bash
# Compatibility wrapper. The real Oracle is grademe.sh.
exec "$(cd "$(dirname "$0")" && pwd)/grademe.sh"
