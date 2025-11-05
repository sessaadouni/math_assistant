#!/usr/bin/env bash
# Quick CLI test with SOLID architecture

echo "🎓 Testing Math Assistant CLI with SOLID Architecture"
echo "=" | tr '=' '='  | head -c 70; echo

# Check Python version
python_version=$(python3 --version 2>&1)
echo "Python: $python_version"

# Check environment
if [ "$USE_LEGACY_ASSISTANT" = "1" ]; then
    echo "⚠️  Mode: LEGACY (monolithic)"
else
    echo "✅ Mode: SOLID (new architecture)"
fi

echo
echo "=" | tr '=' '='  | head -c 70; echo
echo

# Quick smoke test
echo "🧪 Running smoke test..."
python3 << 'PYEOF'
import sys
try:
    from src.assistant import get_assistant
    print("✅ Import successful")
    
    # Check type (but don't instantiate to avoid loading vector store)
    from src.application.adapters import LegacyAssistantAdapter
    print(f"✅ Adapter available: LegacyAssistantAdapter")
    
    # Check all required methods exist
    required = ["route_and_execute", "run_task", "memory", "ensure_ready"]
    for method in required:
        if hasattr(LegacyAssistantAdapter, method):
            print(f"✅ Method exists: {method}")
        else:
            print(f"❌ Missing method: {method}")
            sys.exit(1)
    
    print()
    print("🎉 All checks passed! CLI is ready to use SOLID architecture")
    print()
    print("💡 To run the full CLI:")
    print("   python scripts/run_cli.py")
    print()
    print("💡 To switch to legacy mode:")
    print("   USE_LEGACY_ASSISTANT=1 python scripts/run_cli.py")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYEOF

exit_code=$?
echo
echo "=" | tr '=' '='  | head -c 70; echo

if [ $exit_code -eq 0 ]; then
    echo "✅ CLI smoke test PASSED"
else
    echo "❌ CLI smoke test FAILED"
fi

exit $exit_code
