"""Pin the game to Intel P-cores on hybrid Intel CPUs via taskset."""

import os
from protonfixes import util
from typing import Optional  # keep Optional; drop deprecated Tuple


def main() -> None:
    util.disable_protonmediaconverter()

    p_cores = get_intel_p_cores()
    if p_cores is not None:
        util.set_environment('taskset', f'-c {p_cores[0]}-{p_cores[1]}')


def get_intel_p_cores() -> Optional[tuple[int, int]]:
    # Maps Intel CPU generation numbers to their respective names
    INTEL_GEN_MODEL_CODES = (
        151,  # 12th Gen (Alder Lake)
        183,  # 13th Gen (Raptor Lake)
        190,  # 14th Gen (Raptor Lake Refresh)
        201,  # 15th Gen (Arrow Lake, early)
    )

    # Check if the CPU is Intel and is an appropriate generation
    with open('/proc/cpuinfo') as f:
        cpu_info = f.readlines()
        is_intel = False

        for line in cpu_info:
            if line.startswith('vendor_id') and 'GenuineIntel' in line:
                is_intel = True
                break

        # Return None if not Intel CPU
        if not is_intel:
            return None

        # Set is_intel back to false in case the generation test fails
        is_intel = False
        for line in cpu_info:
            if line.startswith('model'):
                for code in INTEL_GEN_MODEL_CODES:
                    if f': {code}' in line:
                        is_intel = True
                        break
            if is_intel:
                break

        # Return None if CPU is not in supported generations
        if not is_intel:
            return None

        # If the test succeeds, we proceed to return a list of P-cores in the CPU
        # Start by checking the number of CPU cores
        cpu_count = os.cpu_count()
        if cpu_count is None:
            return None

        p_cores: list[int] = []
        for core in range(1, cpu_count, 2):
            try:
                with open(
                    f'/sys/devices/system/cpu/cpu{core}/topology/core_cpus_list'
                ) as core_file:
                    core_type = core_file.read().strip()
                    thread_list = core_type.split('-')

                    if len(thread_list) == 2:
                        p_cores.extend([int(thread_list[0]), int(thread_list[1])])
            except FileNotFoundError:
                # If the core_type file doesn't exist, we can't determine core type
                return None

        if not p_cores:
            return None

        return (p_cores[0], p_cores[-1])
