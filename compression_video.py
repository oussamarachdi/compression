from flask import Flask, request, jsonify, send_file
from flask_uploads import UploadSet, configure_uploads, ALL
from moviepy.editor import VideoFileClip
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

videos = UploadSet("videos", ALL)
app.config["UPLOADED_VIDEOS_DEST"] = "uploads"
configure_uploads(app, videos)

def compress_video(input_path, output_path):
    # Use moviepy to compress the video
    video = VideoFileClip(input_path)
    video.write_videofile(output_path, codec="libx265", audio_codec="aac", preset="ultrafast", threads=4)
    video.close()

@app.route("/compress_video", methods=["POST"])
def compress_video_endpoint():
    if "video" not in request.files:
        return jsonify({"error": "No video provided"}), 400

    video = request.files["video"]

    if video.filename == "":
        return jsonify({"error": "No selected video"}), 400

    try:
        # Save the uploaded video temporarily
        video_path = os.path.join("uploads", video.filename)
        video.save(video_path)

        # Compress the video
        compressed_path = os.path.join("uploads", "temp_compressed.mp4")
        compress_video(video_path, compressed_path)

        # Read the compressed video
        with open(compressed_path, "rb") as compressed_file:
            compressed_data = compressed_file.read()

        return compressed_data, 200, {"Content-Type": "video/mp4", "Content-Disposition": "inline; filename=compressed.mp4"}

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # Clean up temporary files
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(compressed_path):
            os.remove(compressed_path)

if __name__ == "__main__":
    app.run(debug=True)
