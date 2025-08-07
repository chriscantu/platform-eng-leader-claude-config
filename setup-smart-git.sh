#!/bin/bash
"""
Setup Script for Intelligent Git Hooks

Creates aliases and shortcuts for optimized git workflow with the Strategic Integration Service.
"""

echo "🔧 Setting up intelligent git commit workflow..."

# Make scripts executable
chmod +x git-commit-smart

# Add to PATH for current session
export PATH="$PWD:$PATH"

# Create git aliases for intelligent commits
git config --global alias.smart-commit '!'"$PWD/git-commit-smart"
git config --global alias.sc '!'"$PWD/git-commit-smart"  # Short alias
git config --global alias.analyze-commit '!'"$PWD/git-commit-smart --analyze-only"

echo "✅ Git aliases created:"
echo "   git smart-commit -m 'message'  # Intelligent commit with optimization"
echo "   git sc -m 'message'            # Short alias for smart commit"
echo "   git analyze-commit             # Analyze optimization without committing"

# Test the intelligent filtering
echo ""
echo "🧪 Testing intelligent hook analysis..."
./git-commit-smart --analyze-only

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📚 Usage Examples:"
echo "   git sc -m 'Update README'                    # Fast commit for docs"
echo "   git smart-commit -m 'Fix critical bug'       # Optimized commit"
echo "   git smart-commit --force-full -m 'Security'  # Run all hooks"
echo "   git analyze-commit                           # Preview optimization"
echo ""
echo "💡 The system will automatically:"
echo "   - Skip tests for documentation-only changes"
echo "   - Skip Python tools for markdown files"
echo "   - Run full validation for code changes"
echo "   - Optimize based on file types and changeset size"
