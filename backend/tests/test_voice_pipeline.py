import pytest
from app.core.voice.manager import VoiceManager

def test_voice_manager_initialization():
    manager = VoiceManager()
    assert not manager.is_listening
    assert not manager.is_speaking
    assert len(manager.audio_buffer) == 0

def test_voice_manager_buffer_accumulation():
    manager = VoiceManager()
    
    # Mocking a callback
    called = False
    def mock_callback(buffer):
        nonlocal called
        called = True

    # Process some dummy bytes
    manager.process_incoming_audio(b'\x00\x01\x02', mock_callback)
    
    assert len(manager.audio_buffer) == 3
    # Our mock implementation in manager.py doesn't currently flush unless we hit the threshold logic (which is commented out)
    # But we can test the buffer extension
    assert manager.audio_buffer == bytearray(b'\x00\x01\x02')

def test_trigger_interrupt():
    manager = VoiceManager()
    manager.is_speaking = True
    
    manager.trigger_interrupt()
    
    assert not manager.is_speaking
