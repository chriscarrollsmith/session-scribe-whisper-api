# Fast Audio/Video transcribe using Openai's Whisper and Modal

## Powered by Modal.com for parallel processing on-demand, an hour audio file can be transcribed in ~1 minute.

"Modal’s dead-simple parallelism primitives are the key to doing the transcription so quickly. Even with a GPU, transcribing a full episode serially was taking around 10 minutes. But by pulling in ffmpeg with a simple .pip_install("ffmpeg-python") addition to our Modal Image, we could exploit the natural silences of the podcast medium to partition episodes into hundreds of short segments. Each segment is transcribed by Whisper in its own container task with 2 physical CPU cores, and when all are done we stitch the segments back together with only a minimal loss in transcription quality. This approach actually accords quite well with Whisper’s model architecture:"

> “The Whisper architecture is a simple end-to-end approach, implemented as an encoder-decoder Transformer. Input audio is split into 30-second chunks, converted into a log-Mel spectrogram, and then passed into an encoder.” - Introducing Whisper

### How to use

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

3. Transcribe your audio file using the following curl commands. Right now only the URL-formatted version is supported.

  ```curl
  curl --location --request POST 'https://chriscarrollsmith--whisper-audio-video-transcriber-api-v-4c6a21.modal.run/api/transcribe' \
  --header 'Content-Type: application/json' \
  --data-raw '{
      "src_url": "https://storage.googleapis.com/session-scribe-bucket/disciple.wav",
      "unique_id": 123456,
      "session_title": "Session Title Here",
      "presenters": "Presenters Here",
      "is_video": false
  }'
  ```

   ```curl
   curl --location --request POST 'https://chriscarrollsmith--whisper-audio-video-transcriber-api-v-4c6a21.modal.run/api/transcribe?src_url=https://storage.googleapis.com/session-scribe-bucket/disciple.wav&unique_id=123456&session_title=Session%20Title%20Here&presenters=Presenters%20Here&is_video=false'

   ```

   Sample response:

   ```json
   {
     "job_id": "your-job-id"
   }
   ```
