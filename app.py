# app.py
import os
from flask import Flask, request, render_template, jsonify
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
   
    raise ValueError("OPENAI_API_KEY environment variable not set. "
                     "Please create a .env file in the same directory as app.py "
                     "and add OPENAI_API_KEY=YOUR_API_KEY_HERE to it.")

client = OpenAI(api_key=openai_api_key)

def clarify_concept(concept_query: str, subject_context: str = "") -> str:
    """
    Generates an explanation for an engineering concept using an LLM.
    Optionally includes a subject context to tailor the explanation.
    """
    system_prompt = (
        "You are an AI assistant for engineering students on the Edwisely platform. "
        "Your goal is to provide clear, concise, and accurate explanations of engineering concepts. "
        "Always tailor your explanation for an engineering student, assuming they have some foundational knowledge "
        "but need clarity on a specific topic. "
        "Where possible, include a simple, relevant example or analogy to aid understanding. "
        "Conclude with a short, thought-provoking question related to the concept "
        "to encourage deeper understanding and critical thinking."
    )

    # Construct the user's message, including optional context
    user_message = f"Explain the concept: '{concept_query}'."
    if subject_context:
        user_message += f" Please explain it in the context of '{subject_context}'."

    try:
        # Make the API call to OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # Using gpt-3.5-turbo for cost-effectiveness and speed.
                                   # You can change this to "gpt-4" if you have access and prefer higher quality.
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7, # Controls creativity. Lower for more direct answers, higher for more varied ones.
            max_tokens=300 # Limits the length of the generated response to keep it concise
        )
        # Extract and return the AI's generated content
        return response.choices[0].message.content.strip()
    except Exception as e:
        # Log any errors that occur during the API call for debugging
        print(f"Error calling OpenAI API: {e}")
        # Provide a user-friendly error message
        return "I apologize, but I couldn't generate an explanation at this moment. Please try again later."

@app.route('/')
def index():
    """
    Renders the main HTML page for the application.
    Flask will look for 'index.html' inside the 'templates' directory.
    """
    return render_template('index.html')

@app.route('/clarify', methods=['POST'])
def clarify():
    """
    API endpoint to receive concept queries from the frontend and return AI explanations.
    It expects a JSON payload with 'query' and optional 'context' fields.
    """
    # Get JSON data from the request body
    data = request.get_json()
    concept_query = data.get('query')
    subject_context = data.get('context', '') # Default to empty string if no context is provided

    # Basic input validation
    if not concept_query:
        # Return a 400 Bad Request error if the concept query is missing
        return jsonify({"error": "Concept query is required."}), 400

    # Call the core function to get the AI explanation
    explanation = clarify_concept(concept_query, subject_context)
    
    # Return the explanation as a JSON response
    return jsonify({"explanation": explanation})

if __name__ == '__main__':
    # Ensure the 'templates' directory exists for Flask to find index.html
    os.makedirs('templates', exist_ok=True)
    
    # This block is for convenience: it writes the index.html content
    # directly into 'templates/index.html' when app.py is run.
    # In a real project, you'd typically create index.html manually.
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Edwisely Concept Clarifier</title>
    <!-- Tailwind CSS CDN for easy styling -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Google Font: Inter -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        /* Custom CSS for a clean and modern look */
        body {
            font-family: 'Inter', sans-serif;
            background-color: #f0f2f5; /* Light gray background */
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh; /* Full viewport height */
            padding: 1rem; /* Padding around the content */
        }
        .container {
            background-color: #ffffff; /* White background for the card */
            border-radius: 1rem; /* Rounded corners */
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1); /* Soft shadow */
            padding: 2.5rem;
            max-width: 600px; /* Max width for readability */
            width: 100%; /* Full width on smaller screens */
            text-align: center;
        }
        .input-field {
            width: 100%;
            padding: 0.75rem;
            margin-bottom: 1rem;
            border: 1px solid #d1d5db; /* Light gray border */
            border-radius: 0.5rem;
            font-size: 1rem;
            outline: none; /* Remove default outline on focus */
            transition: border-color 0.2s; /* Smooth transition for focus effect */
        }
        .input-field:focus {
            border-color: #6366f1; /* Tailwind indigo-500 on focus */
        }
        .btn-primary {
            background-color: #6366f1; /* Tailwind indigo-500 */
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 0.5rem;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.2s, transform 0.1s; /* Smooth hover effects */
            border: none;
            width: 100%;
        }
        .btn-primary:hover {
            background-color: #4f46e5; /* Tailwind indigo-600 on hover */
            transform: translateY(-1px); /* Slight lift effect */
        }
        .response-box {
            background-color: #e0e7ff; /* Tailwind indigo-100 */
            border: 1px solid #a5b4fc; /* Tailwind indigo-300 */
            border-radius: 0.75rem;
            padding: 1.5rem;
            margin-top: 1.5rem;
            text-align: left;
            min-height: 100px; /* Minimum height for the response area */
            overflow-y: auto; /* Enable scrolling if content overflows */
            white-space: pre-wrap; /* Preserves whitespace and wraps text */
            word-wrap: break-word; /* Breaks long words to prevent horizontal scroll */
            font-size: 0.95rem;
            color: #1e293b; /* Tailwind slate-800 */
            line-height: 1.6; /* Improved readability */
            position: relative; /* For positioning loading indicator */
        }
        .loading-indicator {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            display: none; /* Hidden by default */
            color: #6366f1; /* Tailwind indigo-500 */
            font-weight: 600;
        }
        .logo {
            width: 80px; /* Adjust size as needed */
            margin-bottom: 1.5rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Placeholder image for a simple logo -->
        <img src="https://placehold.co/80x80/6366f1/ffffff?text=AI" alt="Edwisely AI Logo" class="logo mx-auto">
        <h1 class="text-3xl font-bold text-gray-800 mb-4">Edwisely Concept Clarifier</h1>
        <p class="text-gray-600 mb-6">Get instant, personalized explanations for engineering concepts.</p>

        <!-- Form for user input -->
        <form id="clarifierForm" class="flex flex-col gap-4">
            <input type="text" id="conceptInput" class="input-field" placeholder="Enter engineering concept (e.g., 'Mutex', 'Polymorphism')" required>
            <input type="text" id="contextInput" class="input-field" placeholder="Optional: Subject/Context (e.g., 'Operating Systems')">
            <button type="submit" class="btn-primary">Clarify Concept</button>
        </form>

        <!-- Area to display AI response -->
        <div id="responseBox" class="response-box relative">
            <p id="responseText" class="text-gray-700">Your explanations will appear here.</p>
            <!-- Loading indicator -->
            <div id="loadingIndicator" class="loading-indicator">Loading...</div>
        </div>
    </div>

    <script>
        // Event listener for form submission
        document.getElementById('clarifierForm').addEventListener('submit', async function(event) {
            event.preventDefault(); // Prevent default form submission (page reload)

            // Get references to DOM elements
            const conceptInput = document.getElementById('conceptInput');
            const contextInput = document.getElementById('contextInput');
            const responseText = document.getElementById('responseText');
            const loadingIndicator = document.getElementById('loadingIndicator');
            const submitButton = document.querySelector('.btn-primary');

            // Get trimmed values from input fields
            const concept = conceptInput.value.trim();
            const context = contextInput.value.trim();

            // Basic client-side validation
            if (!concept) {
                responseText.textContent = "Please enter a concept to clarify.";
                return; // Stop execution if no concept is entered
            }

            // UI feedback: Clear previous response, show loading, disable button
            responseText.textContent = ""; 
            loadingIndicator.style.display = 'block'; 
            submitButton.disabled = true; 

            try {
                // Make a POST request to the Flask backend's /clarify endpoint
                const response = await fetch('/clarify', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json', // Specify content type as JSON
                    },
                    // Send the concept and context as a JSON string in the request body
                    body: JSON.stringify({ query: concept, context: context }),
                });

                // Check if the response was successful (status code 2xx)
                if (!response.ok) {
                    // If not successful, parse the error message from the server
                    const errorData = await response.json();
                    throw new Error(errorData.error || 'Something went wrong on the server.');
                }

                // Parse the JSON response from the server
                const data = await response.json();
                // Display the AI's explanation
                responseText.textContent = data.explanation;
            } catch (error) {
                // Handle any errors that occurred during the fetch or processing
                console.error('Error:', error);
                responseText.textContent = `Error: ${error.message}. Please try again.`;
            } finally {
                // UI feedback: Hide loading, re-enable button, regardless of success or failure
                loadingIndicator.style.display = 'none'; 
                submitButton.disabled = false; 
            }
        });
    </script>
</body>
</html>
    """
    with open('templates/index.html', 'w') as f:
        f.write(html_content)

    # Run the Flask application in debug mode (auto-reloads on code changes)
    app.run(debug=True)
