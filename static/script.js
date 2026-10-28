class FaceRecognitionApp {
    constructor() {
        this.stream = null;
        this.regVideo = document.getElementById('regVideo');
        this.recVideo = document.getElementById('recVideo');
        this.regCanvas = document.getElementById('regCanvas');
        this.recCanvas = document.getElementById('recCanvas');
        this.regFaceFrame = document.getElementById('regFaceFrame');
        this.recFaceFrame = document.getElementById('recFaceFrame');
        this.regStatus = document.getElementById('regStatus');
        this.recStatus = document.getElementById('recStatus');
        
        this.initializeEventListeners();
        this.initializeFaceDetection();
    }

    initializeEventListeners() {
        // Camera controls
        document.getElementById('startCameraBtn').addEventListener('click', () => this.startCamera());
        document.getElementById('stopCameraBtn').addEventListener('click', () => this.stopCamera());
        
        // Registration
        document.getElementById('regCaptureBtn').addEventListener('click', () => this.captureAndRegister());
        
        // Recognition
        document.getElementById('recCaptureBtn').addEventListener('click', () => this.captureAndRecognize());
        
        // Users list
        document.getElementById('loadUsersBtn').addEventListener('click', () => this.loadUsers());
        
        // Attendance report
        document.getElementById('loadReportBtn').addEventListener('click', () => this.loadAttendanceReport());
    }

    async startCamera() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({ 
                video: { 
                    width: { ideal: 640 },
                    height: { ideal: 480 },
                    facingMode: 'user'
                } 
            });
            
            this.regVideo.srcObject = this.stream;
            this.recVideo.srcObject = this.stream;
            
            document.getElementById('startCameraBtn').disabled = true;
            document.getElementById('stopCameraBtn').disabled = false;
            
            this.showMessage('Camera started successfully!', 'success', 'regMessage');
            this.showMessage('Camera started successfully!', 'success', 'recMessage');
            
        } catch (error) {
            console.error('Error accessing camera:', error);
            this.showMessage('Error accessing camera. Please check permissions.', 'error', 'regMessage');
            this.showMessage('Error accessing camera. Please check permissions.', 'error', 'recMessage');
        }
    }

    stopCamera() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
            
            this.regVideo.srcObject = null;
            this.recVideo.srcObject = null;
            
            document.getElementById('startCameraBtn').disabled = false;
            document.getElementById('stopCameraBtn').disabled = true;
            
            this.showMessage('Camera stopped.', 'info', 'regMessage');
            this.showMessage('Camera stopped.', 'info', 'recMessage');
        }
    }

    initializeFaceDetection() {
        // Start face detection loop for both videos
        this.detectFaceLoop(this.regVideo, this.regFaceFrame, this.regStatus, 'reg');
        this.detectFaceLoop(this.recVideo, this.recFaceFrame, this.recStatus, 'rec');
    }

    async detectFaceLoop(video, faceFrame, statusElement, type) {
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        
        const detectFace = async () => {
            if (video.srcObject && video.readyState === video.HAVE_ENOUGH_DATA) {
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                context.drawImage(video, 0, 0);
                
                try {
                    // Simple face detection using canvas
                    const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
                    const hasFace = this.simpleFaceDetection(imageData);
                    
                    if (hasFace) {
                        faceFrame.style.borderColor = '#48bb78';
                        faceFrame.style.boxShadow = '0 0 20px rgba(72, 187, 120, 0.5)';
                        statusElement.textContent = 'Face Detected! ✅';
                        statusElement.style.color = '#22543d';
                    } else {
                        faceFrame.style.borderColor = '#667eea';
                        faceFrame.style.boxShadow = 'none';
                        statusElement.textContent = type === 'reg' ? 'Position your face in the frame' : 'Position your face for recognition';
                        statusElement.style.color = '#4a5568';
                    }
                } catch (error) {
                    console.error('Face detection error:', error);
                }
            }
            
            requestAnimationFrame(detectFace);
        };
        
        detectFace();
    }

    simpleFaceDetection(imageData) {
        // Simple skin tone detection as a basic face indicator
        const data = imageData.data;
        let skinPixels = 0;
        let totalPixels = data.length / 4;
        
        for (let i = 0; i < data.length; i += 4) {
            const r = data[i];
            const g = data[i + 1];
            const b = data[i + 2];
            
            // Basic skin tone detection
            if (r > 95 && g > 40 && b > 20 && 
                Math.max(r, g, b) - Math.min(r, g, b) > 15 &&
                Math.abs(r - g) > 15 && r > g && r > b) {
                skinPixels++;
            }
        }
        
        const skinRatio = skinPixels / totalPixels;
        return skinRatio > 0.1; // If more than 10% of pixels are skin-like
    }

    async captureAndRegister() {
        const name = document.getElementById('regName').value.trim();
        const userId = document.getElementById('regUserId').value.trim();
        
        if (!name || !userId) {
            this.showMessage('Please enter both name and user ID.', 'error', 'regMessage');
            return;
        }
        
        if (!this.stream) {
            this.showMessage('Please start the camera first.', 'error', 'regMessage');
            return;
        }
        
        try {
            this.showMessage('Processing...', 'info', 'regMessage');
            
            const imageData = await this.captureImage(this.regVideo, this.regCanvas);
            
            const response = await fetch('/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name: name,
                    user_id: userId,
                    image: imageData
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showMessage(result.message, 'success', 'regMessage');
                document.getElementById('regName').value = '';
                document.getElementById('regUserId').value = '';
                
                // Add success animation
                this.regFaceFrame.classList.add('success-animation');
                setTimeout(() => this.regFaceFrame.classList.remove('success-animation'), 600);
                
                // Auto-refresh users list
                setTimeout(() => this.loadUsers(), 1000);
                
            } else {
                this.showMessage(result.message, 'error', 'regMessage');
            }
            
        } catch (error) {
            console.error('Registration error:', error);
            this.showMessage('Error during registration. Please try again.', 'error', 'regMessage');
        }
    }

    async captureAndRecognize() {
        if (!this.stream) {
            this.showMessage('Please start the camera first.', 'error', 'recMessage');
            return;
        }
        
        try {
            this.showMessage('Processing...', 'info', 'recMessage');
            
            const imageData = await this.captureImage(this.recVideo, this.recCanvas);
            
            const response = await fetch('/recognize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    image: imageData
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showMessage(result.message, 'success', 'recMessage');
                
                // Add success animation
                this.recFaceFrame.classList.add('success-animation');
                setTimeout(() => this.recFaceFrame.classList.remove('success-animation'), 600);
                
                // Update status with recognized user info
                this.recStatus.innerHTML = `
                    <div style="background: #c6f6d5; padding: 10px; border-radius: 8px; margin-top: 10px;">
                        <strong>${result.name}</strong><br>
                        ID: ${result.user_id}<br>
                        ${result.attendance_type.replace('_', ' ').toUpperCase()}
                    </div>
                `;
                
                // Auto-refresh attendance report
                setTimeout(() => this.loadAttendanceReport(), 1000);
                
            } else {
                this.showMessage(result.message, 'error', 'recMessage');
            }
            
        } catch (error) {
            console.error('Recognition error:', error);
            this.showMessage('Error during recognition. Please try again.', 'error', 'recMessage');
        }
    }

    async captureImage(video, canvas) {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const context = canvas.getContext('2d');
        context.drawImage(video, 0, 0);
        return canvas.toDataURL('image/jpeg', 0.8);
    }

    async loadUsers() {
        try {
            const response = await fetch('/users');
            const result = await response.json();
            
            if (result.success) {
                this.displayUsers(result.users);
            } else {
                console.error('Failed to load users');
            }
        } catch (error) {
            console.error('Error loading users:', error);
        }
    }

    displayUsers(users) {
        const usersList = document.getElementById('usersList');
        usersList.innerHTML = '';
        
        if (users.length === 0) {
            usersList.innerHTML = '<div style="text-align: center; padding: 20px; color: #718096;">No users registered yet</div>';
            return;
        }
        
        users.forEach(user => {
            const userCard = document.createElement('div');
            userCard.className = 'user-card';
            
            // Get initials for avatar
            const initials = user.name.split(' ').map(n => n[0]).join('').toUpperCase();
            
            userCard.innerHTML = `
                <div class="user-avatar">${initials}</div>
                <div class="user-info">
                    <div class="user-name">${user.name}</div>
                    <div class="user-id">ID: ${user.user_id}</div>
                    <div class="user-date">Registered: ${this.formatDateTime(user.created_at)}</div>
                </div>
                <div class="user-actions">
                    <button class="user-action-btn edit" onclick="editUser('${user.user_id}')">✏️ Edit</button>
                    <button class="user-action-btn delete" onclick="deleteUser('${user.user_id}')">🗑️ Delete</button>
                </div>
            `;
            
            usersList.appendChild(userCard);
        });
    }

    async loadAttendanceReport() {
        try {
            const response = await fetch('/attendance_report');
            const result = await response.json();
            
            if (result.success) {
                this.displayAttendanceReport(result.records);
            } else {
                console.error('Failed to load attendance report');
            }
        } catch (error) {
            console.error('Error loading attendance report:', error);
        }
    }

    displayAttendanceReport(records) {
        const tbody = document.getElementById('attendanceBody');
        tbody.innerHTML = '';
        
        if (records.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; padding: 20px;">No attendance records found</td></tr>';
            return;
        }
        
        records.forEach(record => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${record.name}</td>
                <td>${record.user_id}</td>
                <td>${this.formatDateTime(record.check_in)}</td>
                <td>${record.check_out ? this.formatDateTime(record.check_out) : '-'}</td>
            `;
            tbody.appendChild(row);
        });
    }

    formatDateTime(dateTimeStr) {
        if (!dateTimeStr) return '-';
        const date = new Date(dateTimeStr);
        return date.toLocaleString();
    }

    showMessage(message, type, elementId) {
        const element = document.getElementById(elementId);
        element.textContent = message;
        element.className = `message ${type}`;
        
        // Auto-clear info messages after 3 seconds
        if (type === 'info') {
            setTimeout(() => {
                if (element.textContent === message) {
                    element.textContent = '';
                    element.className = 'message';
                }
            }, 3000);
        }
    }
}

// Global functions for user actions
async function editUser(userId) {
    // TODO: Implement edit functionality
    alert(`Edit user ${userId} - Feature coming soon!`);
}

async function deleteUser(userId) {
    if (confirm(`Are you sure you want to delete user ${userId}? This will also remove all attendance records for this user.`)) {
        try {
            const response = await fetch(`/users/${userId}`, {
                method: 'DELETE'
            });
            
            const result = await response.json();
            
            if (result.success) {
                alert(`User ${userId} deleted successfully!`);
                // Refresh the users list and attendance report
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                alert(`Error: ${result.message}`);
            }
        } catch (error) {
            console.error('Error deleting user:', error);
            alert('Error deleting user. Please try again.');
        }
    }
}

// Initialize the app when the page loads
document.addEventListener('DOMContentLoaded', () => {
    const app = new FaceRecognitionApp();
    
    // Add some initial styling
    document.body.style.opacity = '0';
    document.body.style.transition = 'opacity 0.5s ease-in';
    
    setTimeout(() => {
        document.body.style.opacity = '1';
        // Auto-load users list and attendance report
        app.loadUsers();
        app.loadAttendanceReport();
    }, 100);
});
