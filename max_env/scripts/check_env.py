"""Print the curriculum toolchain. Fail if pins are wrong."""

from __future__ import annotations

import sys


def main() -> int:
    print("python", sys.version.split()[0])
    if not sys.version.startswith("3.13"):
        print("expected Python 3.13.x for MLX wheels")
        return 1

    import mlx.core as mx

    print("mlx", mx.__name__, mx.array([1, 2, 3]))

    from max import engine, graph

    print("max.engine", engine.__name__)
    print("max.graph", graph.__name__)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
