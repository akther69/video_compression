import os
import uuid
import subprocess

from django.shortcuts import render
from django.conf import settings


def upload_video(request):

    download_url = None
    error = None
    success = None

    if request.method == "POST":

        video = request.FILES.get("video")

        if video:

            # 10GB upload limit
            if video.size > 10 * 1024 * 1024 * 1024:

                error = "File size exceeds 10GB"

                return render(request, "upload.html", {
                    "error": error
                })

            try:

                # Generate unique filename
                unique_id = str(uuid.uuid4())

                input_filename = f"{unique_id}_{video.name}"

                input_path = os.path.join(
                    settings.MEDIA_ROOT,
                    "uploads",
                    input_filename
                )

                # Create upload folder
                os.makedirs(
                    os.path.dirname(input_path),
                    exist_ok=True
                )

                # Save uploaded video
                with open(input_path, "wb+") as destination:

                    for chunk in video.chunks():

                        destination.write(chunk)

                # Output filename
                output_filename = (
                    f"compressed_{input_filename}"
                )

                output_path = os.path.join(
                    settings.MEDIA_ROOT,
                    "compressed",
                    output_filename
                )

                # Create compressed folder
                os.makedirs(
                    os.path.dirname(output_path),
                    exist_ok=True
                )

                # FFmpeg path
                ffmpeg_path = "ffmpeg"

                # FFmpeg compression command
                command = [

                    ffmpeg_path,

                    "-i",
                    input_path,

                    "-c:v",
                    "libx265",

                    "-crf",
                    "28",

                    "-preset",
                    "fast",

                    "-c:a",
                    "aac",

                    "-b:a",
                    "96k",

                    output_path
                ]

                # Run FFmpeg
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True
                )

                # Compression failed
                if result.returncode != 0:

                    error = (
                        "Compression failed: "
                        + result.stderr
                    )

                    return render(request, "upload.html", {
                        "error": error
                    })

                # Delete original uploaded file
                if os.path.exists(input_path):

                    os.remove(input_path)

                # Download link
                download_url = (
                    settings.MEDIA_URL
                    + "compressed/"
                    + output_filename
                )

                success = (
                    "Video compressed successfully!"
                )

            except Exception as e:

                error = str(e)

    return render(request, "upload.html", {

        "download_url": download_url,

        "error": error,

        "success": success
    })