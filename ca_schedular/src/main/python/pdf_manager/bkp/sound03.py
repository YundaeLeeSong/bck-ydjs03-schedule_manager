import numpy as np
import wave

def generate_laser_shot(frequency, duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    waveform = 0.5 * np.sin(2 * np.pi * frequency * t * np.exp(-3 * t))
    waveform_integers = np.int16(waveform * 32767)
    return waveform_integers

def save_wave(filename, waveform, sample_rate):
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)        # mono
        wav_file.setsampwidth(2)        # 16 bits per sample
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(waveform.tobytes())

# Parameters for the laser shot sound
sample_rate = 44100  # samples per second
duration = 0.5       # seconds
frequency = 1500.0   # Hz

# Generate the laser shot waveform
laser_waveform = generate_laser_shot(frequency, duration, sample_rate)

# Save the laser shot waveform as a WAV file
save_wave('laser_shot.wav', laser_waveform, sample_rate)

print("Laser shot WAV file generated successfully!")
















def generate_explosion(duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    noise = np.random.normal(0, 1, t.shape)
    envelope = np.exp(-5 * t)
    waveform = envelope * noise
    waveform_integers = np.int16(waveform * 32767)
    return waveform_integers

# Parameters for the explosion sound
sample_rate = 44100  # samples per second
duration = 1.0       # seconds

# Generate the explosion waveform
explosion_waveform = generate_explosion(duration, sample_rate)

# Save the explosion waveform as a WAV file
save_wave('explosion.wav', explosion_waveform, sample_rate)

print("Explosion WAV file generated successfully!")











def generate_magic_spell(frequency, duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    waveform = 0.3 * np.sin(2 * np.pi * frequency * t) + 0.3 * np.sin(2 * np.pi * (frequency + 50) * t)
    envelope = np.exp(-2 * t)
    waveform = envelope * waveform
    waveform_integers = np.int16(waveform * 32767)
    return waveform_integers

# Parameters for the magic spell sound
sample_rate = 44100  # samples per second
duration = 1.5       # seconds
frequency = 800.0    # Hz

# Generate the magic spell waveform
magic_spell_waveform = generate_magic_spell(frequency, duration, sample_rate)

# Save the magic spell waveform as a WAV file
save_wave('magic_spell.wav', magic_spell_waveform, sample_rate)

print("Magic spell WAV file generated successfully!")














def generate_footstep(duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    noise = np.random.normal(0, 1, t.shape)
    envelope = np.exp(-20 * t)
    waveform = envelope * noise
    waveform_integers = np.int16(waveform * 32767)
    return waveform_integers

# Parameters for the footstep sound
sample_rate = 44100  # samples per second
duration = 0.2       # seconds

# Generate the footstep waveform
footstep_waveform = generate_footstep(duration, sample_rate)

# Save the footstep waveform as a WAV file
save_wave('footstep.wav', footstep_waveform, sample_rate)

print("Footstep WAV file generated successfully!")
















def generate_power_up(frequency_start, frequency_end, duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    frequency_sweep = np.linspace(frequency_start, frequency_end, t.shape[0])
    waveform = 0.5 * np.sin(2 * np.pi * frequency_sweep * t)
    waveform_integers = np.int16(waveform * 32767)
    return waveform_integers

# Parameters for the power-up sound
sample_rate = 44100    # samples per second
duration = 1.0         # seconds
frequency_start = 300  # Hz
frequency_end = 1500   # Hz

# Generate the power-up waveform
power_up_waveform = generate_power_up(frequency_start, frequency_end, duration, sample_rate)

# Save the power-up waveform as a WAV file
save_wave('power_up.wav', power_up_waveform, sample_rate)

print("Power-up WAV file generated successfully!")












def generate_water_drop(frequency, duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    waveform = 0.5 * np.sin(2 * np.pi * frequency * t) * np.exp(-10 * t)
    noise = np.random.normal(0, 0.02, t.shape)
    waveform += noise
    waveform_integers = np.int16(waveform * 32767)
    return waveform_integers

# Parameters for the water drop sound
sample_rate = 44100  # samples per second
duration = 0.5       # seconds
frequency = 600.0    # Hz

# Generate the water drop waveform
water_drop_waveform = generate_water_drop(frequency, duration, sample_rate)

# Save the water drop waveform as a WAV file
save_wave('water_drop.wav', water_drop_waveform, sample_rate)

print("Water drop WAV file generated successfully!")












def generate_wind(duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    noise = np.random.normal(0, 1, t.shape)
    envelope = 0.5 * (1 + np.sin(2 * np.pi * 0.1 * t)) * np.exp(-0.5 * t)
    waveform = envelope * noise
    waveform_integers = np.int16(waveform * 32767)
    return waveform_integers

def save_wave(filename, waveform, sample_rate):
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)        # mono
        wav_file.setsampwidth(2)        # 16 bits per sample
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(waveform.tobytes())

# Parameters for the wind blowing sound
sample_rate = 44100  # samples per second
duration = 2.0       # seconds

# Generate the wind blowing waveform
wind_waveform = generate_wind(duration, sample_rate)

# Save the wind blowing waveform as a WAV file
save_wave('wind_blowing_natural.wav', wind_waveform, sample_rate)

print("Natural wind blowing WAV file generated successfully!")










def generate_electric_spark(frequency, duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    waveform = np.sin(2 * np.pi * frequency * t)
    envelope = np.random.choice([0.5, -0.5], size=t.shape)
    waveform = envelope * waveform
    waveform_integers = np.int16(waveform * 32767)
    return waveform_integers

# Parameters for the electric spark sound
sample_rate = 44100  # samples per second
duration = 0.3       # seconds
frequency = 800.0    # Hz

# Generate the electric spark waveform
electric_spark_waveform = generate_electric_spark(frequency, duration, sample_rate)

# Save the electric spark waveform as a WAV file
save_wave('electric_spark.wav', electric_spark_waveform, sample_rate)

print("Electric spark WAV file generated successfully!")











def generate_heartbeat(frequency, duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    waveform = 0.5 * np.sin(2 * np.pi * frequency * t) * np.exp(-5 * t)
    waveform[int(0.1 * sample_rate):int(0.2 * sample_rate)] *= 2
    waveform[int(0.3 * sample_rate):int(0.4 * sample_rate)] *= 2
    waveform_integers = np.int16(waveform * 32767)
    return waveform_integers

# Parameters for the heartbeat sound
sample_rate = 44100  # samples per second
duration = 1.0       # seconds
frequency = 1.2      # Hz (slow heartbeat)

# Generate the heartbeat waveform
heartbeat_waveform = generate_heartbeat(frequency, duration, sample_rate)

# Save the heartbeat waveform as a WAV file
save_wave('heartbeat.wav', heartbeat_waveform, sample_rate)

print("Heartbeat WAV file generated successfully!")