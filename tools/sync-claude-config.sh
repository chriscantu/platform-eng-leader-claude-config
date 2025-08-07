#!/bin/bash

# sync-claude-config.sh
# Synchronizes Director of Engineering Claude configuration between project directory and global Claude config

set -euo pipefail

# Configuration
PROJECT_DIR="${PROJECT_DIR:-$(dirname "$(dirname "$(realpath "$0")")")}"
CLAUDE_GLOBAL_DIR="${CLAUDE_GLOBAL_DIR:-$HOME/.claude}"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Core SuperClaude framework files to sync
CORE_FILES=(
    "CLAUDE.md"
    "COMMANDS.md"
    "FLAGS.md"
    "PRINCIPLES.md"
    "RULES.md"
    "MCP.md"
    "PERSONAS.md"
    "ORCHESTRATOR.md"
    "MODES.md"
    "weekly-report-config.yaml"
    "weekly-report-template.md"
    "jira-integration-spec.md"
)

# Function to print colored output
print_status() {
    echo -e "${BLUE}[SYNC]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if file needs sync
needs_sync() {
    local file="$1"
    local project_file="${PROJECT_DIR}/${file}"
    local global_file="${CLAUDE_GLOBAL_DIR}/${file}"

    if [[ ! -f "$project_file" ]]; then
        return 1  # Project file doesn't exist
    fi

    if [[ ! -f "$global_file" ]]; then
        return 0  # Global file doesn't exist, needs sync
    fi

    # Compare file modification times and content
    if ! cmp -s "$project_file" "$global_file"; then
        return 0  # Files are different, needs sync
    fi

    return 1  # Files are the same
}

# Function to sync a single file
sync_file() {
    local file="$1"
    local project_file="${PROJECT_DIR}/${file}"
    local global_file="${CLAUDE_GLOBAL_DIR}/${file}"

    if [[ ! -f "$project_file" ]]; then
        print_error "Project file $project_file does not exist"
        return 1
    fi

    # Create backup of global file if it exists and is different
    if [[ -f "$global_file" ]] && ! cmp -s "$project_file" "$global_file"; then
        local backup_file="${global_file}.backup.$(date +%Y%m%d_%H%M%S)"
        cp "$global_file" "$backup_file"
        print_warning "Backed up existing global file to $(basename "$backup_file")"
    fi

    # Copy project file to global location
    cp "$project_file" "$global_file"
    print_success "Synced $file"

    return 0
}

# Function to validate sync
validate_sync() {
    local errors=0

    print_status "Validating sync..."

    for file in "${CORE_FILES[@]}"; do
        local project_file="${PROJECT_DIR}/${file}"
        local global_file="${CLAUDE_GLOBAL_DIR}/${file}"

        if [[ ! -f "$project_file" ]]; then
            print_error "Project file $file is missing"
            ((errors++))
            continue
        fi

        if [[ ! -f "$global_file" ]]; then
            print_error "Global file $file is missing"
            ((errors++))
            continue
        fi

        if ! cmp -s "$project_file" "$global_file"; then
            print_error "Files $file are not in sync"
            ((errors++))
        fi
    done

    if [[ $errors -eq 0 ]]; then
        print_success "All files are in sync!"
        return 0
    else
        print_error "Found $errors sync issues"
        return 1
    fi
}

# Main sync function
main() {
    local command="${1:-sync}"

    case "$command" in
        "sync")
            print_status "Starting Director of Engineering Claude Config Sync..."
            print_status "Project: $PROJECT_DIR"
            print_status "Global:  $CLAUDE_GLOBAL_DIR"
            echo

            # Check if directories exist
            if [[ ! -d "$PROJECT_DIR" ]]; then
                print_error "Project directory does not exist: $PROJECT_DIR"
                exit 1
            fi

            if [[ ! -d "$CLAUDE_GLOBAL_DIR" ]]; then
                print_error "Global Claude directory does not exist: $CLAUDE_GLOBAL_DIR"
                exit 1
            fi

            local synced_files=0
            local total_files=${#CORE_FILES[@]}

            # Sync each core file
            for file in "${CORE_FILES[@]}"; do
                if needs_sync "$file"; then
                    if sync_file "$file"; then
                        ((synced_files++))
                    fi
                else
                    print_status "$file is already in sync"
                fi
            done

            echo
            print_success "Sync complete: $synced_files/$total_files files updated"

            # Validate the sync
            echo
            if validate_sync; then
                print_success "Director of Engineering Claude configuration is synchronized!"
            else
                print_error "Sync validation failed"
                exit 1
            fi
            ;;

        "check")
            print_status "Checking sync status..."

            local out_of_sync=0
            for file in "${CORE_FILES[@]}"; do
                if needs_sync "$file"; then
                    print_warning "$file needs sync"
                    ((out_of_sync++))
                else
                    print_success "$file is in sync"
                fi
            done

            if [[ $out_of_sync -eq 0 ]]; then
                print_success "All files are in sync!"
            else
                print_warning "$out_of_sync files need synchronization"
                echo
                print_status "Run './sync-claude-config.sh sync' to synchronize"
                exit 1
            fi
            ;;

        "help"|"-h"|"--help")
            echo "Director of Engineering Claude Config Sync"
            echo
            echo "Usage: $0 [command]"
            echo
            echo "Commands:"
            echo "  sync    Synchronize project config to global Claude config (default)"
            echo "  check   Check if configs are in sync"
            echo "  help    Show this help message"
            echo
            echo "Files synchronized:"
            for file in "${CORE_FILES[@]}"; do
                echo "  - $file"
            done
            ;;

        *)
            print_error "Unknown command: $command"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
