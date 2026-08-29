from faster_whisper import WhisperModel
from fastapi import UploadFile
import tempfile
import os


# Load Whisper model only once when the application starts
model = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8"
)


async def transcribe_audio(file: UploadFile) -> str:
    """
    Convert an uploaded audio/video recording into text.
    """

    # Create a temporary file
    suffix = os.path.splitext(file.filename or "")[1] or ".wav"

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    ) as temp_file:

        audio_data = await file.read()
        temp_file.write(audio_data)
        temp_file_path = temp_file.name

    try:
        # Transcribe audio
        segments, info = model.transcribe(
            temp_file_path,
            beam_size=5,
            vad_filter=True
        )

        # Combine all segments into one transcript
        transcript = " ".join(
            segment.text.strip()
            for segment in segments
        )

        return transcript.strip()

    finally:
        # Delete temporary audio file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

            