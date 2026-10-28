from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import cv2
import numpy as np
import sqlite3
import os
from datetime import datetime
import base64
from PIL import Image
import io
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Load OpenCV's pre-trained face detection model
try:
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    if face_cascade.empty():
        raise Exception("Failed to load face detection model")
    logger.info("Face detection model loaded successfully")
except Exception as e:
    logger.error(f"Error loading face detection model: {e}")
    face_cascade = None

# Database initialization
def init_db():
    try:
        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                user_id TEXT UNIQUE NOT NULL,
                face_features TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create attendance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                check_in TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                check_out TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        raise

# Initialize database
init_db()

def extract_face_features(image_array):
    """Extract simple face features using OpenCV"""
    try:
        if face_cascade is None:
            logger.error("Face detection model not loaded")
            return None
            
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            return None
        
        # Get the first detected face
        x, y, w, h = faces[0]
        face_roi = gray[y:y+h, x:x+w]
        
        # Resize to standard size for comparison
        face_roi = cv2.resize(face_roi, (64, 64))
        
        # Normalize and flatten
        face_features = face_roi.flatten() / 255.0
        
        return face_features
        
    except Exception as e:
        logger.error(f"Error extracting face features: {e}")
        return None

def compare_faces(features1, features2, threshold=0.8):
    """Compare two face feature vectors using cosine similarity"""
    try:
        if features1 is None or features2 is None:
            return False
        
        # Calculate cosine similarity
        dot_product = np.dot(features1, features2)
        norm1 = np.linalg.norm(features1)
        norm2 = np.linalg.norm(features2)
        
        if norm1 == 0 or norm2 == 0:
            return False
        
        similarity = dot_product / (norm1 * norm2)
        return similarity > threshold
        
    except Exception as e:
        logger.error(f"Error comparing faces: {e}")
        return False

@app.route('/')
def index():
    """Main application page"""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        user_count = cursor.fetchone()[0]
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'users_registered': user_count,
            'face_model_loaded': face_cascade is not None
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/register', methods=['POST'])
def register():
    """Register a new user with face data"""
    try:
        data = request.json
        if not data or 'name' not in data or 'user_id' not in data or 'image' not in data:
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        name = data['name'].strip()
        user_id = data['user_id'].strip()
        image_data = data['image']
        
        # Validate input
        if not name or not user_id:
            return jsonify({'success': False, 'message': 'Name and User ID cannot be empty'}), 400
        
        # Decode base64 image
        try:
            image_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            image_array = np.array(image)
        except Exception as e:
            return jsonify({'success': False, 'message': 'Invalid image data'}), 400
        
        # Extract face features
        face_features = extract_face_features(image_array)
        if face_features is None:
            return jsonify({'success': False, 'message': 'No face detected in the image'}), 400
        
        # Convert features to string for storage
        features_str = base64.b64encode(face_features.tobytes()).decode('utf-8')
        
        # Store in database
        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute('SELECT id FROM users WHERE user_id = ?', (user_id,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'message': 'User ID already exists'}), 400
        
        cursor.execute('INSERT INTO users (name, user_id, face_features) VALUES (?, ?, ?)',
                      (name, user_id, features_str))
        conn.commit()
        conn.close()
        
        logger.info(f"User registered successfully: {name} ({user_id})")
        return jsonify({'success': True, 'message': 'User registered successfully'})
        
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'User ID already exists'}), 400
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@app.route('/recognize', methods=['POST'])
def recognize():
    """Recognize a face and mark attendance"""
    try:
        data = request.json
        if not data or 'image' not in data:
            return jsonify({'success': False, 'message': 'Missing image data'}), 400
        
        image_data = data['image']
        
        # Decode base64 image
        try:
            image_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            image_array = np.array(image)
        except Exception as e:
            return jsonify({'success': False, 'message': 'Invalid image data'}), 400
        
        # Extract face features
        face_features = extract_face_features(image_array)
        if face_features is None:
            return jsonify({'success': False, 'message': 'No face detected'}), 400
        
        # Get all stored face features
        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()
        cursor.execute('SELECT name, user_id, face_features FROM users')
        stored_users = cursor.fetchall()
        conn.close()
        
        if not stored_users:
            return jsonify({'success': False, 'message': 'No users registered'}), 400
        
        # Compare with stored features
        for name, user_id, stored_features_str in stored_users:
            try:
                stored_features = np.frombuffer(base64.b64decode(stored_features_str), dtype=np.float64)
                
                # Compare faces
                if compare_faces(face_features, stored_features):
                    # Mark attendance
                    conn = sqlite3.connect('attendance.db')
                    cursor = conn.cursor()
                    
                    # Check if already checked in today
                    today = datetime.now().strftime('%Y-%m-%d')
                    cursor.execute('''
                        SELECT id FROM attendance 
                        WHERE user_id = ? AND DATE(check_in) = ? AND check_out IS NULL
                    ''', (user_id, today))
                    
                    existing_attendance = cursor.fetchone()
                    
                    if existing_attendance:
                        # Check out
                        cursor.execute('''
                            UPDATE attendance 
                            SET check_out = CURRENT_TIMESTAMP 
                            WHERE id = ?
                        ''', (existing_attendance[0],))
                        attendance_type = 'check_out'
                    else:
                        # Check in
                        cursor.execute('''
                            INSERT INTO attendance (user_id, name, check_in) 
                            VALUES (?, ?, CURRENT_TIMESTAMP)
                        ''', (user_id, name))
                        attendance_type = 'check_in'
                    
                    conn.commit()
                    conn.close()
                    
                    logger.info(f"Attendance marked: {name} ({user_id}) - {attendance_type}")
                    return jsonify({
                        'success': True,
                        'name': name,
                        'user_id': user_id,
                        'attendance_type': attendance_type,
                        'message': f'Welcome {name}! {attendance_type.replace("_", " ").title()} recorded.'
                    })
                    
            except Exception as e:
                logger.error(f"Error processing user {user_id}: {e}")
                continue
        
        return jsonify({'success': False, 'message': 'Face not recognized'}), 400
        
    except Exception as e:
        logger.error(f"Recognition error: {e}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@app.route('/users')
def get_users():
    """Get all registered users"""
    try:
        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, user_id, created_at 
            FROM users 
            ORDER BY created_at DESC
        ''')
        users = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'users': [
                {
                    'id': user[0],
                    'name': user[1],
                    'user_id': user[2],
                    'created_at': user[3]
                }
                for user in users
            ]
        })
        
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@app.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a registered user"""
    try:
        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()
        
        # First delete attendance records for this user
        cursor.execute('DELETE FROM attendance WHERE user_id = ?', (user_id,))
        attendance_deleted = cursor.rowcount
        
        # Then delete the user
        cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
        user_deleted = cursor.rowcount
        
        if user_deleted > 0:
            conn.commit()
            conn.close()
            logger.info(f"User deleted: {user_id} (attendance records: {attendance_deleted})")
            return jsonify({'success': True, 'message': f'User {user_id} deleted successfully'})
        else:
            conn.close()
            return jsonify({'success': False, 'message': f'User {user_id} not found'}), 404
        
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@app.route('/attendance_report')
def attendance_report():
    """Get attendance report"""
    try:
        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT name, user_id, check_in, check_out 
            FROM attendance 
            ORDER BY check_in DESC 
            LIMIT 50
        ''')
        attendance_records = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'records': [
                {
                    'name': record[0],
                    'user_id': record[1],
                    'check_in': record[2],
                    'check_out': record[3]
                }
                for record in attendance_records
            ]
        })
        
    except Exception as e:
        logger.error(f"Error getting attendance report: {e}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'message': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'message': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("Starting Face Recognition Attendance System...")
    logger.info("Database initialized and ready")
    logger.info("Face detection model status: " + ("Loaded" if face_cascade else "Failed to load"))
    
    try:
        app.run(debug=True, host='127.0.0.1', port=5000)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
