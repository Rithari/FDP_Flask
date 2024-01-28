from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import os
import logging
from logging.handlers import RotatingFileHandler

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
logger.addHandler(handler)


app = Flask(__name__)

def run_notebook():
    try:
        notebook_path = '/path/to/your/notebook.ipynb'
        
        with open(notebook_path) as f:
            nb = nbformat.read(f, as_version=4)
            ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
            ep.preprocess(nb)

        logger.info("Successfully executed the notebook.")
    except Exception as e:
        logger.error(f"Error executing the notebook: {e}", exc_info=True)

# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=run_notebook, trigger='interval', hours=24) # Run every 24 hours
scheduler.start()

@app.before_first_request
def initialize_scheduler():
    if not scheduler.running:
        scheduler.start()

@app.route('/')
def index():
    return "Flask App with Scheduled Jupyter Notebook Execution"

if __name__ == '__main__':
    try:
        app.run(debug=True, port=5000)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
