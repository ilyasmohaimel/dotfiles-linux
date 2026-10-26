#!/usr/bin/env python3
"""Encode and verify a full-length README WebP with bounded working memory.

Requires FFmpeg, Pillow and NumPy. Source movies remain unchanged.
"""
import argparse, json, math, struct, subprocess, hashlib
from pathlib import Path
from PIL import Image
import numpy as np

def file_hash(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def chunks(data):
    p = 12
    while p < len(data):
        n = struct.unpack_from('<I', data, p + 4)[0]
        end = p + 8 + n + n % 2
        yield (data[p:p + 4], data[p:end])
        p = end
    assert p == len(data)

def build(source, output, work_dir=None):
    output.parent.mkdir(parents=True, exist_ok=True)
    source_hash = file_hash(source)
    workspace = (work_dir or output.parent / '.preview-work') / source_hash[:16]
    workspace.mkdir(parents=True, exist_ok=True)
    duration = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(source)]))
    header = []
    frames = []
    metrics = []
    total = 0
    for start in range(0, math.ceil(duration), 8):
        length = min(8, duration - start)
        part = workspace / f'rgb-q90-method4-{start:04d}.webp'
        common = ['ffmpeg', '-v', 'error', '-threads', '2', '-filter_threads', '2', '-ss', str(start), '-i', str(source), '-t', str(length), '-vf', 'fps=15,scale=854:480:flags=lanczos,format=bgra', '-an']
        if not part.exists():
            pending = part.with_suffix('.pending.webp')
            subprocess.run([*common, '-c:v', 'libwebp_anim', '-pix_fmt', 'bgra', '-quality', '90', '-compression_level', '4', '-loop', '0', '-y', str(pending)], check=True)
            pending.replace(part)
        first_frame = True
        for kind, blob in chunks(part.read_bytes()):
            if kind == b'ANMF':
                if first_frame:
                    rectangle = [int.from_bytes(blob[i:i + 3], 'little') for i in (8, 11, 14, 17)]
                    assert rectangle == [0, 0, 853, 479] and blob[23] & 2, rectangle
                    first_frame = False
                frames.append(blob)
            elif start == 0 and kind in (b'VP8X', b'ANIM'):
                header.append(blob)
        proc = subprocess.Popen([*common, '-f', 'rawvideo', '-pix_fmt', 'bgra', '-'], stdout=subprocess.PIPE)
        im = Image.open(part)
        idx = 0
        im.seek(0)
        im.load()
        end = im.info['duration']
        count = 0
        worst = 100.0
        maxmae = 0.0
        while (data := proc.stdout.read(854 * 480 * 4)):
            assert len(data) == 854 * 480 * 4
            while (count + 0.5) * 1000 / 15 >= end and idx + 1 < im.n_frames:
                idx += 1
                im.seek(idx)
                im.load()
                end += im.info['duration']
            expected = np.frombuffer(data, dtype=np.uint8).reshape(480, 854, 4)[:, :, [2, 1, 0]].astype(np.float32)
            actual = np.asarray(im.convert('RGB')).astype(np.float32)
            delta = expected - actual
            mse = float(np.mean(delta * delta))
            psnr = 100 if mse == 0 else 10 * math.log10(255 * 255 / mse)
            worst = min(worst, psnr)
            maxmae = max(maxmae, float(np.abs(delta).mean()))
            count += 1
        assert proc.wait() == 0
        assert worst > 30, (start, worst, maxmae)
        metrics.append({'startSeconds': start, 'frames': count, 'minimumPsnrDb': round(worst, 2), 'maximumMeanAbsoluteRgbError': round(maxmae, 3)})
        total += count
        print(source.name, start, count, round(worst, 2), sum(map(len, frames)), flush=True)
    # Each section begins with a full canvas frame, so it resets prior state.
    payload = b'WEBP' + b''.join(header + frames)
    output.write_bytes(b'RIFF' + struct.pack('<I', len(payload)) + payload)
    assert total == round(duration * 15), (total, duration)
    assert output.stat().st_size < 100 * 1024 * 1024
    im = Image.open(output)
    ms = 0
    for i in range(im.n_frames):
        im.seek(i)
        im.load()
        ms += im.info['duration']
    assert abs(ms - duration * 1000) < 100, (ms, duration)
    report = {'source': source.name, 'sourceSha256': source_hash, 'encoding': 'RGB-input lossy WebP, quality 90, independently encoded 8-second sections', 'width': 854, 'height': 480, 'fps': 15, 'framesCompared': total, 'encodedFrames': im.n_frames, 'durationMs': ms, 'bytes': output.stat().st_size, 'sha256': file_hash(output), 'segments': metrics}
    output.with_suffix('.json').write_text(json.dumps(report, indent=2) + '\n')
    print('DONE', output, report['bytes'], report['durationMs'], flush=True)
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--work-dir', type=Path, help='Persistent section cache for resuming interrupted builds')
    args = parser.parse_args()
    build(args.input, args.output, args.work_dir)
