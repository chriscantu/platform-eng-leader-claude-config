#!/bin/bash

# Secure Jira API Token Setup for UI Foundation Strategic Analysis
# This script helps securely configure your Jira API token

echo "🔐 Jira API Token Setup for Strategic Analysis"
echo "=============================================="
echo ""

# Check if token is already set
if [[ -n "$JIRA_API_TOKEN" ]]; then
    echo "✅ JIRA_API_TOKEN is already set (${#JIRA_API_TOKEN} characters)"
    echo ""
    echo "Testing current token..."

    # Test the current token
    TEST_RESPONSE=$(curl -s -u "user1@company.com:$JIRA_API_TOKEN" \
        -H "Accept: application/json" \
        "https://company.atlassian.net/rest/api/3/myself" 2>/dev/null)

    if echo "$TEST_RESPONSE" | jq -e '.displayName' >/dev/null 2>&1; then
        USER_NAME=$(echo "$TEST_RESPONSE" | jq -r '.displayName')
        echo "✅ Token is valid! Authenticated as: $USER_NAME"
        echo ""
        echo "🚀 Ready to extract initiative data!"
        echo "   Run: ./tools/extract-current-initiatives.sh"
        exit 0
    else
        echo "❌ Current token is invalid or expired"
        echo "   Please generate a new token and update your configuration"
    fi
else
    echo "ℹ️  JIRA_API_TOKEN not found"
fi

echo ""
echo "📋 Token Setup Instructions:"
echo "=============================="
echo ""
echo "1. Generate API Token:"
echo "   → Go to: https://id.atlassian.com/manage-profile/security/api-tokens"
echo "   → Click: 'Create API token'"
echo "   → Label: 'UI Foundation Strategic Analysis'"
echo "   → Copy the generated token"
echo ""
echo "2. Set Token (Choose one method):"
echo ""

# Detect shell
if [[ "$SHELL" == *"fish"* ]]; then
    echo "   🐠 For Fish shell (detected):"
    echo "   set -gx JIRA_API_TOKEN 'your-token-here'"
    echo ""
    echo "   To make it permanent:"
    echo "   echo \"set -gx JIRA_API_TOKEN 'your-token-here'\" >> ~/.config/fish/config.fish"
elif [[ "$SHELL" == *"zsh"* ]]; then
    echo "   🚀 For Zsh shell (detected):"
    echo "   export JIRA_API_TOKEN='your-token-here'"
    echo ""
    echo "   To make it permanent:"
    echo "   echo \"export JIRA_API_TOKEN='your-token-here'\" >> ~/.zshrc"
else
    echo "   🐚 For Bash shell:"
    echo "   export JIRA_API_TOKEN='your-token-here'"
    echo ""
    echo "   To make it permanent:"
    echo "   echo \"export JIRA_API_TOKEN='your-token-here'\" >> ~/.bashrc"
fi

echo ""
echo "3. Test Token:"
echo "   source ~/.config/fish/config.fish  # or restart terminal"
echo "   ./tools/setup-jira-token.sh        # run this script again to test"
echo ""
echo "4. Extract Data:"
echo "   ./tools/extract-current-initiatives.sh"
echo ""
echo "🔒 Security Notes:"
echo "   • Keep your API token secure and private"
echo "   • Don't commit tokens to git repositories"
echo "   • Regenerate periodically for security"
echo "   • Use only for authorized UI Foundation analysis"
echo ""
