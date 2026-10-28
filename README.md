# Face Recognition Attendance System

A modern web-based face recognition attendance system built with Python Flask backend, HTML/CSS/JavaScript frontend, and SQLite database.

## Features

- **User Registration**: Register new users with name, ID, and face encoding
- **Face Recognition**: Real-time face detection and recognition
- **Attendance Tracking**: Automatic check-in/check-out system
- **Attendance Reports**: View attendance history and reports
- **Modern UI**: Clean, responsive design with animations
- **Webcam Integration**: Uses device camera for face capture

## Technology Stack

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Database**: SQLite
- **Face Recognition**: OpenCV + face_recognition library
- **Image Processing**: PIL (Pillow)

## Installation

### Prerequisites

- Python 3.7 or higher
- Webcam-enabled device
- Modern web browser with camera permissions

### Setup

1. **Clone or download the project files**

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser and navigate to**
   ```
   http://localhost:5000
   ```

## Usage

### 1. Start Camera
- Click the "🎥 Start Camera" button to enable webcam access
- Allow camera permissions when prompted by your browser

### 2. User Registration
- Enter the user's full name and ID
- Position the face in the circular frame
- Click "📸 Capture & Register" to save the user

### 3. Face Recognition
- Position your face in the recognition frame
- Click "🔍 Recognize Face" to identify the user
- The system will automatically mark attendance (check-in/check-out)

### 4. Attendance Reports
- Click "📋 Load Report" to view attendance history
- Reports show check-in and check-out times for all users

## File Structure

```
face-recognition-attendance/
├── app.py                 # Flask backend application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/
│   └── index.html        # Main HTML template
├── static/
│   ├── style.css         # CSS styles and animations
│   └── script.js         # JavaScript functionality
└── attendance.db         # SQLite database (created automatically)
```

## API Endpoints

- `GET /` - Main application page
- `POST /register` - Register new user with face
- `POST /recognize` - Recognize face and mark attendance
- `GET /attendance_report` - Get attendance records

## Database Schema

### Users Table
- `id`: Primary key
- `name`: User's full name
- `user_id`: Unique user identifier
- `face_encoding`: Encoded face data
- `created_at`: Registration timestamp

### Attendance Table
- `id`: Primary key
- `user_id`: Reference to user
- `name`: User's name
- `check_in`: Check-in timestamp
- `check_out`: Check-out timestamp

## Features in Detail

### Face Detection
- Real-time face detection using webcam
- Visual feedback with animated face frame
- Status indicators for face positioning

### Face Recognition
- Robust face encoding using face_recognition library
- Tolerance-based matching for accuracy
- Automatic attendance marking

### User Interface
- Responsive grid layout
- Modern gradient design
- Smooth animations and transitions
- Real-time status updates

### Security Features
- Face encoding storage (not raw images)
- User ID validation
- Duplicate prevention

## Troubleshooting

### Camera Issues
- Ensure camera permissions are granted
- Check if another application is using the camera
- Try refreshing the page and granting permissions again

### Installation Issues
- Make sure Python 3.7+ is installed
- Use virtual environment to avoid package conflicts
- Install Visual Studio Build Tools on Windows if needed

### Performance Issues
- Close other applications using the camera
- Ensure good lighting for face detection
- Check browser console for error messages

## Browser Compatibility

- Chrome 60+
- Firefox 55+
- Safari 11+
- Edge 79+

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the system.

## License

This project is open source and available under the MIT License.

## Support

For technical support or questions, please check the troubleshooting section or create an issue in the project repository.


