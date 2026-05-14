"""Tests for src.orchestrator.registry.

Covers the contract invariants from .claude/rules/multi-strategy.md and the
workflow from .claude/skills/strategy-register/SKILL.md.
"""

from __future__ import annotations

import multiprocessing
import subprocess
import sys
import threading
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from src.orchestrator.registry import (
    DEFAULT_MAGIC_RANGE_END,
    DEFAULT_MAGIC_RANGE_START,
    STRATEGY_ID_RE,
    ExitCode,
    InvariantViolationError,
    LockContentionError,
    PositionMode,
    RegistryDefaults,
    RegistryDocument,
    Runtime,
    SchemaVersionMismatchError,
    StrategyEntry,
    StrategyState,
    allocate_magic_number,
    allowed_transition,
    atomic_replace,
    canonicalize_symbol,
    compose_strategy_id,
    dump_registry,
    load_registry,
    locked_registry_file,
    main,
    validate_registry_relative_path,
    validate_strategy_id,
)

# ---------------------------------------------------------------------------
# strategy_id regex / canonicalization
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "sid",
    [
        "binance.swap.mean-revert.btcusdt.5m.v1",
        "oanda.fx.ma-cross.usdjpy.1h.v2",
        "ibkr.cash.pairs.spy-iwm.1d.v1",
        "tse.cash.breakout.7203t.4h.v1",
    ],
)
def test_strategy_id_regex_accepts_contract_examples(sid: str) -> None:
    assert STRATEGY_ID_RE.match(sid) is not None
    assert validate_strategy_id(sid)


@pytest.mark.parametrize(
    "sid",
    [
        "Binance.swap.mean-revert.btcusdt.5m.v1",  # uppercase
        "binance.swap.mean-revert.btcusdt.5m",  # missing major
        "binance.swap.mean-revert.btcusdt.v1",  # missing timeframe
        "binance..mean-revert.btcusdt.5m.v1",  # empty market
        "binance.swap.mean-revert.btcusdt.5z.v1",  # bad timeframe unit
        "binance.swap.mean-revert.btcusdt.5m.v0",  # major 0
        "",
    ],
)
def test_strategy_id_regex_rejects_invalid(sid: str) -> None:
    assert not validate_strategy_id(sid)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("BTC/USDT", "btcusdt"),
        ("7203.T", "7203t"),
        ("EUR-USD", "eurusd"),
        ("usd_jpy", "usdjpy"),
        ("SPY", "spy"),
    ],
)
def test_canonicalize_symbol(raw: str, expected: str) -> None:
    assert canonicalize_symbol(raw) == expected


def test_compose_strategy_id() -> None:
    sid = compose_strategy_id("binance", "swap", "mean-revert", "btcusdt", "5m", 1)
    assert sid == "binance.swap.mean-revert.btcusdt.5m.v1"
    assert validate_strategy_id(sid)


# ---------------------------------------------------------------------------
# MagicNumber allocation
# ---------------------------------------------------------------------------


def test_allocate_magic_deterministic() -> None:
    a = allocate_magic_number("binance.swap.x.btcusdt.5m.v1", set())
    b = allocate_magic_number("binance.swap.x.btcusdt.5m.v1", set())
    assert a == b
    assert DEFAULT_MAGIC_RANGE_START <= a[0] <= DEFAULT_MAGIC_RANGE_END
    assert a[1] == 0


def test_allocate_magic_collision_increments_salt() -> None:
    first, _ = allocate_magic_number("binance.swap.x.btcusdt.5m.v1", set())
    # Pre-fill `existing` with the first candidate, forcing salt=1.
    second, salt = allocate_magic_number(
        "binance.swap.x.btcusdt.5m.v1", {first}
    )
    assert second != first
    assert salt == 1


def test_allocate_magic_bounded_loop_raises() -> None:
    # Tiny range_size + filled existing set forces exhaustion fast.
    existing = set(range(100, 110))
    with pytest.raises(InvariantViolationError):
        allocate_magic_number(
            "binance.swap.x.btcusdt.5m.v1",
            existing,
            range_start=100,
            range_size=10,
            max_attempts=20,
        )


# ---------------------------------------------------------------------------
# Path validation
# ---------------------------------------------------------------------------


def test_validate_path_rejects_absolute(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="absolute"):
        validate_registry_relative_path(tmp_path, "/etc/passwd", "config/strategies")


def test_validate_path_rejects_parent_traversal(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="parent-traversal"):
        validate_registry_relative_path(
            tmp_path, "../../sensitive", "config/strategies"
        )


def test_validate_path_rejects_outside_prefix(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="prefix"):
        validate_registry_relative_path(
            tmp_path, "logs/strategies/foo", "config/strategies"
        )


def test_validate_path_rejects_empty(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="empty"):
        validate_registry_relative_path(tmp_path, "", "config/strategies")


def test_validate_path_accepts_valid(tmp_path: Path) -> None:
    result = validate_registry_relative_path(
        tmp_path, "config/strategies/binance.swap.mean-revert.btcusdt.5m.v1.toml",
        "config/strategies",
    )
    assert result.is_absolute()
    assert str(result).startswith(str(tmp_path.resolve()))


# ---------------------------------------------------------------------------
# Lifecycle transitions
# ---------------------------------------------------------------------------


def test_allowed_transition_matrix() -> None:
    allowed_pairs = {
        (StrategyState.DRAFT, StrategyState.TESTNET),
        (StrategyState.DRAFT, StrategyState.DEPRECATED),
        (StrategyState.TESTNET, StrategyState.LIVE),
        (StrategyState.TESTNET, StrategyState.DEPRECATED),
        (StrategyState.LIVE, StrategyState.DEPRECATED),
        (StrategyState.DEPRECATED, StrategyState.RETIRED),
    }
    for current in StrategyState:
        for target in StrategyState:
            expected = (current, target) in allowed_pairs
            assert allowed_transition(current, target) is expected, (current, target)


# ---------------------------------------------------------------------------
# TOML round-trip
# ---------------------------------------------------------------------------


def _make_entry(sid: str = "binance.swap.mr.btcusdt.5m.v1") -> StrategyEntry:
    now = datetime.now(UTC).replace(microsecond=0)
    return StrategyEntry(
        id=sid,
        family_id="mr",
        logic_version="1.0.0",
        runtime=Runtime.PYTHON,
        venue="binance",
        market="swap",
        symbol="BTCUSDT",
        timeframe="5m",
        account_scope="binance-main",
        risk_group="crypto-main",
        state=StrategyState.DRAFT,
        enabled=False,
        config_path=f"config/strategies/{sid}.toml",
        state_path=f"state/strategies/{sid}",
        log_path=f"logs/strategies/{sid}",
        db_path=f"state/strategies/{sid}/state.db",
        magic_number=0,
        magic_salt=0,
        created_at=now,
        updated_at=now,
    )


def test_registry_round_trip(tmp_path: Path) -> None:
    doc = RegistryDocument(
        schema_version=1,
        defaults=RegistryDefaults(),
        accounts=[],
        strategies=[_make_entry()],
    )
    path = tmp_path / "registry.toml"
    atomic_replace(path, dump_registry(doc))
    loaded = load_registry(path)
    assert loaded.schema_version == 1
    assert len(loaded.strategies) == 1
    assert loaded.strategies[0].id == "binance.swap.mr.btcusdt.5m.v1"


def test_registry_sorted_by_id(tmp_path: Path) -> None:
    doc = RegistryDocument(
        schema_version=1,
        defaults=RegistryDefaults(),
        accounts=[],
        strategies=[
            _make_entry("zzz.spot.x.eth.1h.v1"),
            _make_entry("aaa.spot.x.btc.1h.v1"),
            _make_entry("mmm.spot.x.sol.1h.v1"),
        ],
    )
    payload = dump_registry(doc).decode()
    # Order of id lines must be aaa, mmm, zzz
    idx_a = payload.index("aaa.spot.x.btc.1h.v1")
    idx_m = payload.index("mmm.spot.x.sol.1h.v1")
    idx_z = payload.index("zzz.spot.x.eth.1h.v1")
    assert idx_a < idx_m < idx_z


def test_load_registry_rejects_unknown_schema_version(tmp_path: Path) -> None:
    path = tmp_path / "registry.toml"
    path.write_text("schema_version = 99\n")
    with pytest.raises(SchemaVersionMismatchError):
        load_registry(path)


# ---------------------------------------------------------------------------
# Locking
# ---------------------------------------------------------------------------


def _hold_lock_briefly(path_str: str, hold_s: float, ready_path: str) -> None:
    """Helper for the lock-contention test: hold the registry lock for hold_s."""
    from src.orchestrator.registry import (  # local import for subprocess context
        locked_registry_file as _lock,
    )

    p = Path(path_str)
    p.parent.mkdir(parents=True, exist_ok=True)
    with _lock(p):
        Path(ready_path).touch()
        time.sleep(hold_s)


def test_lock_contention_times_out_quickly(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Shrink the timeout so the test runs fast.
    monkeypatch.setattr("src.orchestrator.registry.LOCK_TIMEOUT_S", 0.5)
    registry_path = tmp_path / "registry.toml"
    ready_path = tmp_path / ".ready"

    thread = threading.Thread(
        target=_hold_lock_briefly, args=(str(registry_path), 2.0, str(ready_path)),
    )
    thread.start()
    try:
        # Wait for the helper to hold the lock.
        for _ in range(50):
            if ready_path.exists():
                break
            time.sleep(0.05)
        with pytest.raises(LockContentionError), locked_registry_file(registry_path):
            pass
    finally:
        thread.join()


# ---------------------------------------------------------------------------
# CLI smoke tests via subprocess
# ---------------------------------------------------------------------------


def _run_cli(project_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "src.orchestrator.registry",
            "--project-root",
            str(project_root),
            *args,
        ],
        check=False,
        capture_output=True,
        text=True,
        env={"PYTHONPATH": str(Path(__file__).resolve().parents[2]), "PATH": ""},
    )


def test_cli_register_show_transition_audit(tmp_path: Path) -> None:
    out = _run_cli(
        tmp_path,
        "register",
        "--venue", "binance",
        "--market", "swap",
        "--logic-slug", "mean-revert",
        "--symbol", "BTCUSDT",
        "--timeframe", "5m",
        "--runtime", "python",
        "--account-scope", "binance-main",
        "--risk-group", "crypto-main",
    )
    assert out.returncode == ExitCode.OK, out.stderr
    assert "registered" in out.stdout

    out = _run_cli(tmp_path, "list")
    assert out.returncode == ExitCode.OK
    assert "binance.swap.mean-revert.btcusdt.5m.v1" in out.stdout

    out = _run_cli(
        tmp_path,
        "transition",
        "binance.swap.mean-revert.btcusdt.5m.v1",
        "testnet",
    )
    assert out.returncode == ExitCode.OK

    out = _run_cli(tmp_path, "audit")
    assert out.returncode == ExitCode.OK


def test_cli_rejects_duplicate(tmp_path: Path) -> None:
    common = (
        "register",
        "--venue", "binance",
        "--market", "swap",
        "--logic-slug", "mr",
        "--symbol", "BTCUSDT",
        "--timeframe", "5m",
        "--runtime", "python",
        "--account-scope", "binance-main",
        "--risk-group", "crypto-main",
    )
    out = _run_cli(tmp_path, *common)
    assert out.returncode == ExitCode.OK
    out = _run_cli(tmp_path, *common)
    assert out.returncode == ExitCode.USER_ERROR
    assert "already registered" in out.stderr


def test_cli_bad_transition(tmp_path: Path) -> None:
    _run_cli(
        tmp_path,
        "register",
        "--venue", "binance",
        "--market", "swap",
        "--logic-slug", "mr",
        "--symbol", "BTCUSDT",
        "--timeframe", "5m",
        "--runtime", "python",
        "--account-scope", "binance-main",
        "--risk-group", "crypto-main",
    )
    # draft -> live is forbidden (must go via testnet)
    out = _run_cli(tmp_path, "transition", "binance.swap.mr.btcusdt.5m.v1", "live")
    assert out.returncode == ExitCode.USER_ERROR
    assert "forbidden transition" in out.stderr


def test_cli_audit_detects_invariant_violation(tmp_path: Path) -> None:
    # Register, then hand-edit the registry to violate magic-uniqueness.
    _run_cli(
        tmp_path,
        "register",
        "--venue", "oanda",
        "--market", "fx",
        "--logic-slug", "ma-cross",
        "--symbol", "USDJPY",
        "--timeframe", "1h",
        "--runtime", "mql5",
        "--account-scope", "broker",
        "--risk-group", "fx",
    )
    _run_cli(
        tmp_path,
        "register",
        "--venue", "oanda",
        "--market", "fx",
        "--logic-slug", "ma-cross",
        "--symbol", "EURUSD",
        "--timeframe", "1h",
        "--runtime", "mql5",
        "--account-scope", "broker",
        "--risk-group", "fx",
    )
    # Now corrupt the second entry to collide on magic_number.
    reg = tmp_path / "config" / "registry.toml"
    doc = load_registry(reg)
    first_magic = doc.strategies[0].magic_number
    doc.strategies[1].magic_number = first_magic
    atomic_replace(reg, dump_registry(doc))

    out = _run_cli(tmp_path, "audit")
    assert out.returncode == ExitCode.INVARIANT_VIOLATION
    assert "duplicate magic_number" in out.stdout


# ---------------------------------------------------------------------------
# Concurrent registration via multiprocessing
# ---------------------------------------------------------------------------


def _spawn_register(
    project_root: str, symbol: str, queue: multiprocessing.Queue[int]
) -> None:
    rc = main(
        [
            "--project-root", project_root,
            "register",
            "--venue", "binance",
            "--market", "swap",
            "--logic-slug", "mr",
            "--symbol", symbol,
            "--timeframe", "1h",
            "--runtime", "mql5",
            "--account-scope", "binance-mql5",
            "--risk-group", "crypto",
        ]
    )
    queue.put(rc)


def test_concurrent_register_no_double_magic(tmp_path: Path) -> None:
    queue: multiprocessing.Queue[int] = multiprocessing.Queue()
    procs = [
        multiprocessing.Process(
            target=_spawn_register, args=(str(tmp_path), sym, queue)
        )
        for sym in ("BTCUSDT", "ETHUSDT", "SOLUSDT")
    ]
    for p in procs:
        p.start()
    for p in procs:
        p.join(timeout=30)
        assert p.exitcode == 0
    results = sorted(queue.get() for _ in procs)
    assert all(rc == ExitCode.OK for rc in results)
    reg = tmp_path / "config" / "registry.toml"
    doc = load_registry(reg)
    assert len(doc.strategies) == 3
    magics = [e.magic_number for e in doc.strategies]
    assert len(magics) == len(set(magics)), f"duplicate magics: {magics}"


# ---------------------------------------------------------------------------
# Netting account shared-symbol refusal
# ---------------------------------------------------------------------------


def test_netting_shared_symbol_refused(tmp_path: Path) -> None:
    # Pre-populate registry with an [[accounts]] block declaring netting.
    reg = tmp_path / "config" / "registry.toml"
    reg.parent.mkdir(parents=True, exist_ok=True)
    reg.write_text(
        "schema_version = 1\n\n"
        "[defaults]\n"
        'state_dir = "state/strategies"\n'
        'log_dir = "logs/strategies"\n'
        'config_dir = "config/strategies"\n'
        f"magic_range_start = {DEFAULT_MAGIC_RANGE_START}\n"
        f"magic_range_end = {DEFAULT_MAGIC_RANGE_END}\n\n"
        "[[accounts]]\n"
        'name = "broker-prop-netting"\n'
        'position_mode = "netting"\n'
        'notes = ""\n'
    )
    common = (
        "register",
        "--venue", "oanda",
        "--market", "fx",
        "--logic-slug", "ma-cross",
        "--symbol", "USDJPY",
        "--timeframe", "1h",
        "--runtime", "mql5",
        "--account-scope", "broker-prop-netting",
        "--risk-group", "fx",
    )
    out = _run_cli(tmp_path, *common)
    assert out.returncode == ExitCode.OK
    # Second registration on same venue+symbol+account must be refused.
    out2 = _run_cli(tmp_path, *common, "--logic-slug", "rsi-bands")
    assert out2.returncode == ExitCode.USER_ERROR
    assert "netting" in out2.stderr.lower()


# ---------------------------------------------------------------------------
# Audit --fix re-creates missing dirs
# ---------------------------------------------------------------------------


def test_audit_fix_recreates_missing_dirs(tmp_path: Path) -> None:
    _run_cli(
        tmp_path,
        "register",
        "--venue", "binance",
        "--market", "swap",
        "--logic-slug", "mr",
        "--symbol", "BTCUSDT",
        "--timeframe", "5m",
        "--runtime", "python",
        "--account-scope", "binance-main",
        "--risk-group", "crypto-main",
    )
    state_dir = tmp_path / "state" / "strategies" / "binance.swap.mr.btcusdt.5m.v1"
    assert state_dir.exists()
    # Wipe it.
    import shutil

    shutil.rmtree(state_dir)
    out = _run_cli(tmp_path, "audit")
    assert out.returncode == ExitCode.INVARIANT_VIOLATION
    out = _run_cli(tmp_path, "audit", "--fix")
    assert out.returncode == ExitCode.OK
    assert state_dir.exists()


# ---------------------------------------------------------------------------
# Updated_at >= created_at invariant
# ---------------------------------------------------------------------------


def test_audit_detects_timestamp_inversion(tmp_path: Path) -> None:
    _run_cli(
        tmp_path,
        "register",
        "--venue", "binance",
        "--market", "swap",
        "--logic-slug", "mr",
        "--symbol", "BTCUSDT",
        "--timeframe", "5m",
        "--runtime", "python",
        "--account-scope", "binance-main",
        "--risk-group", "crypto-main",
    )
    reg = tmp_path / "config" / "registry.toml"
    doc = load_registry(reg)
    doc.strategies[0].updated_at = doc.strategies[0].created_at - timedelta(days=1)
    atomic_replace(reg, dump_registry(doc))
    out = _run_cli(tmp_path, "audit")
    assert out.returncode == ExitCode.INVARIANT_VIOLATION
    assert "updated_at before created_at" in out.stdout


# ---------------------------------------------------------------------------
# Enum integrity (defensive)
# ---------------------------------------------------------------------------


def test_position_mode_values() -> None:
    assert PositionMode.NETTING.value == "netting"
    assert PositionMode.HEDGING.value == "hedging"
