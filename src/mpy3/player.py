import json
import math
import subprocess
import threading
import time
from math import floor
from pathlib import Path

import pyaudio

CHUNK = 1024


class Media:
    def __init__(self, mrl: Path) -> None:
        self.mrl = mrl
        self.title = mrl.stem
        self.duration = self._get_duration()
        self.meta = None

    def _get_duration(self):
        result = subprocess.run(
            [
                "ffprobe",
                "-i",
                str(self.mrl),
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "json",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        response_json = result.stdout
        duration = float(
            json.loads(response_json).get("format", {}).get("duration", -1)
        )
        duration_in_millis = floor(duration * 1000)
        return duration_in_millis

    def parse_meta(self):
        result = subprocess.run(
            [
                "ffprobe",
                "-i",
                str(self.mrl),
                "-v",
                "error",
                "-show_entries",
                "format_tags",
                "-of",
                "json",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        meta_json = result.stdout
        self.meta = dict(json.loads(meta_json).get("format", {}).get("tags", {}))

        if self.meta and self.meta["title"]:
            self.title = self.meta["title"]


class MediaPlayer:
    def __init__(self, media: Media) -> None:
        self.media = media

        self.sample_rate = 44100
        self.channels = 2
        self.bytes_per_sample = 2

        self.process = None
        self.stream = None
        self.playback_thread = None
        self.p = pyaudio.PyAudio()
        self.paused = False

        self.start_time = None
        self.pause_time = None
        self.total_bytes_played = 0

    def _start_process(self, start_time: int = 0) -> None:
        self.process = subprocess.Popen(
            [
                "ffmpeg",
                "-ss",
                str(start_time),
                "-i",
                self.media.mrl,
                "-f",
                "s16le",
                "-acodec",
                "pcm_s16le",
                "-ar",
                str(self.sample_rate),
                "-ac",
                str(self.channels),
                "pipe:1",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )

        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            output=True,
        )

    def play_until_done(self) -> None:
        print(f"Playing {self.media.mrl.name}")

        if self.process is None:
            self._start_process()
            self.start_time = time.time()
            self.total_bytes_played = 0
            self.playback_thread = threading.Thread(target=self._playback)
            self.playback_thread.start()
            self.paused = False
        elif self.paused:
            if self.pause_time is None:
                raise ValueError('"self.pause_time" has not been set.')

            if self.start_time is None:
                raise ValueError('"self.start_time" has not been set.')

            self.paused = False
            self.start_time += time.time() - self.pause_time

    def _playback(self) -> None:
        if self.process is None or self.process.stdout is None:
            raise ValueError('"self.process" has not been set.')

        if self.stream is None:
            raise ValueError('"self.stream" has not been set.')

        while True:
            if self.paused:
                continue

            data = self.process.stdout.read(CHUNK)
            if not data:
                break

            self.stream.write(data)
            self.total_bytes_played += len(data)

        self.stream = None
        self.process = None

        self.paused = True
        self.pause_time = time.time()

    def get_time(self) -> float:
        if self.start_time is None:
            return 0

        if self.paused:
            if self.pause_time is None:
                raise ValueError('"self.pause_time" has not been set.')

            elapsed = self.pause_time - self.start_time
        else:
            elapsed = time.time() - self.start_time

        samples_played = self.total_bytes_played / (
            self.channels * self.bytes_per_sample
        )
        time_from_bytes = samples_played / self.sample_rate

        t = math.floor(min(max(elapsed, time_from_bytes) * 1000, self.media.duration))

        return t

    def pause(self) -> None:
        if self.process and not self.paused:
            self.paused = True
            self.pause_time = time.time()

    def stop(self) -> None:
        if self.stream is None or self.process is None:
            return

        self.stream.stop_stream()
        self.stream = None
        self.process = None

        self.paused = True
        self.pause_time = None
        self.start_time = None

    def seek(self) -> None:
        pass

    def fast_forward(self) -> None:
        pass

    def rewind(self) -> None:
        pass
