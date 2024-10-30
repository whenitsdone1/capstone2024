import unittest
import os
import logging as logs
from contextlib import contextmanager

logs.basicConfig(level=logs.CRITICAL + 1)

@contextmanager
def suppress_logs():
    """
    Context manager to completely suppress all logs and restore original state afterwards. 
    Useful not logging testing output.
    """
    # Store original logging configuration
    loggers = [logs.getLogger(name) for name in logs.root.manager.loggerDict]
    original_levels = {logger: logger.level for logger in loggers}
    original_root_level = logs.getLogger().level

    try:
        # Suppress all loggers
        for logger in loggers:
            logger.setLevel(logs.CRITICAL + 1) 
        logs.getLogger().setLevel(logs.CRITICAL + 1)        
        yield
    finally:
        # Restore original logging configuration
        for logger, level in original_levels.items():
            logger.setLevel(level)
        logs.getLogger().setLevel(original_root_level)
        

# Run all the tests in the tests subdir
def run_tests():
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Specify the 'tests' subdirectory
    test_dir = os.path.join(current_dir, 'tests')

    # Create a test suite
    test_suite = unittest.TestLoader().discover(
        start_dir=test_dir,
        pattern='*_tests.py'
    )
  

    # Run tests without logs
    with suppress_logs():
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(test_suite)



    print(f"\nSummary: {result.testsRun} tests ran in total.")
    if result.wasSuccessful():
        print("All tests ran successfully!")
    else:
        print(f"{len(result.failures)} tests failed.")
        print(f"{len(result.errors)} tests had errors.")



if __name__ == '__main__':
    run_tests()
