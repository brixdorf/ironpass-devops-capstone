"""Packs the 16, 32 and 48 px PNGs into one favicon.ico (PNG data inside, no Pillow needed).
   python make_ico.py <favicon-32.png> <work-dir> <output.ico>"""
import struct
import sys

png32, work, out = sys.argv[1:4]
files = [(16, f"{work}/_f16.png"), (32, png32), (48, f"{work}/_f48.png")]
data = [open(f, "rb").read() for _, f in files]
header = struct.pack("<HHH", 0, 1, len(files))
offset = 6 + 16 * len(files)
entries = b""
for (size, _), blob in zip(files, data):
    entries += struct.pack("<BBBBHHII", size, size, 0, 0, 1, 32, len(blob), offset)
    offset += len(blob)
open(out, "wb").write(header + entries + b"".join(data))
