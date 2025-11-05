"""Utils package initialization"""
import logging

# Setup logging
def setup_logging():
    """Configure logging for the application"""
    # Root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Agent logger
    agent_logger = logging.getLogger("agent")
    agent_logger.setLevel(logging.INFO)
    
    # Backend logger
    backend_logger = logging.getLogger("backend")
    backend_logger.setLevel(logging.INFO)

# Initialize logging when package is imported
setup_logging()

# Package exports
from . import config
from . import models
from . import storage
from . import backend
from . import agent

__all__ = ['config', 'models', 'storage', 'backend', 'agent']