"""Configure pytest for the nds_database package."""

import os
import sys

# Add the package to the path so we can import it
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
