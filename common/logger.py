import logging
import configparser
import json
import re
import os
import sys
#----------------------------------------------------------------
# Logging
#----------------------------------------------------------------
logging.getLogger('pdfminer').setLevel(logging.CRITICAL) 
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, "app.log")

logging.basicConfig(
    level=logging.INFO,  # Mức độ ghi log (INFO, DEBUG, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
    ]
)

logger = logging.getLogger(__name__) 
