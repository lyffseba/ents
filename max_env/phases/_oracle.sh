#!/usr/bin/env bash
# Shared Oracle of Fangorn helpers. Source from each module's grademe.sh.
# Never echo expected answers as a fallback. Failures must fail.

_ORACLE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ORACLE_ROOT="$(cd "$_ORACLE_DIR/.." && pwd)"
PIXI_MANIFEST="$ORACLE_ROOT/pixi.toml"

# Modular MAX/Mojo write absolute paths into share/max/modular.cfg at install
# time. Relocating the repo (or cloning onto another machine) breaks mojo
# unless we rewrite those paths to the current prefix.
_oracle_fix_modular_cfg() {
    local prefix cfg old
    prefix="$ORACLE_ROOT/.pixi/envs/default"
    cfg="$prefix/share/max/modular.cfg"
    [[ -f "$cfg" ]] || return 0
    if grep -q "$prefix" "$cfg" 2>/dev/null; then
        return 0
    fi
    old="$(python3 -c "import re,pathlib; t=pathlib.Path('$cfg').read_text(); m=re.search(r'package_root = (.*)', t); print(m.group(1) if m else '')" 2>/dev/null || true)"
    if [[ -n "$old" && "$old" != "$prefix" ]]; then
        python3 -c "from pathlib import Path; p=Path('$cfg'); t=p.read_text(); p.write_text(t.replace('$old', '$prefix'))"
    fi
}
_oracle_fix_modular_cfg

ORACLE_PASS=0
ORACLE_FAIL=0
ORACLE_SKIP=0

oracle_capture() {
    local workdir="$1"
    shift
    local out err rc
    out="$(mktemp)"
    err="$(mktemp)"
    if [[ ! -f "$PIXI_MANIFEST" ]]; then
        echo "[oracle] missing pixi.toml at $PIXI_MANIFEST"
        rm -f "$out" "$err"
        return 127
    fi
    (cd "$workdir" && pixi run --manifest-path "$PIXI_MANIFEST" "$@" >"$out" 2>"$err")
    rc=$?
    cat "$out"
    if [[ $rc -ne 0 && -s "$err" ]]; then
        echo "[oracle stderr] $(tr '\n' ' ' <"$err")" >&2
    fi
    rm -f "$out" "$err"
    return $rc
}

oracle_capture_mojo() {
    local workdir="$1"
    local file="$2"
    MAGIC_DIR="$ORACLE_ROOT/.pixi/envs/default" \
        oracle_capture "$workdir" mojo "$file"
}

oracle_contains_any() {
    local hay="$1"
    shift
    local needle
    for needle in "$@"; do
        if [[ "$hay" == *"$needle"* ]]; then
            return 0
        fi
    done
    return 1
}

oracle_grade() {
    local name="$1"
    local got="$2"
    local expected="$3"
    shift 3
    echo -n "Grading ${name}... "
    if [[ -z "$got" ]]; then
        echo "❌ FAIL"
        echo "   Expected: ${expected}"
        echo "   Got:      <empty — command failed or printed nothing>"
        ORACLE_FAIL=$((ORACLE_FAIL + 1))
        return 1
    fi
    if oracle_contains_any "$got" "$@"; then
        echo "✅ PASS"
        ORACLE_PASS=$((ORACLE_PASS + 1))
        return 0
    fi
    echo "❌ FAIL"
    echo "   Expected: ${expected}"
    echo "   Got:      ${got}"
    ORACLE_FAIL=$((ORACLE_FAIL + 1))
    return 1
}

oracle_skip() {
    local name="$1"
    local why="$2"
    echo "Grading ${name}... ⏭️ SKIP (${why})"
    ORACLE_SKIP=$((ORACLE_SKIP + 1))
}

oracle_has_mlx() {
    oracle_capture . python -c "import mlx" >/dev/null 2>&1
}

oracle_mlx_or_skip() {
    local name="$1"
    local workdir="$2"
    local script="$3"
    shift 3
    if [[ "$(uname -s)" == "Linux" ]]; then
        oracle_skip "$name" "MLX is Apple Silicon only"
        return 0
    fi
    if ! oracle_has_mlx; then
        oracle_skip "$name" "mlx not importable in this Pixi env"
        return 0
    fi
    local got
    got="$(oracle_capture "$workdir" python "$script" || true)"
    oracle_grade "$name" "$got" "$@"
}

oracle_summary() {
    local trophy="$1"
    local keep_trying="$2"
    echo "--------------------------------------------------"
    echo "Result: ${ORACLE_PASS} pass, ${ORACLE_FAIL} fail, ${ORACLE_SKIP} skip"
    if [[ "$ORACLE_FAIL" -eq 0 && "$ORACLE_PASS" -gt 0 ]]; then
        echo "🏆 ${trophy}"
        return 0
    fi
    echo "⚠️ ${keep_trying}"
    return 1
}

# Optional: GRADE_PILLAR=jax|mlx|max|mojo grades one exercise and exits.
oracle_wants() {
    local pillar="$1"
    if [[ -z "${GRADE_PILLAR:-}" ]]; then
        return 0
    fi
    [[ "$GRADE_PILLAR" == "$pillar" ]]
}
