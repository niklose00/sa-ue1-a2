from torus_manager import TorusManager
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

if __name__ == "__main__":
    manager = TorusManager(rows=3, cols=3)
    try:
        logging.info("Starte Glühwürmchen-Torus...")
        manager.start_torus()
        input("Drücken Sie Enter, um die Simulation zu beenden...\n")
    finally:
        logging.info("Stoppe Glühwürmchen-Torus...")
        manager.stop_torus()
