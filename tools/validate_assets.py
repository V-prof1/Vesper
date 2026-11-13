#!/usr/bin/env python3
"""Check all Vesper sprite manifests and local Android assets without dependencies."""
from pathlib import Path
import json, struct
ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'assets/sprites.json').read_text(encoding='utf-8'))
assert len(manifest['characters'])==20, 'Expected 20 characters'
assert len(manifest['moris'])==14, 'Expected 14 moris'
frames=0
for group in ('characters','moris'):
    for actor, info in manifest[group].items():
        path=ROOT/info['file']
        assert path.is_file(), f'Missing {path}'
        android=ROOT/'app/src/main/assets'/info['file']
        assert android.is_file(), f'Missing Android asset {android}'
        assert path.read_bytes()==android.read_bytes(), f'Asset mismatch: {actor}'
        raw=path.read_bytes()
        assert raw[:8]==b'\x89PNG\r\n\x1a\n', f'Invalid PNG: {path}'
        w,h=struct.unpack('>II',raw[16:24])
        assert w==info['width']*info['columns'], f'Wrong PNG width: {actor}'
        assert h>=info['height'], f'Wrong PNG height: {actor}'
        frames+=info['frames']
assert frames==4584, f'Expected 4584 frames, got {frames}'
for file in ('index.html','JOGAR_NO_PC.html','app/src/main/assets/index.html'):
    raw=(ROOT/file).read_text(encoding='utf-8')
    assert 'pixelManifest' in raw, f'Missing sprite runtime: {file}'
print(f'OK: {len(manifest["characters"])} characters, {len(manifest["moris"])} moris, {frames} frames, Android assets complete')
