from flask import Flask, request, jsonify
from torch import tensor, no_grad, argmax, float
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
from soundfile import SoundFile as sf
from torchaudio.transforms import Resample

app = Flask(__name__)

# Load the pre-trained model and processor
model_name = "facebook/wav2vec2-base-960h"
processor = Wav2Vec2Processor.from_pretrained(model_name)
model = Wav2Vec2ForCTC.from_pretrained(model_name)

def handler(event, context):
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
    
    audio_file = event.files['audio']
    if audio_file.filename == '':
        return jsonify({"error": "Empty audio file name"}), 400
    
    # Save the uploaded audio file to the file system
    audio_path = "uploaded_audio.wav"
    audio_file.save(audio_path)
    
    # Load the original audio waveform and its sampling rate using soundfile
    print("Loading audio...")
    waveform, original_sampling_rate = sf.read(audio_path)
    print("Audio loaded successfully.")
    
    # Convert the waveform data to the correct data type (Double)
    waveform = tensor(waveform, dtype=float)
    
    # Resample the audio waveform to the target sampling rate (16000 Hz)
    target_sampling_rate = 16000
    resampler = Resample(orig_freq=original_sampling_rate, new_freq=target_sampling_rate)
    resampled_waveform = resampler(waveform)
    
    # Preprocess the audio
    inputs = processor(resampled_waveform.numpy(), sampling_rate=target_sampling_rate, return_tensors="pt")
    # Perform inference
    with no_grad():
        logits = model(input_values=inputs.input_values).logits
    # Perform CTC decoding
    predicted_ids = argmax(logits, dim=-1)
    predicted_text = processor.batch_decode(predicted_ids)
    
    return jsonify({"transcription": predicted_text[0]})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
