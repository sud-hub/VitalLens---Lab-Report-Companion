"""Simple script to run tests and capture output"""
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "pytest", "-v", "--tb=short"],
    capture_output=True,
    text=True
)

print(result.stdout)
print(result.stderr)
sys.exit(result.returncode)
