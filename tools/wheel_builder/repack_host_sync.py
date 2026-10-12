"""Rebuild the official beta2.patch1 wheel with only the three host-copy barriers.

Run with Python 3.12 and an output directory. The input wheel, unmodified source,
and patched source are checked so unrelated changes cannot enter this backport.
"""
import base64
import csv
import hashlib
import io
from pathlib import Path
import sys
import urllib.request
import zipfile

BASE = "3.0.0b2.post1"
VERSION = BASE + "+ripl.1"
SOURCE = "isaaclab_physx/assets/rigid_object/rigid_object.py"
patched = (Path(__file__).resolve().parents[2] / "source/isaaclab_physx" / SOURCE).read_bytes()
assert hashlib.sha256(patched).hexdigest() == "3b999f7b08c164dcd15ce0d402ec4098444f0b6b7a49eab7846f0c8686e33eda"
with urllib.request.urlopen(f"https://pypi.nvidia.com/isaaclab/isaaclab-{BASE}-py3-none-any.whl") as response:
    original = response.read()
assert hashlib.sha256(original).hexdigest() == "dd32886588479ffd70f7348019aeac1582eb9ad16c40244f41d9f458f96f73c3"
output = Path(sys.argv[1]); output.mkdir(parents=True, exist_ok=True)
result = output / f"isaaclab-{VERSION}-py3-none-any.whl"
record = io.StringIO(); writer = csv.writer(record, lineterminator="\n")
with zipfile.ZipFile(io.BytesIO(original)) as src, zipfile.ZipFile(result, "w") as dst:
    assert hashlib.sha256(src.read(SOURCE)).hexdigest() == "0b19990c85e1753a6489fa962b3008869b2d34ef281fa8549f1a65f0c32cf79d"
    for info in src.infolist():
        data = src.read(info.filename)
        info.filename = info.filename.replace(f"isaaclab-{BASE}.dist-info/", f"isaaclab-{VERSION}.dist-info/")
        if info.filename == SOURCE:
            data = patched
        if info.filename.endswith(".dist-info/METADATA"):
            assert data.count(f"Version: {BASE}\n".encode()) == 1
            data = data.replace(f"Version: {BASE}\n".encode(), f"Version: {VERSION}\n".encode())
        if info.filename.endswith(".dist-info/RECORD"):
            record_info = info
            continue
        dst.writestr(info, data)
        digest = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=").decode()
        writer.writerow([info.filename, "sha256=" + digest, len(data)])
    writer.writerow([record_info.filename, "", ""])
    dst.writestr(record_info, record.getvalue())
print(result, hashlib.sha256(result.read_bytes()).hexdigest())
