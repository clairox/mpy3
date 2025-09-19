import json
import math
import subprocess
import threading
import time
from pathlib import Path

import pyaudio

from mpy3.utils import time_from_ms

CHUNK = 1024
SEEK_INTERVAL_IN_SECONDS = 5


class Media:
    def __init__(self, mrl: Path) -> None:
        self.mrl = mrl
        self.title = mrl.stem
        self.duration = self._get_duration()
        self.meta = None

    def _get_duration(self) -> int:
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

        # ffprobe outputs duration in seconds, we are using milliseconds
        return int(duration * 1000)

    def parse_meta(self) -> None:
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
        self.stopped = False

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
            self.stopped = False
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
            if self.stopped:
                break

            if self.paused:
                continue

            data = self.process.stdout.read(CHUNK)
            if not data:
                break

            self.stream.write(data)
            self.total_bytes_played += len(data)

        self.process.terminate()
        self.stream.stop_stream()
        self.stream.close()
        self.stream = None
        self.process = None

        if self.stopped:
            self.pause_time = None
            self.start_time = None

    def get_time(self) -> int:
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
        if self.process and not self.stopped:
            self.paused = True
            self.stopped = True

    def seek(self, t: float) -> None:
        if self.process is None:
            return

        duration_in_secs = self.media.duration / 1000
        if t < 0:
            t = 0
        elif t > duration_in_secs:
            t = duration_in_secs

        self.process.kill()
        self.process = subprocess.Popen(
            [
                "ffmpeg",
                "-ss",
                str(t),
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

        self.start_time = time.time() - t

        current_sample = round(t * self.sample_rate)
        self.total_bytes_played = current_sample * (
            self.channels * self.bytes_per_sample
        )

        print(time_from_ms(int(t * 1000)))

    def fast_forward(self) -> None:
        self.seek((self.get_time() / 1000) + SEEK_INTERVAL_IN_SECONDS)

    def rewind(self) -> None:
        self.seek((self.get_time() / 1000) - SEEK_INTERVAL_IN_SECONDS)
