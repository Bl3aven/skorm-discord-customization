#!/usr/bin/env python3
"""Build seamless animated WebP backgrounds from the five SKORM posters."""

from __future__ import annotations

import argparse
import math
import random
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps


ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = ROOT / "assets" / "backgrounds"
OUTPUT_DIR = ROOT / "assets" / "backgrounds-animated"
THEMES = ("cyberpunk", "galaxy", "greek", "hell", "tropical")


@dataclass(frozen=True)
class RenderConfig:
    width: int = 1280
    height: int = 720
    fps: int = 24
    seconds: int = 4
    quality: int = 68

    @property
    def frames(self) -> int:
        return self.fps * self.seconds


def periodic_pulse(phase: float, center: float, width: float) -> float:
    """Return a pulse that is continuous at the animation loop boundary."""
    distance = abs(phase - center)
    distance = min(distance, 1.0 - distance)
    return math.exp(-((distance / width) ** 2))


def glow_layer(
    size: tuple[int, int],
    center: tuple[int, int],
    radius: tuple[int, int],
    color: tuple[int, int, int],
    alpha: int,
    blur: int,
) -> Image.Image:
    mask = Image.new("L", size)
    draw = ImageDraw.Draw(mask)
    x, y = center
    rx, ry = radius
    draw.ellipse((x - rx, y - ry, x + rx, y + ry), fill=max(0, min(255, alpha)))
    mask = mask.filter(ImageFilter.GaussianBlur(blur))
    layer = Image.new("RGBA", size, (*color, 0))
    layer.putalpha(mask)
    return layer


def seeded_particles(
    seed: int,
    count: int,
    width: int,
    height: int,
) -> list[tuple[float, float, float, float, float]]:
    rng = random.Random(seed)
    return [
        (
            rng.random(),
            rng.random(),
            rng.uniform(0.35, 1.0),
            rng.uniform(0.5, 2.0),
            rng.random(),
        )
        for _ in range(count)
    ]


def add_rising_particles(
    frame: Image.Image,
    phase: float,
    particles: list[tuple[float, float, float, float, float]],
    color: tuple[int, int, int],
    *,
    speed: float,
    drift: float,
    streaks: bool = False,
) -> None:
    width, height = frame.size
    layer = Image.new("RGBA", frame.size)
    draw = ImageDraw.Draw(layer)
    for x0, y0, velocity, size, offset in particles:
        local_phase = (phase + offset) % 1.0
        loops = 1 + int(speed > 0.7 and velocity > 0.72)
        x = (x0 * width + math.sin((local_phase + x0) * math.tau) * drift) % width
        y = (y0 * height - local_phase * height * loops) % height
        opacity = int(45 + 175 * math.sin(math.pi * local_phase) ** 2)
        radius = max(1, int(size))
        if streaks:
            draw.line(
                (x, y + radius * 5, x + drift * 0.04, y - radius * 4),
                fill=(*color, opacity),
                width=radius,
            )
        else:
            draw.ellipse(
                (x - radius, y - radius, x + radius, y + radius),
                fill=(*color, opacity),
            )
    blurred = layer.filter(ImageFilter.GaussianBlur(1.2))
    frame.alpha_composite(blurred)
    frame.alpha_composite(layer)


def add_mist(
    frame: Image.Image,
    phase: float,
    color: tuple[int, int, int],
    *,
    opacity: int,
    seed: int,
) -> None:
    width, height = frame.size
    layer = Image.new("RGBA", frame.size)
    draw = ImageDraw.Draw(layer)
    rng = random.Random(seed)
    for index in range(12):
        start_x = rng.uniform(-0.2, 1.0) * width
        y = rng.uniform(0.2, 0.95) * height
        rx = rng.uniform(150, 360)
        ry = rng.uniform(30, 90)
        speed = rng.uniform(0.25, 0.55)
        x = start_x + math.sin((phase + index / 12) * math.tau) * width * speed * 0.22
        alpha = int(opacity * (0.6 + 0.4 * math.sin((phase + index / 12) * math.tau) ** 2))
        draw.ellipse((x - rx, y - ry, x + rx, y + ry), fill=(*color, alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(42))
    frame.alpha_composite(layer)


def add_rain(
    frame: Image.Image,
    phase: float,
    particles: list[tuple[float, float, float, float, float]],
) -> None:
    width, height = frame.size
    layer = Image.new("RGBA", frame.size)
    draw = ImageDraw.Draw(layer)
    for x0, y0, velocity, size, offset in particles:
        local_phase = (phase + offset) % 1.0
        loops = 1 + int(velocity > 0.7)
        x = (x0 * width + math.sin((local_phase + x0) * math.tau) * 28) % width
        y = (y0 * height + local_phase * height * loops) % height
        length = 10 + int(size * 11)
        draw.line(
            (x, y, x - length * 0.28, y + length),
            fill=(100, 225, 255, 38 + int(35 * velocity)),
            width=1,
        )
    frame.alpha_composite(layer)


def add_star_warp(
    frame: Image.Image,
    phase: float,
    particles: list[tuple[float, float, float, float, float]],
) -> None:
    width, height = frame.size
    cx, cy = width * 0.5, height * 0.43
    max_radius = math.hypot(width, height) * 0.72
    layer = Image.new("RGBA", frame.size)
    draw = ImageDraw.Draw(layer)
    for angle_seed, radius_seed, velocity, size, offset in particles:
        angle = angle_seed * math.tau
        local_phase = (phase + offset) % 1.0
        loops = 1 + int(velocity > 0.78)
        radius = ((radius_seed + local_phase * loops) % 1.0) * max_radius
        x = cx + math.cos(angle) * radius
        y = cy + math.sin(angle) * radius * 0.64
        tail = 3 + radius / max_radius * 15
        opacity = int(70 + 170 * radius / max_radius)
        draw.line(
            (
                x - math.cos(angle) * tail,
                y - math.sin(angle) * tail * 0.64,
                x,
                y,
            ),
            fill=(205, 220, 255, opacity),
            width=max(1, int(size)),
        )
    frame.alpha_composite(layer.filter(ImageFilter.GaussianBlur(0.7)))
    frame.alpha_composite(layer)


def add_scan_and_glitch(frame: Image.Image, phase: float) -> None:
    width, height = frame.size
    layer = Image.new("RGBA", frame.size)
    draw = ImageDraw.Draw(layer)
    # Travel fully off-screen before the loop wraps to avoid a visible seam.
    scan_y = int(phase * (height + 160) - 80)
    draw.rectangle((0, scan_y - 2, width, scan_y + 2), fill=(60, 245, 255, 105))
    draw.rectangle((0, scan_y - 24, width, scan_y + 24), fill=(35, 150, 255, 15))
    glitch = max(
        periodic_pulse(phase, 0.18, 0.025),
        periodic_pulse(phase, 0.57, 0.022),
        periodic_pulse(phase, 0.83, 0.018),
    )
    if glitch > 0.08:
        for index, y in enumerate((170, 268, 420, 505)):
            height_band = 3 + index
            color = (255, 35, 185, int(85 * glitch)) if index % 2 else (30, 225, 255, int(75 * glitch))
            offset = int(math.sin((phase * 47 + index) * math.tau) * 55 * glitch)
            draw.rectangle((max(0, offset), y, min(width, width + offset), y + height_band), fill=color)
    frame.alpha_composite(layer)


def render_effects(
    theme: str,
    base: Image.Image,
    phase: float,
    particles: dict[str, list[tuple[float, float, float, float, float]]],
) -> Image.Image:
    frame = base.copy()
    width, height = frame.size
    pulse = 0.5 + 0.5 * math.sin(phase * math.tau)

    if theme == "cyberpunk":
        frame.alpha_composite(
            glow_layer(
                frame.size,
                (width // 2, int(height * 0.39)),
                (235, 170),
                (255, 25, 170),
                int(24 + pulse * 30),
                70,
            )
        )
        add_rain(frame, phase, particles["rain"])
        add_scan_and_glitch(frame, phase)
    elif theme == "galaxy":
        add_star_warp(frame, phase, particles["stars"])
        frame.alpha_composite(
            glow_layer(
                frame.size,
                (width // 2, int(height * 0.4)),
                (250, 210),
                (135, 75, 255),
                int(25 + pulse * 42),
                85,
            )
        )
    elif theme == "greek":
        rays = Image.new("RGBA", frame.size)
        ray_draw = ImageDraw.Draw(rays)
        origin = (width // 2, -40)
        for index, target in enumerate((-180, 80, 310, 530, 760, 1030, 1320, 1520)):
            sway = math.sin((phase + index / 8) * math.tau) * 22
            ray_draw.polygon(
                (
                    origin,
                    (target + sway, height),
                    (target + 100 + sway, height),
                ),
                fill=(255, 228, 145, 10 + int(12 * pulse)),
            )
        frame.alpha_composite(rays.filter(ImageFilter.GaussianBlur(15)))
        add_mist(frame, phase, (255, 240, 205), opacity=23, seed=301)
        add_rising_particles(
            frame,
            phase,
            particles["gold"],
            (255, 214, 105),
            speed=0.42,
            drift=24,
        )
    elif theme == "hell":
        frame.alpha_composite(
            glow_layer(
                frame.size,
                (width // 2, int(height * 0.46)),
                (310, 250),
                (255, 45, 5),
                int(22 + pulse * 42),
                95,
            )
        )
        add_rising_particles(
            frame,
            phase,
            particles["embers"],
            (255, 92, 20),
            speed=0.95,
            drift=40,
            streaks=True,
        )
        add_mist(frame, phase, (130, 15, 3), opacity=18, seed=401)
    elif theme == "tropical":
        add_mist(frame, phase, (185, 255, 225), opacity=25, seed=501)
        add_rising_particles(
            frame,
            phase,
            particles["fireflies"],
            (175, 255, 145),
            speed=0.18,
            drift=36,
        )
        frame.alpha_composite(
            glow_layer(
                frame.size,
                (width // 2, int(height * 0.43)),
                (220, 170),
                (135, 255, 155),
                int(17 + pulse * 25),
                80,
            )
        )
    return frame.convert("RGB")


def build_theme(theme: str, config: RenderConfig, ffmpeg: str) -> Path:
    source = STATIC_DIR / f"{theme}.png"
    output = OUTPUT_DIR / f"{theme}.webp"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with Image.open(source) as image:
        base = ImageOps.fit(
            image.convert("RGBA"),
            (config.width, config.height),
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.5),
        )

    particles = {
        "rain": seeded_particles(101, 110, config.width, config.height),
        "stars": seeded_particles(201, 130, config.width, config.height),
        "gold": seeded_particles(302, 65, config.width, config.height),
        "embers": seeded_particles(402, 90, config.width, config.height),
        "fireflies": seeded_particles(502, 48, config.width, config.height),
    }

    command = [
        ffmpeg,
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-s",
        f"{config.width}x{config.height}",
        "-r",
        str(config.fps),
        "-i",
        "-",
        "-an",
        "-c:v",
        "libwebp_anim",
        "-lossless",
        "0",
        "-quality",
        str(config.quality),
        "-compression_level",
        "4",
        "-loop",
        "0",
        str(output),
    ]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    assert process.stdin is not None
    try:
        for frame_index in range(config.frames):
            phase = frame_index / config.frames
            frame = render_effects(theme, base, phase, particles)
            process.stdin.write(frame.tobytes())
    finally:
        process.stdin.close()
    return_code = process.wait()
    if return_code:
        raise RuntimeError(f"ffmpeg failed for {theme} with exit code {return_code}")
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--theme",
        choices=THEMES,
        action="append",
        help="Render one theme; may be repeated. Defaults to all themes.",
    )
    parser.add_argument("--quality", type=int, default=68)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg is required but was not found")
    config = RenderConfig(quality=max(1, min(100, args.quality)))
    for theme in args.theme or THEMES:
        output = build_theme(theme, config, ffmpeg)
        print(f"{theme}: {output} ({output.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
