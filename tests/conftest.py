import os
import sys
from pathlib import Path
import pytest
import logging

# Get the project root directory (parent of tests directory)
project_root = Path(__file__).parent.parent

# Add both project root and my_digital_being directory to Python path
sys.path.append(str(project_root))
sys.path.append(str(project_root / "my_digital_being"))

# Also modify PYTHONPATH environment variable
os.environ["PYTHONPATH"] = f"{str(project_root)}{os.pathsep}{str(project_root / 'my_digital_being')}"

# Configure logging to show during tests
@pytest.fixture(autouse=True)
def setup_logging():
    # Create a console handler and set level to INFO
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Create formatter and add it to the handler
    formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    
    # Get root logger and add handler
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler) 