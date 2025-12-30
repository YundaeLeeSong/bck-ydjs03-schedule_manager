import numpy as np
import wave

def generate_siren_wave(frequency1, frequency2, duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    waveform = 0.5 * np.sin(2 * np.pi * frequency1 * t) + 0.5 * np.sin(2 * np.pi * frequency2 * t)
    waveform_integers = np.int16(waveform * 32767)
    return waveform_integers

def save_wave(filename, waveform, sample_rate):
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)        # mono
        wav_file.setsampwidth(2)        # 16 bits per sample
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(waveform.tobytes())

# Parameters for the siren sound
sample_rate = 44100  # samples per second
duration = 5.0       # seconds
frequency1 = 600.0   # Hz
frequency2 = 900.0   # Hz

# Generate the siren waveform
siren_waveform = generate_siren_wave(frequency1, frequency2, duration, sample_rate)

# Save the siren waveform as a WAV file
save_wave('siren_sound.wav', siren_waveform, sample_rate)

print("Siren WAV file generated successfully!")


def add_noise(waveform, noise_level=0.02):
    noise = noise_level * np.random.normal(size=waveform.shape)
    noisy_waveform = waveform + noise
    noisy_waveform = np.clip(noisy_waveform, -1.0, 1.0)  # Ensure values stay within [-1, 1]
    return np.int16(noisy_waveform * 32767)

# Add noise to the siren waveform
noisy_siren_waveform = add_noise(siren_waveform)

# Save the noisy siren waveform as a WAV file
save_wave('noisy_siren_sound.wav', noisy_siren_waveform, sample_rate)

print("Noisy siren WAV file generated successfully!")
