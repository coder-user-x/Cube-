from flask import Flask, request, jsonify, render_template, send_from_directory
import kociemba
import os

# Ensure template_folder and static_folder are correctly specified
# 'templates' is the default for render_template
# 'static' is the default for static files, but explicitly stating can be clearer
app = Flask(__name__, static_folder='static', template_folder='templates')

# Route for the main page
@app.route('/')
def index():
    # This will render the index.html file found inside the 'templates' folder
    return render_template('index.html')

# Route for the solver API endpoint
@app.route('/solve', methods=['POST'])
def solve_cube():
    """
    Receives a scrambled cube state string and returns the solution.
    Expects a JSON body with a 'cubeState' key.
    Includes logic to handle potentially swapped White ('U') and Yellow ('D') centers
    in the input string based on standard Kociemba color representation.
    """
    try:
        # Get the JSON data from the request body
        data = request.get_json()
        if not data or 'cubeState' not in data:
            # Return a bad request error if the expected data is missing
            return jsonify({"error": "Invalid request body. Missing 'cubeState'."}), 400

        scrambled_state_string = data['cubeState']

        # Basic validation of the input string length and allowed characters
        # Kociemba expects a 54-character string using U, R, F, D, L, B for colors
        if len(scrambled_state_string) != 54 or not all(c in 'URFLDB' for c in scrambled_state_string):
             return jsonify({"error": "Invalid cube state string format. Must be 54 characters from U, R, F, D, L, B."}), 400

        # --- Logic to handle potentially swapped White ('U') and Yellow ('D') centers ---
        # This logic assumes the standard Kociemba color representation in the input string:
        # 'U' represents White, 'R' represents Red, 'F' represents Blue,
        # 'D' represents Yellow, 'L' represents Orange, 'B' represents Green.
        # The positions in the string correspond to the faces in the standard solved orientation.
        # Center facelet indices (0-indexed): U:4, R:13, F:22, D:31, L:40, B:49

        cube_list = list(scrambled_state_string)
        up_center_color_char = cube_list[4] # Character representing the color of the Up center
        down_center_color_char = cube_list[31] # Character representing the color of the Down center

        # Check if the colors of the Up and Down centers in the input string
        # are swapped compared to the standard Kociemba solved state (U='U', D='D').
        # We are checking if the Up center is 'D' (Yellow) and the Down center is 'U' (White).
        needs_color_swap = False
        if up_center_color_char == 'D' and down_center_color_char == 'U':
             needs_color_swap = True
             # In a real application, you might want to log this event
             print("Detected swapped White ('U') and Yellow ('D') centers in the input string.")

        # Create a new string with colors potentially swapped internally
        processed_cube_list = []
        if needs_color_swap:
            # If the centers are swapped in the input, swap the 'U' and 'D' characters
            # throughout the string internally before sending to kociemba.solve().
            # This makes the string conform to the standard Kociemba color mapping.
            for color_char in cube_list:
                if color_char == 'U': # If the character is 'U' (representing White in input)
                    processed_cube_list.append('D') # Treat it as 'D' (representing Yellow)
                elif color_char == 'D': # If the character is 'D' (representing Yellow in input)
                    processed_cube_list.append('U') # Treat it as 'U' (representing White)
                else:
                    processed_cube_list.append(color_char) # Keep other color characters as they are
            processed_state_string = "".join(processed_cube_list)
            print(f"Processed string for solver: {processed_state_string}") # Log the processed string
        else:
            # If centers are not swapped, use the original input string
            processed_state_string = scrambled_state_string

        # --- End of color swap logic ---

        # Attempt to solve the cube using the kociemba library
        # kociemba.solve expects the input string to follow the standard Kociemba
        # color representation (U=White, R=Red, F=Blue, D=Yellow, L=Orange, B=Green).
        # By potentially swapping 'U' and 'D' above, we ensure the input to solve()
        # conforms to this standard, regardless of the original input's U/D center colors.
        try:
            solution = kociemba.solve(processed_state_string)

            # The returned solution is the sequence of moves to get from the
            # processed_state_string to the standard Kociemba solved state.
            # If we performed a swap, this solution will effectively solve the original
            # cube (which had swapped U/D centers) to a state where the physical
            # Yellow face is on top and the physical White face is on the bottom
            # (corresponding to the standard Kociemba U and D positions after the swap).

            return jsonify({"solution": solution})

        except Exception as solve_error:
            # The kociemba.solve() function raises an exception if the input
            # string represents an invalid cube state (e.g., impossible scramble).
            return jsonify({"error": f"Could not solve cube. Invalid state? {solve_error}"}), 400

    except Exception as e:
        # Catch any other unexpected errors during request processing
        return jsonify({"error": f"An internal server error occurred: {str(e)}"}), 500

# This block allows running the Flask application locally for testing.
# Render uses a production-ready WSGI server like Gunicorn to run the app.
if __name__ == '__main__':
    # Ensure static and templates directories exist for local running convenience
    # In a typical deployment, these folders would be part of your project structure
    # and served by the web server or Flask's static/template handling.
    if not os.path.exists('static'):
        os.makedirs('static')
    if not os.path.exists('templates'):
        os.makedirs('templates')
    # Create dummy files if they don't exist (for initial local setup without full project clone)
    # In your actual project, these files should contain the HTML, CSS, and JS code.
    if not os.path.exists('static/style.css'):
         with open('static/style.css', 'w') as f:
             f.write("/* Basic CSS */")
    if not os.path.exists('static/script.js'):
         with open('static/script.js', 'w') as f:
             f.write("// Basic JS")
    if not os.path.exists('templates/index.html'):
        with open('templates/index.html', 'w') as f:
            f.write("")

    # Run the Flask development server
    # debug=True provides helpful error messages during local development
    app.run(debug=True)
