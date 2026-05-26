import os
import re
import uuid
import threading
import subprocess

from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings


compression_progress = {}

download_links = {}


def home(request):

    return render(request, "upload.html")


def get_video_duration(input_path):

    command = [
        "ffmpeg",
        "-i",
        input_path
    ]

    result = subprocess.run(
        command,
        stderr=subprocess.PIPE,
        text=True
    )

    output = result.stderr

    duration_match = re.search(
        r"Duration: (\d+):(\d+):(\d+\.\d+)",
        output
    )

    if duration_match:

        hours = int(duration_match.group(1))
        minutes = int(duration_match.group(2))
        seconds = float(duration_match.group(3))

        total_seconds = (
            hours * 3600
            + minutes * 60
            + seconds
        )

        return total_seconds

    return 0


def compress_video_background(
    task_id,
    input_path,
    output_path,
    output_filename
):

    total_duration = get_video_duration(
        input_path
    )

    command = [

        "ffmpeg",

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

    process = subprocess.Popen(

        command,

        stderr=subprocess.PIPE,

        universal_newlines=True
    )

    for line in process.stderr:

        time_match = re.search(
            r"time=(\d+):(\d+):(\d+\.\d+)",
            line
        )

        if time_match:

            hours = int(time_match.group(1))
            minutes = int(time_match.group(2))
            seconds = float(time_match.group(3))

            current_seconds = (
                hours * 3600
                + minutes * 60
                + seconds
            )

            percentage = int(
                (
                    current_seconds
                    / total_duration
                ) * 100
            )

            compression_progress[
                task_id
            ] = percentage

    process.wait()

    compression_progress[
        task_id
    ] = 100

    download_links[task_id] = (
        settings.MEDIA_URL
        + "compressed/"
        + output_filename
    )

    if os.path.exists(input_path):

        os.remove(input_path)


def compress_video(request):

    if request.method == "POST":

        video = request.FILES.get("video")

        if not video:

            return JsonResponse({
                "error": "No video uploaded"
            })

        task_id = str(uuid.uuid4())

        input_filename = (
            f"{task_id}_{video.name}"
        )

        input_path = os.path.join(
            settings.MEDIA_ROOT,
            "uploads",
            input_filename
        )

        os.makedirs(
            os.path.dirname(input_path),
            exist_ok=True
        )

        with open(input_path, "wb+") as destination:

            for chunk in video.chunks():

                destination.write(chunk)

        output_filename = (
            f"compressed_{input_filename}"
        )

        output_path = os.path.join(
            settings.MEDIA_ROOT,
            "compressed",
            output_filename
        )

        os.makedirs(
            os.path.dirname(output_path),
            exist_ok=True
        )

        compression_progress[
            task_id
        ] = 0

        # START BACKGROUND THREAD
        thread = threading.Thread(

            target=compress_video_background,

            args=(
                task_id,
                input_path,
                output_path,
                output_filename
            )
        )

        thread.start()

        return JsonResponse({

            "task_id": task_id
        })

    return JsonResponse({
        "error": "Invalid request"
    })


def get_progress(request, task_id):

    progress = compression_progress.get(
        task_id,
        0
    )

    download_url = download_links.get(
        task_id,
        None
    )

    return JsonResponse({

        "progress": progress,

        "download_url": download_url
    })