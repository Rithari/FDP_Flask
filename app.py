from flask import Flask, request, jsonify, send_file, after_this_request
import papermill as pm
import logging
from logging.handlers import RotatingFileHandler
from apscheduler.schedulers.background import BackgroundScheduler
import tempfile
import os
import glob
import shutil
import zipfile
from flask_cors import CORS

# Configure logging for the application
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = RotatingFileHandler("app.log", maxBytes=10000, backupCount=3)
logger.addHandler(handler)

# Create the Flask application instance
app = Flask(__name__)

# Configure Cross-Origin Resource Sharing (CORS)
originURL = "*"
CORS(app, resources={r"/*": {"origins": originURL}})


# Function to clear output directory
def clear_output_directory():
    output_dir = "./outputs"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    logger.info("Cleared output directory.")


# Set up a scheduler to clear the output directory daily at midnight
scheduler = BackgroundScheduler()
scheduler.add_job(clear_output_directory, "cron", hour=0)
scheduler.start()


# Function to create a temporary zip file with the specified files
def create_zip(files):
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "output_svgs.zip")
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for file in files:
            zipf.write(file, os.path.basename(file))
    return zip_path


# Endpoint to run statistics notebook and return SVG or zip file
@app.route("/stats", methods=["POST"])
def run_stats_notebook():
    try:
        # Extract parameters from the request
        stats_category = request.json["stats_category"]
        identifier = request.json.get("identifier")

        # Define the output directory
        output_dir = f"./outputs/{stats_category}"
        if identifier:
            output_dir = f"{output_dir}/{identifier}"

        # Define the input notebook path
        input_nb_path = "./statistics.ipynb"

        # Execute the notebook if SVGs haven't been generated yet
        existing_svgs = glob.glob(f"{output_dir}/*.svg")
        if not existing_svgs:
            with tempfile.NamedTemporaryFile(suffix=".ipynb") as temp_output:
                output_nb_path = temp_output.name

                # Execute the notebook with parameters using Papermill
                pm.execute_notebook(
                    input_nb_path,
                    output_nb_path,
                    parameters={
                        "stats_category": stats_category,
                        "identifier": identifier,
                    },
                )

            logger.info("Successfully executed the notebook with parameters.")

            # Collect the generated SVGs
            generated_svgs = glob.glob(f"{output_dir}/*.svg")
        else:
            # Use existing SVGs
            generated_svgs = existing_svgs

        # Sending the SVG files
        if len(generated_svgs) == 1:
            return send_file(generated_svgs[0], mimetype="image/svg+xml")
        elif generated_svgs:
            zip_file = create_zip(generated_svgs)

            @after_this_request
            def remove_file(response):
                shutil.rmtree(os.path.dirname(zip_file))
                return response

            return send_file(zip_file, as_attachment=True)
        else:
            return jsonify({"error": "No SVG files generated"}), 404
    except Exception as e:
        logger.error(f"Error executing the notebook: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


# Run the Flask app
if __name__ == "__main__":
    logger.info("__name__ is set to __main__, running the Flask app locally.")
    app.run(debug=True, port=4000)
