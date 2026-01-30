"""
Quick test to verify minimal architecture works
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all UI modules can be imported"""
    print("Testing UI module imports...")
    
    try:
        from ui.sender import render_sender
        print("✅ ui/sender.py imports successfully")
    except Exception as e:
        print(f"❌ ui/sender.py import failed: {e}")
    
    try:
        from ui.manager import render_manager
        print("✅ ui/manager.py imports successfully")
    except Exception as e:
        print(f"❌ ui/manager.py import failed: {e}")
    
    try:
        from ui.supervisor import render_supervisor
        print("✅ ui/supervisor.py imports successfully")
    except Exception as e:
        print(f"❌ ui/supervisor.py import failed: {e}")
    
    try:
        from ui.viewer import render_viewer
        print("✅ ui/viewer.py imports successfully")
    except Exception as e:
        print(f"❌ ui/viewer.py import failed: {e}")
    
    try:
        from ui.receiver import render_receiver
        print("✅ ui/receiver.py imports successfully")
    except Exception as e:
        print(f"❌ ui/receiver.py import failed: {e}")
    
    try:
        from ui.coo import render_coo
        print("✅ ui/coo.py imports successfully")
    except Exception as e:
        print(f"❌ ui/coo.py import failed: {e}")

def test_event_sourcing():
    """Test that event sourcing module loads"""
    print("\nTesting event sourcing...")
    
    try:
        from app.storage.event_log import get_all_shipments_by_state
        print("✅ Event sourcing module loads")
        
        # Try to get shipments
        shipments = get_all_shipments_by_state()
        print(f"✅ Retrieved {len(shipments)} shipments from event store")
        
    except Exception as e:
        print(f"❌ Event sourcing failed: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("MINIMAL ARCHITECTURE TEST")
    print("=" * 60)
    
    test_imports()
    test_event_sourcing()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print("\nTo run the app:")
    print("  streamlit run app_minimal.py")
