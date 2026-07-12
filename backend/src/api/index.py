import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from main import app 

# Vercel's Python runtime just needs `app` exposed