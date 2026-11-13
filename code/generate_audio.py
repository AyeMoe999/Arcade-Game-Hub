import math
import os
import struct
import wave
import random

SAMPLE_RATE = 44100

def midi_to_freq(note):
    if note is None or note == 0:
        return 0.0
    return 440.0 * (2.0 ** ((note - 69) / 12.0))

def pulse_wave(phase, duty=0.5):
    p = phase % (2.0 * math.pi)
    return 1.0 if p < (duty * 2.0 * math.pi) else -1.0

def triangle_wave(phase):
    p = (phase / (2.0 * math.pi)) % 1.0
    return 2.0 * abs(2.0 * p - 1.0) - 1.0

def sine_wave(phase):
    return math.sin(phase)

def generate_pong_bgm(output_path):
    bpm = 138
    quarter_len = 60.0 / bpm
    sixteenth_len = quarter_len / 4.0
    total_bars = 16
    total_beats = total_bars * 4
    total_seconds = total_beats * quarter_len
    total_samples = int(total_seconds * SAMPLE_RATE)

    # Note definitions (MIDI numbers)
    C3, D3, E3, F3, G3, A3, B3 = 48, 50, 52, 53, 55, 57, 59
    C4, D4, E4, F4, G4, A4, B4 = 60, 62, 64, 65, 67, 69, 71
    C5, D5, E5, F5, G5, A5, B5 = 72, 74, 76, 77, 79, 81, 83
    C6, D6, E6, F6, G6, A6, B6 = 84, 86, 88, 89, 91, 93, 95
    ___ = None # Rest

    # 16-bar Lead Melody (in 16th notes: 1 bar = 16 sixteenth notes)
    # Section A: Fun Catchy Intro (Bars 1-4)
    sec_a_lead = [
        E5,___,G5,___,C6,___,___,B5, A5,___,G5,___,E5,___,G5,___,
        F5,___,A5,___,C6,___,___,A5, G5,___,F5,___,E5,___,D5,___,
        C5,___,E5,___,G5,___,C6,___, B5,___,A5,___,G5,___,E5,___,
        D5,___,F5,___,A5,___,B5,___, C6,___,G5,___,E5,___,C5,___
    ]

    # Section B: Bouncy Arpeggio Counterpoint (Bars 5-8)
    sec_b_lead = [
        C5,E5,G5,C6, E5,G5,C6,E6, C5,E5,G5,C6, E5,G5,C6,E6,
        A4,C5,E5,A5, C5,E5,A5,C6, A4,C5,E5,A5, C5,E5,A5,C6,
        F4,A4,C5,F5, A4,C5,F5,A5, F4,A4,C5,F5, A4,C5,F5,A5,
        G4,B4,D5,G5, B4,D5,G5,B5, G4,B4,D5,G5, B4,D5,G5,B5
    ]

    # Section C: High-Energy Arcade Peak (Bars 9-12)
    sec_c_lead = [
        G5,G5,A5,___, C6,___,D6,___, E6,___,D6,___, C6,___,A5,___,
        G5,___,E5,___, G5,___,A5,___, C6,___,D6,___, E6,___,G6,___,
        F6,___,E6,___, D6,___,C6,___, B5,___,A5,___, G5,___,F5,___,
        E5,___,G5,___, C6,___,D6,___, E6,___,D6,___, C6,___,B5,___
    ]

    # Section D: Playful Ping-Pong Left-Right Bouncing Melody (Bars 13-16)
    sec_d_lead = [
        C6,___,G5,___, C6,___,E6,___, G6,___,E6,___, C6,___,G5,___,
        A5,___,F5,___, A5,___,C6,___, F6,___,C6,___, A5,___,F5,___,
        D5,___,F5,___, A5,___,D6,___, F6,___,D6,___, B5,___,G5,___,
        C6,D6,E6,G6, A6,G6,E6,D6, C6,___,G5,___, C6,___,___,___
    ]

    lead_notes = sec_a_lead + sec_b_lead + sec_c_lead + sec_d_lead

    # 16-bar Bassline (8th notes: 1 bar = 8 eighth notes)
    # Chord pattern: C - Am - F - G
    bass_pattern_c = [C3, C3, G3, C3, C3, C3, E3, G3]
    bass_pattern_am = [A2 if 'A2' in locals() else 45, 45, E3, 45, 45, 45, C3, E3]
    bass_pattern_f = [F2 if 'F2' in locals() else 41, 41, C3, 41, 41, 41, A2 if 'A2' in locals() else 45, C3]
    bass_pattern_g = [G2 if 'G2' in locals() else 43, 43, D3, 43, 43, 43, B2 if 'B2' in locals() else 47, D3]

    # MIDI notes for bass:
    C2, A1, F1, G1 = 36, 33, 29, 31
    C3, A2, F2, G2 = 48, 45, 41, 43
    E3, D3, B2 = 52, 50, 47

    bass_c  = [C2, C3, C2, C3, E3, C3, G2, C3]
    bass_am = [A1, A2, A1, A2, C3, A2, E2 if 'E2' in locals() else 40, A2]
    bass_f  = [F1, F2, F1, F2, A2, F2, C2, F2]
    bass_g  = [G1, G2, G1, G2, B2, G2, D2 if 'D2' in locals() else 38, G2]

    bass_notes = (bass_c + bass_am + bass_f + bass_g) * 4 # 16 bars total

    lead_phase = 0.0
    bass_phase = 0.0
    counter_phase = 0.0

    # Pre-generate noise buffer for drums
    noise_buffer = [random.uniform(-1.0, 1.0) for _ in range(SAMPLE_RATE)]

    left_samples = []
    right_samples = []

    for i in range(total_samples):
        t = i / SAMPLE_RATE

        # Determine sixteenth note index
        sixteenth_idx = int(t / sixteenth_len) % len(lead_notes)
        sub_sixteenth_t = (t % sixteenth_len) / sixteenth_len

        # Lead Note
        lead_midi = lead_notes[sixteenth_idx]
        lead_freq = midi_to_freq(lead_midi)
        
        # Lead Envelope (fast attack, exponential decay)
        lead_env = math.exp(-sub_sixteenth_t * 3.5) if lead_freq > 0 else 0.0

        if lead_freq > 0:
            # Subtle pitch vibrato
            vibrato = 1.0 + 0.005 * math.sin(2.0 * math.pi * 6.0 * t)
            lead_phase += 2.0 * math.pi * (lead_freq * vibrato) / SAMPLE_RATE
            # Pulse wave with 25% duty cycle for bright arcade sound
            lead_val = pulse_wave(lead_phase, duty=0.25) * lead_env * 0.22
        else:
            lead_val = 0.0

        # Bass Note (8th notes)
        eighth_idx = int(t / (sixteenth_len * 2)) % len(bass_notes)
        sub_eighth_t = (t % (sixteenth_len * 2)) / (sixteenth_len * 2)
        bass_midi = bass_notes[eighth_idx]
        bass_freq = midi_to_freq(bass_midi)
        bass_env = math.exp(-sub_eighth_t * 2.5) if bass_freq > 0 else 0.0

        if bass_freq > 0:
            bass_phase += 2.0 * math.pi * bass_freq / SAMPLE_RATE
            # Warm triangle/square bass mix
            bass_val = (triangle_wave(bass_phase) * 0.6 + pulse_wave(bass_phase, 0.5) * 0.4) * bass_env * 0.35
        else:
            bass_val = 0.0

        # Drums / Rhythm
        beat_in_bar = (t / quarter_len) % 4.0
        sub_beat_t = beat_in_bar % 1.0

        # Kick drum on beats 0 and 2 (Low frequency sine sweep 130Hz -> 40Hz)
        kick_val = 0.0
        if (beat_in_bar < 0.25) or (2.0 <= beat_in_bar < 2.25):
            k_t = (sub_beat_t if beat_in_bar < 0.25 else beat_in_bar - 2.0) / 0.25
            kick_freq = 130.0 * (1.0 - k_t) + 40.0
            kick_env = math.exp(-k_t * 6.0)
            kick_phase = 2.0 * math.pi * kick_freq * t
            kick_val = sine_wave(kick_phase) * kick_env * 0.35

        # Snare drum on beats 1 and 3 (Noise burst + 180Hz body snap)
        snare_val = 0.0
        if (1.0 <= beat_in_bar < 1.25) or (3.0 <= beat_in_bar < 3.25):
            s_t = (beat_in_bar - 1.0 if beat_in_bar < 1.25 else beat_in_bar - 3.0) / 0.25
            snare_env = math.exp(-s_t * 8.0)
            noise_sample = noise_buffer[i % len(noise_buffer)]
            snap = sine_wave(2.0 * math.pi * 180.0 * t) * 0.4
            snare_val = (noise_sample * 0.6 + snap) * snare_env * 0.25

        # Hi-hat tick every sixteenth note
        hihat_val = 0.0
        sub_16_t = sub_sixteenth_t
        if sub_16_t < 0.3:
            hh_env = math.exp(-sub_16_t * 25.0)
            hihat_val = noise_buffer[(i * 3) % len(noise_buffer)] * hh_env * 0.08

        # Ping-Pong Panning effect for Lead in Section D (Bars 13-16)
        bar_idx = int(t / (quarter_len * 4)) % 16
        if bar_idx >= 12:
            # Alternating left-right pan on every 8th note
            pan_left = 0.85 if (sixteenth_idx % 4 < 2) else 0.15
            pan_right = 1.0 - pan_left
        else:
            pan_left = 0.5
            pan_right = 0.5

        # Combine Channels
        mix_left = (lead_val * pan_left * 2.0) + (bass_val * 0.5) + (kick_val * 0.5) + (snare_val * 0.5) + (hihat_val * 0.6)
        mix_right = (lead_val * pan_right * 2.0) + (bass_val * 0.5) + (kick_val * 0.5) + (snare_val * 0.5) + (hihat_val * 0.4)

        # Soft clipping / Limiter
        mix_left = max(-0.95, min(0.95, mix_left))
        mix_right = max(-0.95, min(0.95, mix_right))

        left_samples.append(int(mix_left * 32767))
        right_samples.append(int(mix_right * 32767))

    # Write WAV file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with wave.open(output_path, 'wb') as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        
        interleaved = bytearray()
        for l, r in zip(left_samples, right_samples):
            interleaved.extend(struct.pack('<hh', l, r))
        
        wav_file.writeframes(interleaved)

    print(f"Generated BGM successfully: {output_path} ({total_seconds:.2f}s)")


def generate_sound_effects(audio_dir):
    os.makedirs(audio_dir, exist_ok=True)
    
    # 1. Hit Sound (Paddle Bounce - crisp high beep with fast frequency drop)
    hit_path = os.path.join(audio_dir, "hit.wav")
    samples = []
    dur = 0.08
    n_samples = int(dur * SAMPLE_RATE)
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        freq = 600.0 - (t / dur) * 300.0
        env = math.exp(-t * 35.0)
        val = pulse_wave(2.0 * math.pi * freq * t, 0.5) * env * 0.5
        samples.append(int(val * 32767))
    with wave.open(hit_path, 'wb') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SAMPLE_RATE)
        f.writeframes(b''.join(struct.pack('<h', s) for s in samples))

    # 2. Wall Sound (Top/Bottom Bounce - lower pitch boing)
    wall_path = os.path.join(audio_dir, "wall.wav")
    samples = []
    dur = 0.07
    n_samples = int(dur * SAMPLE_RATE)
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        freq = 320.0 - (t / dur) * 120.0
        env = math.exp(-t * 40.0)
        val = triangle_wave(2.0 * math.pi * freq * t) * env * 0.5
        samples.append(int(val * 32767))
    with wave.open(wall_path, 'wb') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SAMPLE_RATE)
        f.writeframes(b''.join(struct.pack('<h', s) for s in samples))

    # 3. Score Sound (Point Scored - ascending arcade arpeggio)
    score_path = os.path.join(audio_dir, "score.wav")
    samples = []
    dur = 0.3
    n_samples = int(dur * SAMPLE_RATE)
    notes = [523.25, 659.25, 783.99, 1046.50] # C5, E5, G5, C6
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        note_idx = min(len(notes) - 1, int(t / (dur / len(notes))))
        freq = notes[note_idx]
        sub_t = t % (dur / len(notes))
        env = math.exp(-sub_t * 18.0)
        val = pulse_wave(2.0 * math.pi * freq * t, 0.3) * env * 0.4
        samples.append(int(val * 32767))
    with wave.open(score_path, 'wb') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SAMPLE_RATE)
        f.writeframes(b''.join(struct.pack('<h', s) for s in samples))

    print(f"Generated SFX in {audio_dir}")


if __name__ == "__main__":
    audio_dir = os.path.join(os.path.dirname(__file__), "audio")
    generate_pong_bgm(os.path.join(audio_dir, "pong_bgm.wav"))
    generate_sound_effects(audio_dir)
