#!/bin/bash
"""
Strategic Git Hooks Setup Script

Sets up comprehensive git hooks for strategic data protection and code quality.
This ensures all commits meet security and quality standards before reaching GitHub.
"""

set -e

echo "🔧 Setting up Strategic Integration Service Git Hooks"
echo "=" * 60

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Virtual environment not detected. Attempting to activate..."
    if [[ -f "venv/bin/activate" ]]; then
        source venv/bin/activate
        echo "✅ Virtual environment activated"
    else
        echo "❌ Error: Please activate your virtual environment first"
        echo "Run: source venv/bin/activate (or venv/bin/activate.fish for fish shell)"
        exit 1
    fi
fi

# Install pre-commit if not already installed
echo "📦 Installing pre-commit dependencies..."
pip install pre-commit bandit detect-secrets

# Install pre-commit hooks
echo "🔗 Installing pre-commit hooks..."
pre-commit install

# Update hook repositories
echo "🔄 Updating pre-commit hook repositories..."
pre-commit autoupdate

# Run initial check on all files
echo "🧪 Running initial hook validation..."
if pre-commit run --all-files; then
    echo "✅ All hooks passed initial validation"
else
    echo "⚠️  Some hooks failed initial validation - this is normal for first run"
    echo "Files have been automatically formatted. Please review changes."
fi

# Initialize secrets baseline
echo "🔐 Initializing secrets detection baseline..."
if [[ ! -f ".secrets.baseline" ]]; then
    detect-secrets scan --baseline .secrets.baseline
    echo "✅ Secrets baseline created"
else
    echo "✅ Secrets baseline already exists"
fi

# Create git hooks documentation
cat > GIT_HOOKS_README.md << 'EOF'
# Strategic Integration Service - Git Hooks

## Overview

This repository uses comprehensive git hooks to ensure:
- 🔐 **Security**: PII detection and secret scanning
- 🧪 **Quality**: Automated testing and code quality checks
- 📋 **Compliance**: Strategic data validation
- 🎨 **Standards**: Code formatting and linting

## Hooks Configured

### Pre-commit Hooks

1. **Code Quality**
   - Black code formatting
   - isort import sorting
   - Flake8 linting
   - MyPy type checking
   - Trailing whitespace removal

2. **Security Scanning**
   - Bandit vulnerability detection
   - detect-secrets for API tokens/keys
   - Custom PII scanner for strategic data

3. **Strategic Data Protection**
   - PII pattern detection
   - Strategic data validation
   - Executive report structure checks
   - JSON/YAML validation

4. **Testing**
   - Unit test execution
   - Code coverage validation
   - Integration tests (when credentials available)
   - Git status verification

## Usage

### Normal Development
```bash
# Hooks run automatically on commit
git add .
git commit -m "Your commit message"
# Hooks will run and either allow or block the commit
```

### Manual Hook Execution
```bash
# Run all hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run pii-scanner
pre-commit run test-runner

# Run hooks on specific files
pre-commit run --files file1.py file2.py
```

### Bypassing Hooks (Emergency Only)
```bash
# Skip all hooks (use sparingly!)
git commit --no-verify -m "Emergency commit"

# Skip specific checks by fixing issues first
```

## Hook Behavior

### Commit Blocking (High Severity)
- High-severity PII violations (API tokens, emails, etc.)
- Critical security vulnerabilities
- Unit test failures
- Syntax errors in JSON/YAML

### Commit Allowed with Warnings (Medium/Low Severity)
- Code formatting issues (auto-fixed)
- Medium-severity PII (phone numbers, internal URLs)
- Documentation structure issues
- Integration test failures (if credentials unavailable)

## Troubleshooting

### Common Issues

1. **Hook Installation Failed**
   ```bash
   # Reinstall hooks
   pre-commit uninstall
   ./setup_git_hooks.sh
   ```

2. **PII False Positives**
   - Update `.secrets.baseline` for detect-secrets
   - Modify PII patterns in `strategic_integration_service/hooks/pii_scanner.py`

3. **Test Failures**
   ```bash
   # Run tests manually to debug
   python -m pytest tests/unit/ -v
   ```

4. **Security Scan Issues**
   ```bash
   # Run security scan manually
   bandit -r strategic_integration_service/
   ```

## Configuration Files

- `.pre-commit-config.yaml` - Hook configuration
- `.secrets.baseline` - Known secrets baseline
- `strategic_integration_service/hooks/` - Custom hook scripts

## Support

For issues with git hooks:
1. Check this documentation
2. Run hooks manually to debug
3. Contact the platform team
4. Review hook logs in `/tmp/` or `~/.cache/pre-commit/`

## Security Note

These hooks protect strategic leadership data. Never bypass security hooks without approval from the security team.
EOF

echo "📚 Git hooks documentation created: GIT_HOOKS_README.md"

echo ""
echo "🎉 Strategic Git Hooks Setup Complete!"
echo ""
echo "✅ Pre-commit hooks installed and configured"
echo "✅ Security scanning enabled"
echo "✅ Strategic data protection active"
echo "✅ Code quality enforcement enabled"
echo ""
echo "📋 Next Steps:"
echo "1. Review GIT_HOOKS_README.md for usage instructions"
echo "2. Test with: git add . && git commit -m 'Test commit'"
echo "3. Hooks will now run automatically on every commit"
echo ""
echo "🛡️  Your strategic data is now protected!"
