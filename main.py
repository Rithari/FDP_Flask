from flask import Flask, request, jsonify
import papermill as pm
import logging
from logging.handlers import RotatingFileHandler
import tempfile

# Existing logging configuration...

app = Flask(__name__)

@app.route('/stats', methods=['POST'])
def run_stats_notebook():
    try:
        # Retrieve data from POST request
        stats_category = request.json['stats_category']
        identifier = request.json['identifier']
        
        # Define the input notebook path
        input_nb_path = './statistics.ipynb'

        # Use a temporary file for the output notebook. File is deleted automatically after the context manager exits.
        with tempfile.NamedTemporaryFile(suffix='.ipynb') as temp_output:
            output_nb_path = temp_output.name

            # Execute the notebook with parameters
            pm.execute_notebook(
                input_nb_path,
                output_nb_path,
                parameters={
                    'stats_category': stats_category,
                    'identifier': identifier
                }
            )

        logger.info("Successfully executed the notebook with parameters.")
        return jsonify({"message": "Notebook executed successfully"})
    except Exception as e:
        logger.error(f"Error executing the notebook: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
