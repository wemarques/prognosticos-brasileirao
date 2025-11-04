"""
Test logging system
"""
import os
import sys
import logging
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from utils.logger import setup_logger


def test_logger_creation():
    """Test that logger can be created"""
    logger = setup_logger("test_module")
    assert logger is not None
    assert logger.name == "test_module"
    print("✅ Logger creation OK")


def test_log_file_exists():
    """Test that log file is created"""
    logger = setup_logger("test_file")
    logger.info("Test message")
    
    log_dir = Path(ROOT_DIR) / "logs"
    assert log_dir.exists(), "Log directory not created"
    
    log_files = list(log_dir.glob("*.log"))
    assert len(log_files) > 0, "No log files created"
    
    print(f"✅ Log directory exists with {len(log_files)} log file(s)")


def test_log_levels():
    """Test different log levels"""
    logger = setup_logger("test_levels", level=logging.DEBUG)
    
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    
    print("✅ All log levels working")


def test_rotating_file_handler():
    """Test that rotating file handler is configured"""
    logger = setup_logger("test_rotation")
    
    has_rotating_handler = False
    for handler in logger.handlers:
        if isinstance(handler, logging.handlers.RotatingFileHandler):
            has_rotating_handler = True
            assert handler.maxBytes > 0, "Max bytes not configured"
            assert handler.backupCount > 0, "Backup count not configured"
            print(f"✅ Rotating handler configured: maxBytes={handler.maxBytes}, backupCount={handler.backupCount}")
            break
    
    assert has_rotating_handler, "No rotating file handler found"


def test_console_handler():
    """Test that console handler is configured"""
    logger = setup_logger("test_console")
    
    has_console_handler = False
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
            has_console_handler = True
            print("✅ Console handler configured")
            break
    
    assert has_console_handler, "No console handler found"


def test_no_duplicate_handlers():
    """Test that calling setup_logger twice doesn't duplicate handlers"""
    logger1 = setup_logger("test_duplicate")
    handler_count_1 = len(logger1.handlers)
    
    logger2 = setup_logger("test_duplicate")
    handler_count_2 = len(logger2.handlers)
    
    assert handler_count_1 == handler_count_2, f"Handlers duplicated: {handler_count_1} vs {handler_count_2}"
    print(f"✅ No duplicate handlers ({handler_count_1} handlers)")


if __name__ == "__main__":
    print("🔍 Running logging system tests...\n")
    
    try:
        test_logger_creation()
        test_log_file_exists()
        test_log_levels()
        test_rotating_file_handler()
        test_console_handler()
        test_no_duplicate_handlers()
        
        print("\n🎉 ALL LOGGING TESTS PASSED!")
        print(f"\n📁 Log files location: {ROOT_DIR / 'logs'}")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
