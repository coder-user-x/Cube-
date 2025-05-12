document.addEventListener('DOMContentLoaded', () => {
    const facelets = document.querySelectorAll('.facelet');
    const colorOptions = document.querySelectorAll('.color-option');
    const getSolutionButton = document.getElementById('get-solution');
    const solutionSteps = document.getElementById('solution-steps');

    let selectedColor = null;

    // Function to get the color character from a facelet's class
    function getFaceletColor(facelet) {
        const colors = ['U', 'R', 'F', 'D', 'L', 'B'];
        for (const color of colors) {
            if (facelet.classList.contains(color)) {
                return color;
            }
        }
        return 'X'; // Placeholder for uncolored or invalid
    }

     // Function to set the initial solved state colors
    function initializeSolvedState() {
        const faces = {
            'U': document.querySelector('.face.up'),
            'L': document.querySelector('.face.left'),
            'F': document.querySelector('.face.front'),
            'R': document.querySelector('.face.right'),
            'B': document.querySelector('.face.back'),
            'D': document.querySelector('.face.down')
        };

        for (const faceKey in faces) {
            const face = faces[faceKey];
            if (face) {
                const faceletsOnFace = face.querySelectorAll('.facelet');
                faceletsOnFace.forEach(facelet => {
                    // Remove any existing color classes
                     facelet.classList.remove('U', 'R', 'F', 'D', 'L', 'B', 'X', 'gray'); // Remove all
                     facelet.classList.add(faceKey); // Add the correct color class
                });
            }
        }
    }


    // Initialize the cube display to a solved state on load
     initializeSolvedState();


    // Color picking functionality
    colorOptions.forEach(option => {
        option.addEventListener('click', () => {
            // Remove selected class from all options
            colorOptions.forEach(opt => opt.classList.remove('selected'));
            // Add selected class to the clicked option
            option.classList.add('selected');
            // Store the selected color (U, R, F, D, L, B)
            selectedColor = option.getAttribute('data-color');
        });
    });

    // Apply selected color to facelets on click
    facelets.forEach(facelet => {
        facelet.addEventListener('click', () => {
            if (selectedColor) {
                // Remove any existing color classes
                facelet.classList.remove('U', 'R', 'F', 'D', 'L', 'B', 'X', 'gray');
                // Add the selected color class
                facelet.classList.add(selectedColor);
            }
        });
    });

    // --- Get Cube State String ---
    function getCubeStateString() {
        let stateString = "";
         // Order of faces for the state string: U R F D L B
        const faceOrder = ['U', 'R', 'F', 'D', 'L', 'B'];

        faceOrder.forEach(faceKey => {
            const face = document.querySelector(`.face[data-face="${faceKey}"]`);
            if (face) {
                const faceletsOnFace = face.querySelectorAll('.facelet');
                faceletsOnFace.forEach(facelet => {
                    stateString += getFaceletColor(facelet);
                });
            }
        });

        return stateString;
    }

    // --- Event Listener for the Solve Button ---
    getSolutionButton.addEventListener('click', async () => {
        const cubeState = getCubeStateString();

        // Basic validation: Check if all facelets are colored
        if (cubeState.includes('X') || cubeState.length !== 54) {
            solutionSteps.textContent = "Error: Please ensure all 54 facelets have a color.";
            return;
        }

        solutionSteps.textContent = "Calculating solution...";
        getSolutionButton.disabled = true; // Disable button while solving

        try {
            // Send the cube state to the backend solver
            const response = await fetch('/solve', { // Endpoint on your Flask server
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ cubeState: cubeState })
            });

            if (response.ok) {
                const data = await response.json();
                if (data.solution) {
                    solutionSteps.textContent = data.solution;
                } else if (data.error) {
                     solutionSteps.textContent = `Solver Error: ${data.error}`;
                } else {
                     solutionSteps.textContent = "Unexpected response from solver.";
                }

            } else {
                 const errorText = await response.text(); // Get more details if available
                 solutionSteps.textContent = `Error from server: ${response.status} ${response.statusText} - ${errorText}`;
            }
        } catch (error) {
            solutionSteps.textContent = `Error communicating with solver service: ${error}`;
        } finally {
             getSolutionButton.disabled = false; // Re-enable button
        }
    });
});
