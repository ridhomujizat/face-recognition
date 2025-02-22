import io
import base64
import numpy as np
from PIL import Image, ImageOps
from flask import Flask, jsonify, request
import requests
import face_recognition
app = Flask(__name__)

def url_to_base64(url):
    """
    Function to convert URL to base64 string
    """
    try:
        response = requests.get(url)
        if response.status_code == 200:
            image_bytes = response.content
            base64_string = base64.b64encode(image_bytes).decode('utf-8')
            return base64_string
        return None
    except Exception as e:
        print("Error converting URL to base64:", e)
        return None

def decode_image(image_base64):
    """
    Function to decode image from Base64 to numpy array
    """
    try:
        image_bytes = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_bytes))
        # Convert image format to RGB (if image is in RGBA or grayscale)
        image = ImageOps.exif_transpose(image)
        image = image.convert('RGB')
        
        # max_size = 1000
        # if max(image.size) > max_size:
        #     image.thumbnail((max_size, max_size), Image.LANCZOS)
        
        return np.array(image)
    except Exception as e:
        print("Error decoding image:", e)
        return None



@app.route("/api")
def api():
    # Sample JSON response
    data = {
        "message": "Hello, this is the API response!",
        "status": "success"
    }
    return jsonify(data)


@app.route('/verify', methods=['POST'])
def verify():

    
    data = request.get_json()

    # Get the array of verification faces from request
    verif_face = data.get('verif_face', [])
    if not verif_face:
        return jsonify({'error': 'Field "verif_face" must be provided'}), 400
    
    # Validate that verif_face is a list
    if not isinstance(verif_face, list):
        return jsonify({'error': 'verif_face must be an array of URLs'}), 400

    if not data:
        return jsonify({'error': 'No input data provided'}), 400
    
    image_data = data.get('image')

    if not image_data:
        return jsonify({'error': 'Field "name" dan "image" harus disediakan'}), 400
    
    image = url_to_base64(image_data)
    if image is None:
        return jsonify({'error': 'Gambar tidak valid'}), 400
    

    # Decode the input image
    unknown_face = decode_image(image)
    if unknown_face is None:
        return jsonify({'error': 'Cannot decode input image'}), 400

    # Get face encodings for unknown face
    unknown_face_encodings = face_recognition.face_encodings(unknown_face)
    if not unknown_face_encodings:
        return jsonify({'error': 'No face found in input image'}), 400

    # match = False
    # Compare with each Ronaldo image
    similarity_list = []
    compare_list = []
    for face_url in verif_face:
        face_base64 = url_to_base64(face_url)
        if face_base64:
            face_image = decode_image(face_base64)
            if face_image is not None:
                face_encodings = face_recognition.face_encodings(face_image)
                if face_encodings:
                    # Compare faces
                    results = face_recognition.compare_faces([face_encodings[0]], unknown_face_encodings[0], tolerance=0.5)  # More strict matching
                    compare_list.append(True if results[0] else False)
                                        # Get face distance (lower means more similar)
                    face_distances = face_recognition.face_distance([face_encodings[0]], unknown_face_encodings[0])
                    # Convert distance to similarity score (1 - distance)
                    similarity = 1 - face_distances[0]
                    similarity_list.append(similarity)

    
    average_similarity = sum(similarity_list) / len(similarity_list) if similarity_list else 0.0

    # Determine valid: true if there are more True values than False values in compare_list
    valid = compare_list.count(True) > compare_list.count(False) if compare_list else False
 
    return jsonify({
        'match': {
            'similarity': average_similarity,
            'valid': valid
        },
        'similarity': similarity_list,
        'compare': compare_list
    }), 200   