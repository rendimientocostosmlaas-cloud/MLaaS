import csv
import os
import time
import psutil
import subprocess
from datetime import datetime

OUTPUT_FILE = "resource_monitor.csv"
INTERVAL = 5   # segundos

# Encabezado del CSV
header = [
    "timestamp",
    "gpu_utilization_percent",
    "gpu_memory_utilization_percent",
    "gpu_memory_used_mib",
    "gpu_memory_total_mib",
    "gpu_temperature_c",
    "gpu_power_w",
    "cpu_percent",
    "ram_percent",
    "ram_used_gb",
    "ram_total_gb",
    "disk_read_mb",
    "disk_write_mb",
    "disk_read_count",
    "disk_write_count",
    "disk_usage_percent",
    "network_sent_mb",
    "network_recv_mb"
]

if not os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, "w", newline="") as f:
        csv.writer(f).writerow(header)

last_disk = psutil.disk_io_counters()
last_net = psutil.net_io_counters()

print("Monitor iniciado...")
print("Guardando en:", OUTPUT_FILE)

while True:

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ---------------- GPU ----------------

    try:
        gpu = subprocess.check_output([
            "nvidia-smi",
            "--query-gpu=utilization.gpu,utilization.memory,memory.used,memory.total,temperature.gpu,power.draw",
            "--format=csv,noheader,nounits"
        ]).decode().strip().split(", ")

    except:
        gpu = ["","","","","",""]

    # ---------------- CPU ----------------

    cpu = psutil.cpu_percent(interval=1)

    # ---------------- RAM ----------------

    ram = psutil.virtual_memory()

    ram_percent = ram.percent
    ram_used = ram.used / (1024**3)
    ram_total = ram.total / (1024**3)

    # ---------------- Disco ----------------

    disk = psutil.disk_io_counters()

    read_mb = (disk.read_bytes-last_disk.read_bytes)/(1024**2)
    write_mb = (disk.write_bytes-last_disk.write_bytes)/(1024**2)

    read_count = disk.read_count-last_disk.read_count
    write_count = disk.write_count-last_disk.write_count

    last_disk = disk

    disk_usage = psutil.disk_usage("/").percent

    # ---------------- Red ----------------

    net = psutil.net_io_counters()

    sent_mb = (net.bytes_sent-last_net.bytes_sent)/(1024**2)
    recv_mb = (net.bytes_recv-last_net.bytes_recv)/(1024**2)

    last_net = net

    row = [
        timestamp,
        *gpu,
        cpu,
        ram_percent,
        round(ram_used,2),
        round(ram_total,2),
        round(read_mb,3),
        round(write_mb,3),
        read_count,
        write_count,
        disk_usage,
        round(sent_mb,3),
        round(recv_mb,3)
    ]

    with open(OUTPUT_FILE,"a",newline="") as f:
        csv.writer(f).writerow(row)

    time.sleep(INTERVAL-1)
