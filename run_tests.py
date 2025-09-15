#!/usr/bin/env python3
"""
Test runner script for the numeric converter application.

This script provides different test execution options:
- Run all tests
- Run specific test categories
- Run with different verbosity levels
- Generate coverage reports
"""

import os
import sys
import subprocess
import argparse


def run_command(cmd, description=""):
    """Run a command and return the result"""
    print(f"\n{'='*60}")
    if description:
        print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")

    result = subprocess.run(cmd, capture_output=False, text=True)
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="Run tests for the numeric converter")
    parser.add_argument(
        "--type",
        choices=["all", "unit", "integration", "edge", "api"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run with coverage reporting"
    )
    parser.add_argument(
        "--failfast", "-x",
        action="store_true",
        help="Stop on first failure"
    )

    args = parser.parse_args()

    # Base pytest command
    cmd = ["python", "-m", "pytest"]

    # Add test selection based on type
    if args.type == "unit":
        cmd.extend(["tests/test_conversions.py"])
    elif args.type == "integration":
        cmd.extend(["tests/test_api.py"])
    elif args.type == "edge":
        cmd.extend(["tests/test_edge_cases.py"])
    elif args.type == "api":
        cmd.extend(["tests/test_api.py", "tests/test_base64_little_endian.py"])
    else:  # all
        cmd.extend(["tests/"])

    # Add verbosity
    if args.verbose:
        cmd.append("-v")

    # Add fail fast
    if args.failfast:
        cmd.append("-x")

    # Add coverage if requested
    if args.coverage:
        print("Coverage reporting requested but pytest-cov not installed.")
        print("Install with: pip install pytest-cov")
        cmd.extend(["--cov=api", "--cov-report=html", "--cov-report=term"])

    # Run the tests
    success = run_command(cmd, f"Running {args.type} tests")

    if success:
        print(f"\n✅ All {args.type} tests passed!")
        return 0
    else:
        print(f"\n❌ Some {args.type} tests failed!")
        return 1


if __name__ == "__main__":
    exit(main())