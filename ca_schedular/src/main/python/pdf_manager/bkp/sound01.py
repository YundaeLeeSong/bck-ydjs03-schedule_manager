import numpy as np
import wave

# Parameters for the WAV file
sample_rate = 44100  # samples per second
duration = 2.0       # seconds
frequency = 440.0    # Hz (A4 note)

# Generate the sine wave
t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
waveform = 0.5 * np.sin(2 * np.pi * frequency * t)

# Convert to 16-bit PCM format
waveform_integers = np.int16(waveform * 32767)

# Save the waveform as a WAV file
with wave.open('sine_wave.wav', 'w') as wav_file:
    # Set the parameters
    wav_file.setnchannels(1)        # mono
    wav_file.setsampwidth(2)        # 16 bits per sample
    wav_file.setframerate(sample_rate)
    # Write the waveform data
    wav_file.writeframes(waveform_integers.tobytes())

print("WAV file generated successfully!")



# Explanation
# Numpy is used to create the waveform data.
# Wave is used to write the waveform data to a WAV file.
# The sample rate is set to 44.1 kHz, which is a common sample rate for audio files.
# The duration is set to 2 seconds.
# The frequency is set to 440 Hz, which corresponds to the A4 note.
# The waveform is scaled to 16-bit PCM format and saved as a WAV file.
# You can adjust the sample_rate, duration, and frequency variables to generate different types of sounds.



















def generate_natural_wind(duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    noise = np.random.normal(0, 1, t.shape)
    
    # Smooth the noise using a low-pass filter
    kernel_size = int(sample_rate * 0.05)  # 50 ms kernel for smoothing
    smooth_noise = np.convolve(noise, np.ones(kernel_size) / kernel_size, mode='same')
    
    # Create a slow amplitude modulation to simulate wind gusts
    modulation_frequency = 0.5  # Hz (modulation frequency for wind gusts)
    modulation = 0.5 * (1 + np.sin(2 * np.pi * modulation_frequency * t))
    
    # Apply modulation to the smoothed noise
    waveform = smooth_noise * modulation
    waveform = np.int16(waveform * 32767)  # Convert to 16-bit PCM format
    
    return waveform

def save_wave(filename, waveform, sample_rate):
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)        # mono
        wav_file.setsampwidth(2)        # 16 bits per sample
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(waveform.tobytes())

# Parameters for the natural wind sound
sample_rate = 44100  # samples per second
duration = 2.0       # seconds

# Generate the natural wind waveform
natural_wind_waveform = generate_natural_wind(duration, sample_rate)

# Save the natural wind waveform as a WAV file
save_wave('natural_wind.wav', natural_wind_waveform, sample_rate)

print("Natural wind WAV file generated successfully!")