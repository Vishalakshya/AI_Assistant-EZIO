import logging
import asyncio
from typing import Callable

logger = logging.getLogger(__name__)

class VoiceManager:
    """
    Manages the offline wake-word detection (pvporcupine) and 
    Voice Activity Detection (webrtcvad).
    """
    def __init__(self):
        self.is_listening = False
        self.is_speaking = False
        self.audio_buffer = bytearray()
        
        # In a real implementation, initialize pvporcupine here with "Hey EZIO" model
        # and WebRTC VAD with strict aggressiveness level (3)
        # self.porcupine = pvporcupine.create(access_key="...", keyword_paths=["hey_ezio.ppn"])
        # self.vad = webrtcvad.Vad(3)

    def process_incoming_audio(self, pcm_chunk: bytes, on_speech_detected: Callable):
        """
        Takes raw 16kHz PCM chunks from the WebSocket.
        1. Checks for Wake Word if idle.
        2. Checks VAD for speech ends to flush buffer to Whisper.
        """
        if self.is_speaking:
            # INTERRUPT LOGIC
            # If EZIO is speaking (TTS outputting) and we detect loud speech on the mic,
            # we immediately trigger a halt callback to stop TTS.
            # volume_rms = math.sqrt(sum([sample*sample for sample in pcm_chunk])/len(pcm_chunk))
            # if volume_rms > THRESHOLD:
            #    self.trigger_interrupt()
            pass

        self.audio_buffer.extend(pcm_chunk)
        
        # Mock VAD logic: If silence detected for 1.5 seconds, flush to STT
        # is_speech = self.vad.is_speech(pcm_chunk, 16000)
        # if not is_speech and self.buffer_duration > 1.5s:
        #    on_speech_detected(self.audio_buffer)
        #    self.audio_buffer.clear()

    def trigger_interrupt(self):
        self.is_speaking = False
        logger.info("User interrupted EZIO voice playback. Halting TTS.")
        # Fire event to WebSocket to immediately stop AudioContext playback on frontend

voice_manager = VoiceManager()
