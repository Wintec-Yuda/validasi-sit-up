from flask import Flask, redirect, url_for, render_template, Response, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import time
import mediapipe as mp
from functions import *

app = Flask(__name__)
# CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/sit_up'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(50), nullable=False)
    waktu = db.Column(db.Time, nullable=False)
    jumlah = db.Column(db.Integer, nullable=False)

def gen(file_path, realtime=False, upload=False, nama=None, waktu=None):
    if file_path == '0':
        file_path = int(file_path)

    cap = cv2.VideoCapture(file_path)

    pTime = 0
    situp_count = 0
    start_situp = False
    end_situp = False
    point_11 = point_23 = point_25 = point_27 = None
    start_time = time.time()
    initial_position_verified = False

    if upload:
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        video_duration = total_frames / fps
        waktu = int(video_duration)

    while True:
        success, img = cap.read()

        if not success or img is None:
            break

        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(imgRGB)

        if results.pose_landmarks:
            mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)

            point_11, point_23, point_25, point_27, cx, cy = draw_landmark_points(img, results.pose_landmarks.landmark)

            # Menghitung besar sudut antara tiga titik
            if 'point_11' in locals() and 'point_23' in locals() and 'point_25' in locals():
                angle_23 = calculate_angle(point_11, point_23, point_25)
                cv2.putText(img, f"{round(angle_23, 2)}", (point_23[0] + 20, point_23[1] - 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, green, 2)

            if 'point_23' in locals() and 'point_25' in locals() and 'point_27' in locals():
                angle_25 = calculate_angle(point_23, point_25, point_27)
                cv2.putText(img, f"{round(angle_25, 2)}", (point_25[0] + 20, point_25[1] - 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, green, 2)

                if not initial_position_verified:
                    # Validasi posisi awal sit up
                        if validate_initial_position(angle_23, angle_25):
                            draw_correct_position(img)
                            initial_position_verified = True
                            start_situp = True
                        else:
                            draw_wrong_position(img)
                            initial_position_verified = False
                else:
                    # Cek perubahan sudut dan hitung sit-up
                    if validate_initial_sit_up(angle_25, initial_position_verified):
                        draw_correct_position(img)
                        if angle_23 < 60:
                            end_situp = True
                        if start_situp and end_situp:
                            situp_count += 1
                            start_situp = False
                            end_situp = False
                        if angle_23 > 130:
                            start_situp = True
                    else:
                        draw_wrong_position(img)
                        initial_position_verified = False

            img = cv2.line(img, (cx, cy - 20), (cx, cy + 20), green, 1)
            img = cv2.line(img, (cx - 20, cy), (cx + 20, cy), green, 1)

        elapsed_time = time.time() - start_time
        # menghitung mundur waktu
        if realtime or upload:
            remaining_time = max(0, waktu - elapsed_time)
            draw_remaining_time(img, remaining_time)

            if remaining_time <= 0:
                # Save data to the User table
                with app.app_context():
                    user = User(nama=nama, waktu=waktu, jumlah=situp_count)
                    db.session.add(user)
                    db.session.commit()
                break

        # cetak jumlah sit up
        draw_count_sit_up(img, situp_count)

        ret, jpeg = cv2.imencode('.jpg', img)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/latihan')
def latihan():
    return render_template('latihan.html')

@app.route('/peringkat')
def peringkat():
    users = User.query.order_by(User.id.desc()).all()
    return render_template('peringkat.html', users=users)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    nama = request.form['nama']
    if file.filename == '':
        return redirect(request.url)

    old_file_path = request.args.get('file_path', None)

    if old_file_path:
        try:
            os.remove(old_file_path)
        except OSError as e:
            print(f"Error deleting old file: {e}")

    file_path = "temp_video.mp4"
    file.save(file_path)

    return {'file_path': file_path, 'nama': nama}

@app.route('/video_feed_upload')
def video_feed_upload():
    file_path = request.args.get('file_path', '0')
    nama = request.args.get('nama', 'Anonymous')
    return Response(gen(file_path, upload=True, nama=nama), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed')
def video_feed():
    return Response(gen(0), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_realtime')
def video_feed_realtime():
    nama = request.args.get('nama', 'Anonymous')
    waktu = request.args.get('waktu', 60)
    return Response(gen(0, realtime=True, nama=nama, waktu=int(waktu)), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
