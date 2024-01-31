from flask import Flask, request, jsonify, send_file
import papermill as pm
import logging
from logging.handlers import RotatingFileHandler
import tempfile
import os
import glob
from apscheduler.schedulers.background import BackgroundScheduler
import shutil

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = RotatingFileHandler("app.log", maxBytes=10000, backupCount=3)
logger.addHandler(handler)
app = Flask(__name__)


def clear_output_directory():
    output_dir = "./outputs"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    logger.info("Cleared output directory.")


# Scheduler to clear output directory once a day at midnight
scheduler = BackgroundScheduler()
scheduler.add_job(clear_output_directory, "cron", hour=0)
scheduler.start()


@app.route("/stats", methods=["POST"])
def run_stats_notebook():
    try:
        stats_category = request.json["stats_category"]
        identifier = request.json.get(
            "identifier"
        )  # What does this look like if it's not present? None? Answer: None

        output_dir = f"./outputs/{stats_category}"
        if identifier:
            output_dir = f"{output_dir}/{identifier}"

        # Check if output already exists to serve cached version
        existing_svgs = glob.glob(f"{output_dir}/*.svg")
        if existing_svgs:
            return jsonify({"files": existing_svgs})

        # Define the input notebook path
        input_nb_path = "./statistics.ipynb"

        with tempfile.NamedTemporaryFile(suffix=".ipynb") as temp_output:
            output_nb_path = temp_output.name

            # Execute the notebook with parameters
            pm.execute_notebook(
                input_nb_path,
                output_nb_path,
                parameters={"stats_category": stats_category, "identifier": identifier},
            )

        logger.info("Successfully executed the notebook with parameters.")

        # Collect the generated SVGs
        generated_svgs = glob.glob(f"{output_dir}/*.svg")
        return jsonify({"files": generated_svgs})
    except Exception as e:
        logger.error(f"Error executing the notebook: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
