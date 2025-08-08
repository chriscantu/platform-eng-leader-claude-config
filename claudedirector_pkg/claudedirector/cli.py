"""
ClaudeDirector CLI - New package-based implementation
Backward compatible wrapper around the legacy claudedirector script
"""

import sys
from pathlib import Path

def main():
    """Main CLI entry point - delegates to legacy claudedirector for now"""
    
    # Find the legacy claudedirector script
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent
    legacy_cli = project_root / "claudedirector"
    
    if not legacy_cli.exists():
        print("❌ Legacy claudedirector CLI not found")
        print("   Please run from the project root directory")
        sys.exit(1)
    
    # Import and run legacy CLI
    sys.path.insert(0, str(project_root))
    
    try:
        # Import the legacy CLI module
        import importlib.util
        spec = importlib.util.spec_from_file_location("legacy_cli", legacy_cli)
        legacy_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(legacy_module)
        
        # Run the legacy CLI main function
        if hasattr(legacy_module, 'main'):
            legacy_module.main()
        else:
            print("❌ Legacy CLI main function not found")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error running legacy CLI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
