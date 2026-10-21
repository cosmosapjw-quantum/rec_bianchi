"""Read-only cooperative resource sampling; never touch unrelated processes."""
import math
import os
import time
from pathlib import Path

GIB = 1024**3


def _text(path):
    try:
        return Path(path).read_text().strip()
    except OSError:
        return None


def effective_cpus():
    affinity = len(os.sched_getaffinity(0)) if hasattr(os, 'sched_getaffinity') else (os.cpu_count() or 1)
    quota = _text('/sys/fs/cgroup/cpu.max')
    count = float(affinity)
    if quota:
        q, period = quota.split()
        if q != 'max':
            count = min(count, int(q)/int(period))
    else:
        q, p = _text('/sys/fs/cgroup/cpu/cpu.cfs_quota_us'), _text('/sys/fs/cgroup/cpu/cpu.cfs_period_us')
        if q and p and int(q) > 0:
            count = min(count, int(q)/int(p))
    return max(1, math.floor(count))


def memory():
    data = {}
    for line in Path('/proc/meminfo').read_text().splitlines():
        key, value = line.split(':', 1)
        data[key] = int(value.split()[0])*1024
    total, available = data['MemTotal'], data.get('MemAvailable', data['MemFree'])
    maximum, current = _text('/sys/fs/cgroup/memory.max'), _text('/sys/fs/cgroup/memory.current')
    if maximum and maximum != 'max' and current:
        total = min(total, int(maximum))
        available = min(available, max(0, int(maximum)-int(current)))
    return total, available


def cpu_ticks(stat_text=None, affinity=None):
    """Ticks only from CPUs this process is permitted to use."""
    if affinity is None:
        affinity = os.sched_getaffinity(0)
    rows = (Path('/proc/stat').read_text() if stat_text is None else stat_text).splitlines()
    total = idle = found = 0
    for row in rows:
        fields = row.split()
        if fields and fields[0].startswith('cpu') and fields[0][3:].isdigit():
            if int(fields[0][3:]) in affinity:
                ticks = [int(v) for v in fields[1:9]]
                total += sum(ticks)
                idle += ticks[3]+ticks[4]
                found += 1
    if not found:
        raise RuntimeError('NO_AFFINITY_CPU_TICKS_OBSERVED')
    return total, idle


def allocation(profile, requested, effective, total, available, idle_fraction):
    ceiling = min(4 if profile == 'sandbox' else 63, effective,
                  requested if requested is not None else effective)
    reserve = 16*GIB if total >= 120*GIB else max(GIB, .1*total)
    memory_slots = max(0, math.floor((available-reserve)/(.5*GIB)))
    # One nice worker is allowed on a busy CPU when memory permits.
    cpu_slots = max(1, math.floor(effective*max(0., min(1., idle_fraction))))
    return max(0, min(ceiling, memory_slots, cpu_slots))


class Sampler:
    def __init__(self):
        self.previous = cpu_ticks()
        # No idle measurement yet: allow at most one nice worker.
        self.idle = 0.

    def sample(self, profile, requested=None):
        now = cpu_ticks()
        if now[0] > self.previous[0]:
            self.idle = (now[1]-self.previous[1])/(now[0]-self.previous[0])
        self.previous = now
        total, available = memory()
        cpus = effective_cpus()
        return {'effective_cpus': cpus, 'memory_total_bytes': total,
                'memory_available_bytes': available, 'idle_fraction': self.idle,
                'slots': allocation(profile, requested, cpus, total, available, self.idle),
                'observed_monotonic': time.monotonic()}
