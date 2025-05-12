from flask import Flask, request, jsonify, render_template, send_from_directory
import kociemba
import os

app = Flask(__name__, static_folder='static')

# Route for the main page
@app.route('/')
def index():
    return render_template('index.html')

# Route to serve static files (CSS, JS) - Flask does this automatically if configured
# but explicit routes can be useful for understanding.
# In this setup, Flask's default static file handling is used.

# Route for the solver API endpoint
@app.route('/solve', methods=['POST'])
def solve_cube():
    """
    Receives a scrambled cube state string and returns the solution.
    Expects a JSON body with a 'cubeState' key.
    """
    try:
        data = request.get_json()
        if not data or 'cubeState' not in data:
            return jsonify({"error": "Invalid request body. Missing 'cubeState'."}), 400

        scrambled_state_string = data['cubeState']

        # Basic validation of the input string length and characters
        if len(scrambled_state_string) != 54 or not all(c in 'URFLDB' for c in scrambled_state_string):
             return jsonify({"error": "Invalid cube state string format. Must be 54 characters from U, R, F, D, L, B."}), 400
            
            # Attempt to solve the cube
        try:
            solution = kociemba.solve(scrambled_state_string)
            return jsonify({"solution": solution})
        except Exception as solve_error:
            # kociemba.solve() raises an exception for invalid cube states
            return jsonify({"error": f"Could not solve cube. Invalid state? {solve_error}"}), 400


    except Exception as e:
        # Catch any other unexpected errors
        return jsonify({"error": f"An internal error occurred: {str(e)}"}), 500

# This is for running locally. Render uses a production web server.
if __name__ == '__main__':
    # Make sure the 'static' directory exists for CSS/JS
    if not os.path.exists('static'):
        os.makedirs('static')
    # Create dummy files if they don't exist (for initial setup)
    if not os.path.exists('static/style.css'):
         with open('static/style.css', 'w') as f:
             f.write("/* Basic CSS */")
    if not os.path.exists('static/script.js'):
         with open('static/script.js', 'w') as f:
             f.write("// Basic JS")

    app.run(debug=True)
