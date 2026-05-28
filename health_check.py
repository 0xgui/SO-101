#!/usr/bin/env python3
"""Check local SO-101 repo prerequisites without touching robot hardware."""

from __future__ import annotations

import argparse
import glob
import grp
import json
import os
import platform
import pwd
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent
LEROBOT_ROOT = Path("/home/gs/projects/github/lerobot")
EXPECTED_CONDA_ENV = "lerobot"
EXPECTED_ROBOT_IDS = {
    "follower": "purple_bot",
    "leader": "yellow_bot",
}
LEROBOT_COMMANDS = (
    "lerobot-find-port",
    "lerobot-setup-motors",
    "lerobot-calibrate",
    "lerobot-teleoperate",
    "lerobot-record",
    "lerobot-train",
)


@dataclass
class Check:
    name: str
    status: str
    detail: str
    fix: str = ""


def ok(name: str, detail: str) -> Check:
    return Check(name, "OK", detail)


def warn(name: str, detail: str, fix: str = "") -> Check:
    return Check(name, "WARN", detail, fix)


def fail(name: str, detail: str, fix: str = "") -> Check:
    return Check(name, "FAIL", detail, fix)


def command_output(command: list[str], timeout: float = 5.0) -> tuple[int, str]:
    try:
        result = subprocess.run(
            command,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return 127, str(exc)
    return result.returncode, result.stdout.strip()


def command_version(command: str, args: list[str] | None = None) -> str:
    args = args or ["--version"]
    code, output = command_output([command, *args], timeout=3.0)
    if code != 0 or not output:
        return "found"
    return output.splitlines()[0]


def current_groups() -> set[str]:
    groups: set[str] = set()
    try:
        groups.add(grp.getgrgid(os.getgid()).gr_name)
    except KeyError:
        pass
    for group_id in os.getgroups():
        try:
            groups.add(grp.getgrgid(group_id).gr_name)
        except KeyError:
            continue
    return groups


def mode_string(path: Path) -> str:
    mode = path.stat().st_mode & 0o777
    return oct(mode)


def find_serial_ports() -> list[Path]:
    ports = [
        Path(port)
        for pattern in ("/dev/ttyACM*", "/dev/ttyUSB*")
        for port in glob.glob(pattern)
    ]
    return sorted(ports, key=lambda item: item.name)


def parse_platformio_ports() -> dict[str, str]:
    ini = REPO_ROOT / "face_display" / "platformio.ini"
    if not ini.exists():
        return {}

    ports: dict[str, str] = {}
    for line in ini.read_text(encoding="utf-8").splitlines():
        match = re.match(r"\s*(upload_port|monitor_port)\s*=\s*(\S+)", line)
        if match:
            ports[match.group(1)] = match.group(2)
    return ports


def likely_calibration_paths(robot_id: str, max_seen: int = 15000) -> list[Path]:
    roots = [
        Path.home() / ".cache" / "huggingface" / "lerobot",
        Path.home() / ".cache" / "lerobot",
    ]
    matches: list[Path] = []
    seen = 0
    for root in roots:
        if not root.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [name for name in dirnames if not name.startswith(".")]
            for name in filenames:
                seen += 1
                if robot_id in name:
                    matches.append(Path(dirpath) / name)
                    if len(matches) >= 5:
                        return matches
                if seen >= max_seen:
                    return matches
    return matches


def check_python() -> Check:
    version = platform.python_version()
    if sys.version_info >= (3, 10):
        return ok("Python", f"{version} at {sys.executable}")
    return fail(
        "Python",
        f"{version} is too old",
        "Use Python 3.10+; LeRobot IL docs recommend Python 3.12.",
    )


def check_conda() -> Check:
    env = os.environ.get("CONDA_DEFAULT_ENV")
    if env == EXPECTED_CONDA_ENV:
        return ok("Conda env", f"active env is {env}")
    if env:
        return warn(
            "Conda env",
            f"active env is {env}, expected {EXPECTED_CONDA_ENV}",
            f"Run: conda activate {EXPECTED_CONDA_ENV}",
        )
    return warn("Conda env", "no active conda env detected", f"Run: conda activate {EXPECTED_CONDA_ENV}")


def check_lerobot_root() -> Check:
    if LEROBOT_ROOT.exists():
        return ok("LeRobot checkout", str(LEROBOT_ROOT))
    return fail("LeRobot checkout", f"missing {LEROBOT_ROOT}", "Clone/install LeRobot before running robot CLIs.")


def check_conda_binary() -> Check:
    path = shutil.which("conda")
    if path:
        version = command_version("conda", ["--version"])
        return ok("Conda", f"{version} ({path})")

    conda_exe = os.environ.get("CONDA_EXE")
    if conda_exe and Path(conda_exe).exists():
        return ok("Conda", f"available via CONDA_EXE={conda_exe}")

    return warn("Conda", "not found on PATH", "Install Conda before using the related workflow.")


def check_lerobot_cli() -> list[Check]:
    checks: list[Check] = []
    for command in LEROBOT_COMMANDS:
        path = shutil.which(command)
        if path:
            checks.append(ok(command, path))
        else:
            checks.append(
                fail(
                    command,
                    "not found on PATH",
                    f"Run: conda activate {EXPECTED_CONDA_ENV} && "
                    f"cd {LEROBOT_ROOT} && pip install -e \".[feetech,dataset,train]\"",
                )
            )
    return checks


def check_serial() -> list[Check]:
    checks: list[Check] = []
    ports = find_serial_ports()
    groups = current_groups()
    user = pwd.getpwuid(os.getuid()).pw_name

    if "dialout" in groups:
        checks.append(ok("Dialout group", f"{user} is in dialout"))
    else:
        checks.append(
            warn(
                "Dialout group",
                f"{user} is not in dialout",
                "Permanent fix: sudo usermod -aG dialout $USER, then log out and back in.",
            )
        )

    if not ports:
        checks.append(
            warn(
                "Serial ports",
                "no /dev/ttyACM* or /dev/ttyUSB* devices found",
                "Plug in an arm or face display, then run ./find_port.sh.",
            )
        )
        return checks

    port_details = []
    inaccessible = []
    for port in ports:
        readable = os.access(port, os.R_OK)
        writable = os.access(port, os.W_OK)
        access = (
            "rw"
            if readable and writable
            else "read-only"
            if readable
            else "write-only"
            if writable
            else "no-access"
        )
        port_details.append(f"{port} ({access}, {mode_string(port)})")
        if not (readable and writable):
            inaccessible.append(str(port))

    if inaccessible:
        checks.append(
            fail(
                "Serial ports",
                "; ".join(port_details),
                "Temporary fix: sudo chmod 666 /dev/ttyACM0, replacing the port as needed.",
            )
        )
    else:
        checks.append(ok("Serial ports", "; ".join(port_details)))
    return checks


def check_platformio_config() -> list[Check]:
    checks: list[Check] = []
    ini = REPO_ROOT / "face_display" / "platformio.ini"
    if not ini.exists():
        return [warn("PlatformIO config", "face_display/platformio.ini is missing")]

    configured_ports = parse_platformio_ports()
    if not configured_ports:
        checks.append(
            warn(
                "Face display ports",
                "upload_port/monitor_port not set",
                "Run ./find_port.sh and update face_display/platformio.ini.",
            )
        )
        return checks

    live_ports = {str(port) for port in find_serial_ports()}
    for key, value in configured_ports.items():
        if value in live_ports:
            checks.append(ok(f"Face {key}", f"{value} exists"))
        else:
            checks.append(
                warn(
                    f"Face {key}",
                    f"{value} is configured but not connected",
                    "Run ./find_port.sh before flashing or monitoring.",
                )
            )
    return checks


def check_tool(
    command: str,
    name: str | None = None,
    args: list[str] | None = None,
    required: bool = True,
) -> Check:
    label = name or command
    path = shutil.which(command)
    if path:
        version = command_version(command, args)
        return ok(label, f"{version} ({path})")
    builder = fail if required else warn
    return builder(
        label,
        "not found on PATH",
        f"Install {label} before using the related workflow.",
    )


def check_robot_ids() -> list[Check]:
    checks: list[Check] = []
    for role, robot_id in EXPECTED_ROBOT_IDS.items():
        matches = likely_calibration_paths(robot_id)
        if matches:
            display = ", ".join(str(path) for path in matches[:2])
            suffix = "" if len(matches) <= 2 else f" (+{len(matches) - 2} more)"
            checks.append(
                ok(
                    f"{role} id",
                    f"{robot_id} calibration/cache file found: {display}{suffix}",
                )
            )
        else:
            checks.append(
                warn(
                    f"{role} id",
                    f"{robot_id} has no obvious local calibration/cache file",
                    "Calibrate the arm after confirming the port: "
                    "lerobot-calibrate ... --robot.id=purple_bot "
                    "or --teleop.id=yellow_bot",
                )
            )
    return checks


def run_checks(include_cache_scan: bool) -> list[Check]:
    checks: list[Check] = [
        check_python(),
        check_conda(),
        check_lerobot_root(),
        check_conda_binary(),
        check_tool("openscad", "OpenSCAD", ["--version"]),
        check_tool("pio", "PlatformIO", ["--version"]),
    ]
    checks.extend(check_lerobot_cli())
    checks.extend(check_serial())
    checks.extend(check_platformio_config())
    if include_cache_scan:
        checks.extend(check_robot_ids())
    return checks


def print_table(checks: list[Check]) -> None:
    name_width = max(len(check.name) for check in checks)
    status_width = 4
    for check in checks:
        print(
            f"[{check.status:<{status_width}}] "
            f"{check.name:<{name_width}}  {check.detail}"
        )
        if check.fix:
            print(f"{'':{status_width + name_width + 5}}fix: {check.fix}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    parser.add_argument(
        "--skip-cache-scan",
        action="store_true",
        help="skip searching local LeRobot cache for purple_bot/yellow_bot calibration files",
    )
    args = parser.parse_args()

    checks = run_checks(include_cache_scan=not args.skip_cache_scan)

    if args.json:
        print(json.dumps([asdict(check) for check in checks], indent=2))
    else:
        print("SO-101 health check\n")
        print_table(checks)

    return 1 if any(check.status == "FAIL" for check in checks) else 0


if __name__ == "__main__":
    raise SystemExit(main())
