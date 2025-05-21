import os
import json
import csv
import glob
import zipfile
from datetime import datetime, timedelta
from typing import Optional, Iterator, Dict
import threading

class Logger:
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        self.log_dir = config.get('log_dir', './logs')
        self.filename_pattern = config.get('filename_pattern', 'sensors_%Y%m%d_%H%M%S.csv')
        self.buffer_size = config.get('buffer_size', 200)
        self.rotate_every_hours = config.get('rotate_every_hours', 24)
        self.max_size_mb = config.get('max_size_mb', 10)
        self.rotate_after_lines = config.get('rotate_after_lines', None)
        self.retention_days = config.get('retention_days', 30)
        
        self._buffer = []
        self._lock = threading.Lock()
        self._current_file = None
        self._current_filename = None
        self._file_start_time = None
        self._last_rotation_time = datetime.now()
        self._is_running = False
        
        os.makedirs(self.log_dir, exist_ok=True)
        self.archive_dir = os.path.join(self.log_dir, 'archive')
        os.makedirs(self.archive_dir, exist_ok=True)

        self._file = None 
        self._csv_writer = None

    def start(self):
        with self._lock:
            if self._is_running:
                return
            self._open_new_log_file()
            self._is_running = True

    def stop(self):
        with self._lock:
            if not self._is_running:
                return
            self._flush_buffer()
            if self._file:
                self._file.close()
                self._file = None
            self._is_running = False

    def log_reading(self, sensor_id: str, timestamp: datetime, value: float, unit: str):
        entry = {
            'timestamp': timestamp.isoformat(),
            'sensor_id': sensor_id,
            'value': value,
            'unit': unit
        }
        with self._lock:
            if not self._is_running:
                self.start()
            self._buffer.append(entry)
            if len(self._buffer) >= self.buffer_size:
                self._flush_buffer()
            self._check_rotation()

    def read_logs(self, start: datetime, end: datetime, sensor_id: Optional[str] = None) -> Iterator[Dict]:
        # Lista plików logów (obecne + archiwum ZIP)
        files = glob.glob(os.path.join(self.log_dir, '*.csv'))
        zip_files = glob.glob(os.path.join(self.archive_dir, '*.zip'))
        all_files = files + zip_files

        for file_path in all_files:
            # Obsługa plików ZIP
            if file_path.endswith('.zip'):
                with zipfile.ZipFile(file_path, 'r') as zipf:
                    for name in zipf.namelist():
                        with zipf.open(name) as f:
                            reader = csv.DictReader(line.decode('utf-8') for line in f)
                            for row in reader:
                                yield self._parse_log_row(row, start, end, sensor_id)
            else:
                with open(file_path, 'r', newline='') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        yield self._parse_log_row(row, start, end, sensor_id)

    # --- Metody prywatne ---
    def _parse_log_row(self, row: Dict, start: datetime, end: datetime, sensor_id: Optional[str]):
        try:
            timestamp = datetime.fromisoformat(row['timestamp'])
        except Exception:
            return None
        if start <= timestamp <= end:
            if sensor_id is None or row['sensor_id'] == sensor_id:
                return {
                    'timestamp': timestamp,
                    'sensor_id': row['sensor_id'],
                    'value': float(row['value']),
                    'unit': row['unit']
                }
        return None

    def _open_new_log_file(self):
        filename = datetime.now().strftime(self.filename_pattern)
        filepath = os.path.join(self.log_dir, filename)
        self._current_filename = filepath
        self._file_start_time = datetime.now()
        self._last_rotation_time = datetime.now()
        self._file = open(filepath, 'a', newline='', encoding='utf-8')
        self._csv_writer = csv.writer(self._file)
        # Zapisz nagłówek jeśli plik jest nowy
        if self._file.tell() == 0:
            self._csv_writer.writerow(['timestamp', 'sensor_id', 'value', 'unit'])

    def _flush_buffer(self):
        if not self._buffer:
            return
        for entry in self._buffer:
            self._csv_writer.writerow([
                entry['timestamp'],
                entry['sensor_id'],
                entry['value'],
                entry['unit']
            ])
        self._file.flush()
        self._buffer.clear()

    def _check_rotation(self):
        now = datetime.now()
        # Rotacja co określony czas
        if (now - self._last_rotation_time).total_seconds() >= self.rotate_every_hours * 3600:
            self._rotate_log()

        # Rotacja na podstawie rozmiaru pliku
        if self._file and os.path.getsize(self._current_filename) >= self.max_size_mb * 1024 * 1024:
            self._rotate_log()

        # Rotacja na podstawie liczby wpisów
        if self.rotate_after_lines is not None:
            # Jeśli w pliku jest więcej niż rotate_after_lines
            if os.path.exists(self._current_filename):
                with open(self._current_filename, 'r', encoding='utf-8') as f:
                    line_count = sum(1 for line in f) - 1  # minus nagłówek
                if line_count >= self.rotate_after_lines:
                    self._rotate_log()

    def _rotate_log(self):
        # Zamknij bieżący plik
        if self._file:
            self._flush_buffer()
            self._file.close()
            self._file = None
        # Przenieś plik do archiwum
        timestamp_str = self._file_start_time.strftime('%Y%m%d_%H%M%S')
        archive_name = f"{os.path.basename(self._current_filename).replace('.csv', '')}_{timestamp_str}.zip"
        archive_path = os.path.join(self.archive_dir, archive_name)

        # ZIP archiwizacja
        with zipfile.ZipFile(archive_path, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(self._current_filename, arcname=os.path.basename(self._current_filename))
        # Usunięcie oryginalnego pliku
        os.remove(self._current_filename)

        # Usuwanie starych archiwów
        self._clean_old_archives()

        # Otwarcie nowego pliku
        self._open_new_log_file()
        self._last_rotation_time = datetime.now()

    def _clean_old_archives(self):
        cutoff = datetime.now() - timedelta(days=self.retention_days)
        for zip_path in glob.glob(os.path.join(self.archive_dir, '*.zip')):
            try:
                mtime = datetime.fromtimestamp(os.path.getmtime(zip_path))
                if mtime < cutoff:
                    os.remove(zip_path)
            except Exception:
                continue

