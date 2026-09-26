"""Local Laya runtime for the System 1 decision bus.

This is the published ``laya.Router`` API
(https://huggingface.co/convaiinnovations/laya), not a chat completion and
not the mock heuristic. ``Router.predict(state, questions)`` scores the same
``choice`` / ``score`` / ``noul`` schemas the tutor and retention gates use.

Import and weight failures raise ``LayaNotReady``. The bus turns that into a
mock answer. A missing package, a bad ``SYSTEM1_LAYA_PATH``, or a failed
checkpoint load is sticky for the process so a later request does not retry
a multi-hundred-megabyte download. A predict error after the router exists
is not sticky.

Unit tests inject ``sys.modules['laya']`` or patch ``open_router``. Neither
path downloads weights.
"""

from __future__ import annotations

import os

from ..config import (
    LAYA_BUNDLE_REPO,
    system1_laya_auto_task,
    system1_laya_device,
    system1_laya_max_len,
    system1_laya_max_loaded,
    system1_laya_model,
    system1_laya_path,
    system1_laya_preload,
    system1_laya_repo,
    system1_laya_revision,
    system1_laya_token,
)

# Same aliases ``laya.router.normalise_name`` accepts.
_ALIASES = {
    "en": "english",
    "laya": "english",
    "default": "english",
    "english": "english",
    "multi": "multilingual",
    "ml": "multilingual",
    "laya-multilingual": "multilingual",
    "multilingual": "multilingual",
    "typed": "typed-decisions",
    "typed_decisions": "typed-decisions",
    "laya-typed-decisions": "typed-decisions",
    "decisions": "typed-decisions",
    "typed-decisions": "typed-decisions",
}


class LayaNotReady(Exception):
    """Laya cannot answer. ``sticky`` remembers the failure for the process."""

    def __init__(self, reason: str, *, sticky: bool = True):
        super().__init__(reason)
        self.sticky = sticky


def canonical_checkpoint(raw: str, *, default: str | None) -> str | None:
    """Map a model env value onto ``english`` / ``multilingual`` / ``typed-decisions``."""
    text = (raw or "").strip().lower()
    if not text:
        return default
    name = _ALIASES.get(text)
    if name is None:
        raise LayaNotReady(
            f"laya model {raw.strip()!r} is not english, multilingual, or typed-decisions",
            sticky=True,
        )
    return name


def selected_checkpoint(*, force: bool) -> str | None:
    """The checkpoint this process will call, or None to let the Router choose."""
    return canonical_checkpoint(system1_laya_model(), default="english" if force else None)


def _pins_one_checkpoint() -> bool:
    return bool(system1_laya_model()) or bool(system1_laya_path()) or system1_laya_repo() != LAYA_BUNDLE_REPO


def ensure_configured() -> None:
    """Reject a missing local directory or an unknown checkpoint name. No import."""
    path = system1_laya_path()
    if path and not os.path.isdir(path):
        raise LayaNotReady(
            f"laya weights unavailable (SYSTEM1_LAYA_PATH is not a directory: {path})",
            sticky=True,
        )
    selected_checkpoint(force=False)


def router_kwargs() -> dict:
    """Keyword arguments for ``laya.Router``. Does not import the package."""
    ensure_configured()
    kwargs: dict = {}
    device = system1_laya_device()
    if device:
        kwargs["device"] = device
    token = system1_laya_token()
    if token:
        kwargs["token"] = token
    revision = system1_laya_revision()
    if revision:
        kwargs["revision"] = revision
    if system1_laya_auto_task():
        kwargs["auto_task_detection"] = True
    max_loaded = system1_laya_max_loaded()
    if max_loaded is None and system1_laya_path():
        # One local directory cannot satisfy a second checkpoint.
        max_loaded = 1
    if max_loaded is not None:
        kwargs["max_loaded"] = max_loaded
    path = system1_laya_path()
    repo = system1_laya_repo()
    if path or repo != LAYA_BUNDLE_REPO:
        checkpoint = selected_checkpoint(force=True)
        kwargs["models"] = {checkpoint: path or repo}
    return kwargs


def predict_kwargs() -> dict:
    """Keyword arguments for ``Router.predict`` beyond state and questions."""
    kwargs: dict = {}
    if _pins_one_checkpoint():
        kwargs["model"] = selected_checkpoint(force=True)
    max_len = system1_laya_max_len()
    if max_len is not None:
        kwargs["max_len"] = max_len
    return kwargs


def preload_targets() -> list[str] | None:
    """Checkpoints to build up front, or None to stay lazy.

    A named model, local path, or custom repo preloads only that checkpoint.
    Otherwise preload the pair automatic routing chooses between. Typed-decisions
    is included only when ``SYSTEM1_LAYA_AUTO_TASK`` is set or that checkpoint
    was named. ``Router(preload=True)`` would download all three (~1.16B).
    """
    if not system1_laya_preload():
        return None
    if _pins_one_checkpoint():
        names = [selected_checkpoint(force=True)]
    else:
        names = ["english", "multilingual"]
    if system1_laya_auto_task() and "typed-decisions" not in names:
        names.append("typed-decisions")
    return names


def open_router():
    """Construct a ``laya.Router``. Raises ``ImportError`` or ``LayaNotReady``.

    ``USE_TF=0`` is set when unset. TensorFlow's import probe can deadlock
    ``laya.load`` when TensorFlow is installed; the model card documents that.
    An explicit ``USE_TF`` is left alone.
    """
    ensure_configured()
    os.environ.setdefault("USE_TF", "0")
    from laya import Router

    router = Router(**router_kwargs())
    names = preload_targets()
    if names:
        router.preload(names)
    return router


def run_predict(router, state, questions):
    """One ``Router.predict`` call. The return value is Laya's result dict."""
    return router.predict(state, questions, **predict_kwargs())
