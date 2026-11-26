"""Simulation for doc/proposal-infeasible.md (sections 5.4 and 5.5).

One shared link, non-preemptive, every image takes the same time to send.
A 10-minute flight; images arrive as a Poisson process (2 images/s); 30% are disaster images.
Assumed severity s given by the edge AI (not measured values):
  disaster: 90% s=0.9 (sure), 5% s=0.5 (unsure), 5% s=0.05 (missed)  -- miss rate also 20%, 40%
  normal:   95% s=0.05,        5% s=0.5
After the flight ends, the queue keeps draining until every queued image is sent.

Policies
  fifo   : arrival order
  sev    : highest s first (ties: earlier arrival)
  sum    : highest s + wait / ALPHA_INV  (the proposal, 1/alpha = 10 s)
  filter : drop images with s < 0.1, then highest s first
"""
from __future__ import annotations

import numpy as np

LAM = 2.0          # images per second
T_FLIGHT = 600.0   # seconds
P_DISASTER = 0.3
ALPHA_INV = 10.0   # seconds of waiting that add 1 to the priority
DROP_BELOW = 0.1
SEEDS = range(5)


MISS = 0.05        # share of disaster images the edge AI misses (s=0.05); 5% are unsure (s=0.5)


def make_arrivals(seed: int) -> list[tuple[float, bool, float]]:
    rng = np.random.default_rng(seed)
    t, arrivals = 0.0, []
    while True:
        t += rng.exponential(1 / LAM)
        if t > T_FLIGHT:
            return arrivals
        is_disaster = rng.random() < P_DISASTER
        u = rng.random()
        if is_disaster:
            s = 0.9 if u < 1 - MISS - 0.05 else (0.5 if u < 1 - MISS else 0.05)
        else:
            s = 0.05 if u < 0.95 else 0.5
        arrivals.append((t, is_disaster, s))


def simulate(rho: float, policy: str, seed: int) -> dict[str, float]:
    service = rho / LAM  # rho is the load before any filtering
    arrivals = make_arrivals(seed)
    n_disaster = sum(d for _, d, _ in arrivals)
    if policy == "filter":
        sent = [x for x in arrivals if x[2] >= DROP_BELOW]
    else:
        sent = arrivals
    n = len(sent)
    finish = np.zeros(n)
    queue: list[int] = []
    now, i = 0.0, 0
    while i < n or queue:
        if not queue and now < sent[i][0]:
            now = sent[i][0]
        while i < n and sent[i][0] <= now:
            queue.append(i)
            i += 1
        if policy == "fifo":
            k = min(queue, key=lambda j: sent[j][0])
        elif policy == "sum":
            k = max(queue, key=lambda j: sent[j][2] + (now - sent[j][0]) / ALPHA_INV)
        else:  # sev, filter
            k = max(queue, key=lambda j: (sent[j][2], -sent[j][0]))
        queue.remove(k)
        now += service
        finish[k] = now
    arrive = np.array([x[0] for x in sent])
    is_dis = np.array([x[1] for x in sent], dtype=bool)
    is_missed = is_dis & (np.array([x[2] for x in sent]) < DROP_BELOW)
    delay = finish - arrive
    # 90% of ALL disaster images, counting dropped ones as never delivered (infinite delay)
    all_dis_delay = np.sort(np.concatenate([delay[is_dis], np.full(n_disaster - int(is_dis.sum()), np.inf)]))
    p90 = float(all_dis_delay[int(np.ceil(0.9 * n_disaster)) - 1])
    return {
        "p90": p90,
        "missed_mean": float(delay[is_missed].mean()) if is_missed.any() else float("nan"),
        "lost_pct": 100 * (n_disaster - int(is_dis.sum())) / n_disaster,
        "sent_pct": 100 * n / len(arrivals),
    }


def main() -> None:
    global MISS
    for miss, rhos in ((0.05, (0.9, 1.2, 3.0)), (0.20, (0.9, 1.2)), (0.40, (0.9, 1.2))):
        MISS = miss
        print(f"--- miss rate {miss:.2f}")
        run_table(rhos)


def run_table(rhos: tuple[float, ...]) -> None:
    for rho in rhos:
        for policy in ("fifo", "sev", "sum", "filter"):
            if rho == 3.0 and policy != "filter":
                continue
            runs = [simulate(rho, policy, seed) for seed in SEEDS]
            mean = {key: float(np.mean([r[key] for r in runs])) for key in runs[0]}
            # missed images are never sent under "filter", so their delay does not exist
            missed = "   lost" if policy == "filter" else f"{mean['missed_mean']:6.1f}s"
            print(
                f"rho={rho:<4} {policy:<6} p90={mean['p90']:7.2f}s "
                f"missed_mean={missed} lost={mean['lost_pct']:4.1f}% "
                f"sent={mean['sent_pct']:4.0f}%"
            )


if __name__ == "__main__":
    main()
