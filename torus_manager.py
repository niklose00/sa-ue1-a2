import subprocess
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')


class TorusManager:
    def __init__(self, rows, cols, base_port=5000):
        self.rows = rows
        self.cols = cols
        self.base_port = base_port
        self.processes = []

    def start_torus(self):
        for row in range(self.rows):
            for col in range(self.cols):
                port = self.base_port + row * self.cols + col
                neighbors = [
                    self.base_port + ((row - 1) % self.rows) * self.cols + col,  # Top
                    self.base_port + ((row + 1) % self.rows) * self.cols + col,  # Bottom
                    self.base_port + row * self.cols + (col - 1) % self.cols,    # Left
                    self.base_port + row * self.cols + (col + 1) % self.cols,    # Right
                ]
                process = subprocess.Popen(["python", "glowworm.py", str(port)] + [str(n) for n in neighbors])
                self.processes.append(process)
                logging.info(f"Started process for Glowworm at port {port} with neighbors {neighbors}")
        time.sleep(1)  # Warte, bis alle Prozesse gestartet sind

    def stop_torus(self):
        for process in self.processes:
            process.terminate()
        logging.info("Stopped all Glowworm processes")