"""AIDER の全画像から、エッジ役・サーバー役のモデルの特徴量と、送るときのバイト数を取り出す。

使い方: python extract.py <AIDERフォルダ> <出力npz>
"""
import io
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torchvision.models as tvm
from PIL import Image

CLASSES = ["collapsed_building", "fire", "flooded_areas", "normal", "traffic_incident"]
SEND_SIZE = 240        # ドローンが送る画像の大きさ（EmergencyNet の入力と同じ）
JPEG_QUALITY = 85

root = Path(sys.argv[1])
out = sys.argv[2]
torch.set_num_threads(12)

paths, labels = [], []
for ci, c in enumerate(CLASSES):
    ps = sorted((root / c).glob("*"))
    ps = [p for p in ps if p.suffix.lower() in (".jpg", ".jpeg", ".png")]
    paths += ps
    labels += [ci] * len(ps)
print({c: labels.count(i) for i, c in enumerate(CLASSES)}, flush=True)

edge_w = tvm.MobileNet_V3_Small_Weights.IMAGENET1K_V1
srv_w = tvm.ConvNeXt_Tiny_Weights.IMAGENET1K_V1
edge = tvm.mobilenet_v3_small(weights=edge_w).eval()
edge.classifier = torch.nn.Identity()          # 576次元の特徴
srv = tvm.convnext_tiny(weights=srv_w).eval()
srv.classifier[2] = torch.nn.Identity()        # 768次元の特徴
pre_e = edge_w.transforms()
pre_s = srv_w.transforms()
print("edge params", sum(p.numel() for p in edge.parameters()),
      "server params", sum(p.numel() for p in srv.parameters()), flush=True)

fe, fs, nbytes, sizes = [], [], [], []
B = 32
t0 = time.time()
with torch.no_grad():
    for i in range(0, len(paths), B):
        imgs = [Image.open(p).convert("RGB") for p in paths[i:i + B]]
        for im in imgs:
            sizes.append(im.size)
            buf = io.BytesIO()
            im.resize((SEND_SIZE, SEND_SIZE)).save(buf, "JPEG", quality=JPEG_QUALITY)
            nbytes.append(buf.tell())
        fe.append(edge(torch.stack([pre_e(im) for im in imgs])).numpy())
        fs.append(srv(torch.stack([pre_s(im) for im in imgs])).numpy())
        if i % (B * 20) == 0:
            print(i, len(paths), f"{time.time() - t0:.0f}s", flush=True)

np.savez(out, fe=np.concatenate(fe), fs=np.concatenate(fs), y=np.array(labels),
         nbytes=np.array(nbytes), sizes=np.array(sizes),
         paths=np.array([str(p.relative_to(root)) for p in paths]))
print("done", f"{time.time() - t0:.0f}s")
