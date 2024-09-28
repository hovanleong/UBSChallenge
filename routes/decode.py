from flask import Flask, jsonify
import base64
import re

from routes import app

@app.route('/ub5-flags', methods=['GET'])
def get_flags():
    # Simulated output content (replace with the actual output)
    output = "Some text UB5{dzNsYzBtM183MF9jN2ZfTjB0dHlCMDE=} more text"

    # Regular expression to find the flag
    match = re.search(r'UB5{(.*?)}', output)
    
    if match:
        # Extract the base64 content
        base64_content = match.group(1)
        
        # Decode the base64 content
        decoded_content = base64.b64decode(base64_content).decode('utf-8')
        
        # Create the JSON response
        response = {
            "sanityScroll": {
                "flag": f"UB5{{{decoded_content}}}"
            }
        }
        
        return jsonify(response), 200
    else:
        return jsonify({"error": "Flag not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
