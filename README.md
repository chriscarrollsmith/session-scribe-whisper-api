# Fast Audio/Video transcribe using Openai's Whisper and Modal

## Powered by Modal.com for parallel processing on-demand, an hour audio file can be transcribed in ~1 minute.

"Modal’s dead-simple parallelism primitives are the key to doing the transcription so quickly. Even with a GPU, transcribing a full episode serially was taking around 10 minutes. But by pulling in ffmpeg with a simple .pip_install("ffmpeg-python") addition to our Modal Image, we could exploit the natural silences of the podcast medium to partition episodes into hundreds of short segments. Each segment is transcribed by Whisper in its own container task with 2 physical CPU cores, and when all are done we stitch the segments back together with only a minimal loss in transcription quality. This approach actually accords quite well with Whisper’s model architecture." The model uses 30-second chunking.

## How to develop

1. Create a Modal account and get your API key.

   - Run this command to install modal client and generate token.

     ```bash
     pip install modal-client
     modal token new
     ```

     - The first command will install the Modal client library on your computer, along with its dependencies.

     - The second command creates an API token by authenticating through your web browser. It will open a new tab, but you can close it when you are done.

2. Deploy your modal project with the following command.

   ```bash
   modal deploy api.main
   ```

### To-do items

- [x] I want to do some pseudocode and some refactoring to make this more maintainable
- [x] Make sure old imports from config.py now point to constants.py or logger.py
- [ ] Implement an outgoing API endpoint here to ping a Vercel webhook when transcription is complete.
- [ ] Make it optional to split the audio before transcribing, so we can compare transcription quality with and without splitting.
- [ ] Explore using an LLM to format and clean up the outputs for printing.
- [ ] Save the audio files in Google Cloud so we can serve them for download (if an event organizer chooses to do that).
- [ ] Investigate other models or Whisper extensions that allow for time-stamping and diarization (i.e., speaker identification). In particular, see [WhisperX](https://github.com/m-bain/whisperX). Also look at [pyannote](https://github.com/pyannote/pyannote-audio) (tutorial on pyannote diarization [here](https://lablab.ai/t/whisper-transcription-and-speaker-identification)).

## How to use

1. Transcribe your audio file using the following curl command. The 'transcribe' endpoint wants a JSON formatted request:

  ```curl
  curl --location --request POST 'https://chriscarrollsmith--whisper-audio-video-transcriber-api-v-4c6a21.modal.run/api/transcribe' \
  --header 'Content-Type: application/json' \
  --data-raw '{
      "src_url": "https://storage.googleapis.com/session-scribe-bucket/disciple.wav",
      "unique_id": 987654,
      "session_title": "Session Title Here",
      "presenters": "Presenters Here",
      "is_video": false
  }'
  ```

   Sample response:

   ```json
   {
     "job_id": "your-job-id"
   }
   ```
