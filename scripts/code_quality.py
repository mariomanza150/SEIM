#!/usr/bin/env python3
"""
SEIM Code Quality Analysis Script

This script provides comprehensive code quality analysis for the SEIM project,
including formatting, linting, type checking, security analysis, and complexity metrics.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


class CodeQualityAnalyzer:
    """Comprehensive code quality analysis for SEIM project."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.results = {
            "formatting": {"status": "unknown", "issues": []},
            "linting": {"status": "unknown", "issues": []},
            "type_checking": {"status": "unknown", "issues": []},
            "security": {"status": "unknown", "issues": []},
            "complexity": {"status": "unknown", "metrics": {}},
        }

    def run_command(
        self, command: list[str], capture_output: bool = True
    ) -> tuple[int, str, str]:
        """Run a shell command and return exit code, stdout, and stderr."""
        try:
            result = subprocess.run(
                command,
                capture_output=capture_output,
                text=True,
                cwd=self.project_root,
                timeout=300,  # 5 minute timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", f"Command timed out: {' '.join(command)}"
        except Exception as e:
            return 1, "", str(e)

    def check_formatting(self) -> bool:
        """Check code formatting with Black and isort."""
        print("🔍 Checking code formatting...")

        # Check Black formatting
        exit_code, stdout, stderr = self.run_command(["black", "--check", "."])
        if exit_code != 0:
            self.results["formatting"]["issues"].append(
                f"Black formatting issues: {stderr}"
            )

        # Check isort imports
        exit_code, stdout, stderr = self.run_command(["isort", "--check-only", "."])
        if exit_code != 0:
            self.results["formatting"]["issues"].append(
                f"Import sorting issues: {stderr}"
            )

        success = len(self.results["formatting"]["issues"]) == 0
        self.results["formatting"]["status"] = "pass" if success else "fail"
        return success

    def check_linting(self) -> bool:
        """Check code with flake8 and pylint."""
        print("🔍 Running linting checks...")

        # Check with flake8
        exit_code, stdout, stderr = self.run_command(
            ["flake8", ".", "--max-line-length=88", "--extend-ignore=E203,W503"]
        )
        if exit_code != 0:
            self.results["linting"]["issues"].append(f"Flake8 issues:\n{stdout}")

        # Check with pylint
        exit_code, stdout, stderr = self.run_command(
            ["pylint", "--rcfile=pyproject.toml", "."]
        )
        if exit_code != 0:
            self.results["linting"]["issues"].append(f"Pylint issues:\n{stdout}")

        success = len(self.results["linting"]["issues"]) == 0
        self.results["linting"]["status"] = "pass" if success else "fail"
        return success

    def check_types(self) -> bool:
        """Check type annotations with mypy."""
        print("🔍 Running type checking...")

        exit_code, stdout, stderr = self.run_command(
            ["mypy", ".", "--ignore-missing-imports"]
        )

        if exit_code != 0:
            self.results["type_checking"]["issues"].append(
                f"Type checking issues:\n{stdout}"
            )

        success = len(self.results["type_checking"]["issues"]) == 0
        self.results["type_checking"]["status"] = "pass" if success else "fail"
        return success

    def check_security(self) -> bool:
        """Check for security issues with bandit and safety."""
        print("🔒 Running security analysis...")

        # Check with bandit
        exit_code, stdout, stderr = self.run_command(
            ["bandit", "-r", ".", "-f", "json", "-o", "bandit-report.json"]
        )

        if exit_code != 0:
            self.results["security"]["issues"].append(
                f"Bandit security issues:\n{stderr}"
            )

        # Check with safety
        exit_code, stdout, stderr = self.run_command(["safety", "check"])
        if exit_code != 0:
            self.results["security"]["issues"].append(f"Safety issues:\n{stdout}")

        success = len(self.results["security"]["issues"]) == 0
        self.results["security"]["status"] = "pass" if success else "fail"
        return success

    def check_complexity(self) -> bool:
        """Analyze code complexity with radon."""
        print("📊 Analyzing code complexity...")

        # Check cyclomatic complexity
        exit_code, stdout, stderr = self.run_command(["radon", "cc", ".", "-a"])
        if exit_code == 0:
            self.results["complexity"]["metrics"]["cyclomatic"] = stdout
        else:
            self.results["complexity"]["issues"].append(
                f"Complexity analysis failed: {stderr}"
            )

        # Check maintainability index
        exit_code, stdout, stderr = self.run_command(["radon", "mi", ".", "-a"])
        if exit_code == 0:
            self.results["complexity"]["metrics"]["maintainability"] = stdout
        else:
            self.results["complexity"]["issues"].append(
                f"Maintainability analysis failed: {stderr}"
            )

        success = len(self.results["complexity"]["issues"]) == 0
        self.results["complexity"]["status"] = "pass" if success else "fail"
        return success

    def run_all_checks(self) -> dict:
        """Run all code quality checks."""
        print("🚀 Starting comprehensive code quality analysis...")
        print("=" * 60)

        checks = [
            ("Formatting", self.check_formatting),
            ("Linting", self.check_linting),
            ("Type Checking", self.check_types),
            ("Security", self.check_security),
            ("Complexity", self.check_complexity),
        ]

        all_passed = True
        for name, check_func in checks:
            print(f"\n📋 {name} Check:")
            print("-" * 40)
            try:
                if check_func():
                    print(f"✅ {name} check passed")
                else:
                    print(f"❌ {name} check failed")
                    all_passed = False
            except Exception as e:
                print(f"❌ {name} check error: {e}")
                all_passed = False

        print("\n" + "=" * 60)
        print("📊 Code Quality Analysis Summary:")
        print("=" * 60)

        for category, result in self.results.items():
            status_icon = "✅" if result["status"] == "pass" else "❌"
            print(f"{status_icon} {category.title()}: {result['status']}")
            if result.get("issues"):
                for issue in result["issues"]:
                    print(f"   • {issue[:100]}...")

        return {
            "overall_status": "pass" if all_passed else "fail",
            "results": self.results,
        }

    def generate_report(self, output_file: Path | None = None) -> None:
        """Generate a detailed code quality report."""
        if output_file is None:
            output_file = self.project_root / "code-quality-report.json"

        with open(output_file, "w") as f:
            json.dump(self.results, f, indent=2)

        print(f"\n📄 Detailed report saved to: {output_file}")


def main():
    """Main entry point for the code quality analysis script."""
    parser = argparse.ArgumentParser(description="SEIM Code Quality Analysis")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root directory (default: current directory)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file for detailed report (default: code-quality-report.json)",
    )
    parser.add_argument(
        "--check",
        choices=["formatting", "linting", "types", "security", "complexity", "all"],
        default="all",
        help="Specific check to run (default: all)",
    )

    args = parser.parse_args()

    if not args.project_root.exists():
        print(f"❌ Project root directory does not exist: {args.project_root}")
        sys.exit(1)

    analyzer = CodeQualityAnalyzer(args.project_root)

    if args.check == "all":
        result = analyzer.run_all_checks()
        analyzer.generate_report(args.output)
        sys.exit(0 if result["overall_status"] == "pass" else 1)
    else:
        check_map = {
            "formatting": analyzer.check_formatting,
            "linting": analyzer.check_linting,
            "types": analyzer.check_types,
            "security": analyzer.check_security,
            "complexity": analyzer.check_complexity,
        }

        check_func = check_map.get(args.check)
        if check_func:
            success = check_func()
            sys.exit(0 if success else 1)
        else:
            print(f"❌ Unknown check: {args.check}")
            sys.exit(1)


if __name__ == "__main__":
    main()
