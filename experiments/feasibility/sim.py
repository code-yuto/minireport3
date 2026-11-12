"""エッジ・サーバーの分類器を作り、回線が細くなる条件で送り方を比べる。

使い方: python sim.py <features.npz> <結果の出力先フォルダ> <撮影の間隔（秒）>
"""
import json
import sys
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

CLASSES = ["collapsed_building", "fire", "flooded_areas", "normal", "traffic_incident"]
NORMAL = 3
SEED = 0

d = np.load(sys.argv[1])
outdir = Path(sys.argv[2])
outdir.mkdir(parents=True, exist_ok=True)
y, nbytes = d["y"], d["nbytes"]
idx = np.arange(len(y))
tr, rest = train_test_split(idx, test_size=0.5, stratify=y, random_state=SEED)
va, te = train_test_split(rest, test_size=0.6, stratify=y[rest], random_state=SEED)
report = {"counts": {c: int((y == i).sum()) for i, c in enumerate(CLASSES)},
          "split": {"train": len(tr), "val": len(va), "test": len(te)},
          "bytes_per_image_mean": float(nbytes.mean())}


def fit(X):
    sc = StandardScaler().fit(X[tr])
    best = None
    for C in [0.001, 0.01, 0.1, 1.0]:
        m = LogisticRegression(C=C, max_iter=5000, class_weight="balanced")
        m.fit(sc.transform(X[tr]), y[tr])
        f = f1_score(y[va], m.predict(sc.transform(X[va])), average="macro")
        if best is None or f > best[0]:
            best = (f, C, m)
    m = best[2]
    return best[1], m.predict_proba(sc.transform(X))


Ce, pe = fit(d["fe"])   # エッジ（MobileNetV3-Small の特徴）
Cs, ps = fit(d["fs"])   # サーバー（ConvNeXt-Tiny の特徴）


def scores(p, ids):
    pred = p[ids].argmax(1)
    dis_true = y[ids] != NORMAL
    dis_pred = pred != NORMAL
    return {"macroF1": round(f1_score(y[ids], pred, average="macro"), 4),
            "acc": round(float((pred == y[ids]).mean()), 4),
            "recall_per_class": {c: round(r, 4) for c, r in zip(CLASSES, recall_score(y[ids], pred, average=None))},
            "disaster_recall": round(float(dis_pred[dis_true].mean()), 4),
            "false_alarm_rate": round(float(dis_pred[~dis_true].mean()), 4)}


report["edge"] = {"C": Ce, **scores(pe, te)}
report["server"] = {"C": Cs, **scores(ps, te)}

# エッジが「平常」と見逃した被災画像の確信度
pred_e = pe.argmax(1)
miss = te[(y[te] != NORMAL) & (pred_e[te] == NORMAL)]
conf_miss = pe[miss].max(1)
report["edge_misses"] = {
    "n": int(len(miss)),
    "of_disaster": int((y[te] != NORMAL).sum()),
    "conf_quantiles": [round(float(q), 3) for q in np.quantile(conf_miss, [0.1, 0.25, 0.5, 0.75, 0.9])] if len(miss) else [],
    "conf_ge_0.8": int((conf_miss >= 0.8).sum()), "conf_ge_0.9": int((conf_miss >= 0.9).sum()),
    "server_correct_on_misses": int((ps[miss].argmax(1) != NORMAL).sum()),
}

# ---------- 送り方（しきい値は検証用データで、送る割合が同じになるように決める） ----------
def dis_score(p):
    return 1.0 - p[:, NORMAL]          # 被災っぽさ


def thr_for_ratio(v, ratio, high_sends):
    """v の値で送る割合が ratio になるしきい値（high_sends=True なら v>=t を送る）"""
    q = 1 - ratio if high_sends else ratio
    return float(np.quantile(v, q))


def policies(budget):
    conf_v = pe[va].max(1)
    dis_v = dis_score(pe[va])
    th_conf = thr_for_ratio(conf_v, budget, high_sends=False)
    th_dis = thr_for_ratio(dis_v, budget, high_sends=True)
    # しきい値2つ（Choi ら）: 被災っぽさが lo〜hi の間だけ送る。送る割合が予算に近い組で、検証の2値正解率が最大のもの
    best = None
    grid = np.unique(np.quantile(dis_v, np.linspace(0, 1, 81)))
    for lo in grid:
        for hi in grid[grid > lo]:
            send = (dis_v >= lo) & (dis_v <= hi)
            if abs(send.mean() - budget) > 0.02:
                continue
            fin = np.where(send, ps[va].argmax(1) != NORMAL, dis_v > hi)
            acc = (fin == (y[va] != NORMAL)).mean()
            if best is None or acc > best[0]:
                best = (acc, lo, hi)
    lo, hi = best[1], best[2]
    # 提案2: 「確信度が低い」または「被災っぽい」を送る。合わせて予算になる組で、検証の被災見逃しが最小のもの
    best2 = None
    for a in np.linspace(0.05, budget, 20):
        tc = thr_for_ratio(conf_v, a, high_sends=False)
        for td in np.unique(np.quantile(dis_v, np.linspace(0.3, 1, 71))):
            send = (conf_v < tc) | (dis_v >= td)
            if abs(send.mean() - budget) > 0.01:
                continue
            fin = np.where(send, ps[va].argmax(1), pe[va].argmax(1))
            dis = y[va] != NORMAL
            miss = (dis & (fin == NORMAL)).sum()
            if best2 is None or miss < best2[0]:
                best2 = (miss, tc, td)
    comb_t = (pe[te].max(1) < best2[1]) | (dis_score(pe[te]) >= best2[2])
    pe_t, dis_t = pe[te], dis_score(pe[te])
    return {
        "全部送る": (np.ones(len(te), bool), None),
        "エッジだけ": (np.zeros(len(te), bool), None),
        "確信度が低いものだけ送る": (pe_t.max(1) < th_conf, None),
        "しきい値2つ（Choi型）": ((dis_t >= lo) & (dis_t <= hi), None),
        "提案（順番なし）": (dis_t >= th_dis, None),
        "提案2（確信度が低い or 被災っぽい、順番なし）": (comb_t, None),
        "提案2（確信度が低い or 被災っぽい、被災っぽい順）": (comb_t, -dis_t),
        "提案（被災っぽい順に送る）": (dis_t >= th_dis, -dis_t),
    }


def link_profile(kind, T):
    """(開始時刻, bps) の区間リスト"""
    if kind == "劣化(10M→1M→200k)":
        return [(0, 10e6), (T / 3, 1e6), (2 * T / 3, 200e3)]
    return [(0, {"10Mbps": 10e6, "1Mbps": 1e6, "200kbps": 200e3}[kind])]


def tx_end(start, bits, prof):
    t, left = start, bits
    for k, (s, bw) in enumerate(prof):
        e = prof[k + 1][0] if k + 1 < len(prof) else np.inf
        if t >= e:
            continue
        t = max(t, s)
        cap = (e - t) * bw
        if left <= cap:
            return t + left / bw
        left -= cap
        t = e
    return t


def simulate(send, prio, kind, interval, order):
    n = len(te)
    cap_t = np.arange(n) * interval                 # 撮影時刻
    T = n * interval
    prof = link_profile(kind, T)
    ids = te[order]
    s, pr = send[order], (prio[order] if prio is not None else None)
    bits = nbytes[ids] * 8.0
    done = np.full(n, np.nan)
    queue, t, i = [], 0.0, 0
    while i < n or queue:
        while i < n and cap_t[i] <= t:
            if s[i]:
                queue.append(i)
            i += 1
        if not queue:
            if i >= n:
                break
            t = cap_t[i]
            continue
        j = min(queue, key=lambda q: (pr[q], cap_t[q])) if pr is not None else queue[0]
        queue.remove(j)
        t = tx_end(t, bits[j], prof)
        done[j] = t
    final = np.where(s, ps[ids].argmax(1), pe[ids].argmax(1))
    # エッジで終えた画像は、撮影した時刻にラベル（数十バイト）だけ送ったとみなす
    rec_t = np.where(s, done, cap_t)
    dis = y[ids] != NORMAL
    found = dis & (final != NORMAL)
    delay = rec_t[found] - cap_t[found]
    return {
        "送った割合": round(float(s.mean()), 3),
        "送ったMB": round(float(bits[s].sum() / 8e6), 2),
        "被災の見逃し率": round(float(1 - found.sum() / dis.sum()), 4),
        "誤報率": round(float((~dis & (final != NORMAL)).sum() / (~dis).sum()), 4),
        "5クラスmacroF1": round(f1_score(y[ids], final, average="macro"), 4),
        "被災画像の平均遅延s": round(float(delay.mean()), 1),
        "被災画像の遅延95%s": round(float(np.quantile(delay, 0.95)), 1),
        "最後の被災画像まで（撮影終了後）s": round(float(rec_t[found].max() - cap_t[-1]), 1),
    }


INTERVAL = float(sys.argv[3])
rng = np.random.default_rng(SEED)
orders = [rng.permutation(len(te)) for _ in range(3)]
results = {}
for budget in [0.4]:
    pols = policies(budget)
    for kind in ["劣化(10M→1M→200k)"]:
        for name, (send, prio) in pols.items():
            runs = [simulate(send, prio, kind, INTERVAL, o) for o in orders]
            avg = {k: round(float(np.mean([r[k] for r in runs])), 4) for k in runs[0]}
            results.setdefault(f"budget{int(budget*100)}", {}).setdefault(kind, {})[name] = avg

report["sim"] = results
report["sim_setting"] = {"interval_s": INTERVAL, "repeats": len(orders), "send_size": 240, "jpeg_quality": 85}
json.dump(report, open(outdir / f"report_{INTERVAL}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
sys.stdout.reconfigure(encoding="utf-8")
for kind in ["劣化(10M→1M→200k)"]:
    print("== budget40", kind)
    for name, r in results["budget40"][kind].items():
        print(f"  {name:20s}", r)
