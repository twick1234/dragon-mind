"""Procedural texture generator - creates Minecraft-style block textures at runtime."""

import random
from PIL import Image, ImageDraw, ImageFilter
from constants import (
    BLOCK_GRASS, BLOCK_DIRT, BLOCK_STONE, BLOCK_SAND, BLOCK_WATER,
    BLOCK_WOOD, BLOCK_LEAVES, BLOCK_COBBLESTONE, BLOCK_PLANK,
    BLOCK_GLASS, BLOCK_BEDROCK, BLOCK_COAL_ORE, BLOCK_IRON_ORE,
    BLOCK_GOLD_ORE, BLOCK_DIAMOND_ORE, BLOCK_GRAVEL, BLOCK_SNOW,
    BLOCK_ICE, BLOCK_CACTUS, BLOCK_LAVA, BLOCK_COLORS
)
import os

TEXTURE_SIZE = 16  # pixels per block face


def _noise_pixel(r, g, b, variance=15, seed=0):
    rng = random.Random(seed)
    nr = max(0, min(255, r + rng.randint(-variance, variance)))
    ng = max(0, min(255, g + rng.randint(-variance, variance)))
    nb = max(0, min(255, b + rng.randint(-variance, variance)))
    return (nr, ng, nb)


def _make_solid(r, g, b, variance=12):
    img = Image.new("RGB", (TEXTURE_SIZE, TEXTURE_SIZE))
    pixels = []
    for y in range(TEXTURE_SIZE):
        for x in range(TEXTURE_SIZE):
            seed = x * 100 + y * 10000
            pixels.append(_noise_pixel(r, g, b, variance, seed))
    img.putdata(pixels)
    return img


def _make_grass_top():
    img = _make_solid(85, 130, 50, 18)
    # Add a few lighter patches
    draw = ImageDraw.Draw(img)
    for _ in range(4):
        x = random.randint(0, 12)
        y = random.randint(0, 12)
        draw.rectangle([x, y, x+2, y+2], fill=(110, 160, 60))
    return img


def _make_grass_side():
    img = Image.new("RGB", (TEXTURE_SIZE, TEXTURE_SIZE))
    # Top 3 pixels = grass green
    top = _make_solid(85, 130, 50, 15)
    dirt = _make_solid(120, 80, 40, 12)
    for y in range(TEXTURE_SIZE):
        for x in range(TEXTURE_SIZE):
            if y < 3:
                img.putpixel((x, y), top.getpixel((x, y)))
            else:
                img.putpixel((x, y), dirt.getpixel((x, y)))
    return img


def _make_stone():
    img = _make_solid(130, 130, 130, 20)
    draw = ImageDraw.Draw(img)
    # Crack lines
    for _ in range(3):
        x1, y1 = random.randint(0, 15), random.randint(0, 15)
        x2, y2 = x1 + random.randint(-4, 4), y1 + random.randint(-4, 4)
        draw.line([x1, y1, x2, y2], fill=(100, 100, 100), width=1)
    return img


def _make_cobblestone():
    img = Image.new("RGB", (TEXTURE_SIZE, TEXTURE_SIZE), (100, 100, 100))
    draw = ImageDraw.Draw(img)
    # Draw cobblestone pattern
    draw.rectangle([0, 0, 7, 7], fill=(115, 115, 115))
    draw.rectangle([8, 0, 15, 7], fill=(95, 95, 95))
    draw.rectangle([0, 8, 7, 15], fill=(90, 90, 90))
    draw.rectangle([8, 8, 15, 15], fill=(110, 110, 110))
    draw.line([0, 8, 15, 8], fill=(70, 70, 70))
    draw.line([8, 0, 8, 15], fill=(70, 70, 70))
    img = img.filter(ImageFilter.GaussianBlur(0.3))
    return img


def _make_wood():
    img = Image.new("RGB", (TEXTURE_SIZE, TEXTURE_SIZE))
    for x in range(TEXTURE_SIZE):
        for y in range(TEXTURE_SIZE):
            base = 110 - abs(x - 7) * 2
            seed = x * 17 + y * 131
            rng = random.Random(seed)
            v = rng.randint(-8, 8)
            r = max(80, min(140, base + v))
            g = max(55, min(100, int(base * 0.72) + v))
            b = max(25, min(55, int(base * 0.36) + v))
            img.putpixel((x, y), (r, g, b))
    return img


def _make_wood_top():
    img = Image.new("RGB", (TEXTURE_SIZE, TEXTURE_SIZE))
    for x in range(TEXTURE_SIZE):
        for y in range(TEXTURE_SIZE):
            dist = ((x - 7.5)**2 + (y - 7.5)**2) ** 0.5
            rng = random.Random(x * 7 + y * 13)
            v = rng.randint(-5, 5)
            if dist < 3:
                r, g, b = 160 + v, 120 + v, 60 + v
            elif dist < 6:
                r, g, b = 130 + v, 95 + v, 45 + v
            else:
                r, g, b = 110 + v, 80 + v, 40 + v
            img.putpixel((x, y), (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))))
    return img


def _make_leaves():
    img = Image.new("RGBA", (TEXTURE_SIZE, TEXTURE_SIZE), (0, 0, 0, 0))
    for x in range(TEXTURE_SIZE):
        for y in range(TEXTURE_SIZE):
            rng = random.Random(x * 31 + y * 97)
            if rng.random() > 0.15:
                v = rng.randint(-20, 20)
                r = max(20, min(80, 40 + v))
                g = max(80, min(140, 110 + v))
                b = max(10, min(50, 25 + v))
                img.putpixel((x, y), (r, g, b, 220))
    return img


def _make_sand():
    img = _make_solid(200, 185, 120, 15)
    return img


def _make_water():
    img = Image.new("RGBA", (TEXTURE_SIZE, TEXTURE_SIZE))
    for x in range(TEXTURE_SIZE):
        for y in range(TEXTURE_SIZE):
            rng = random.Random(x * 23 + y * 47)
            v = rng.randint(-15, 15)
            r = max(20, min(80, 40 + v))
            g = max(60, min(120, 90 + v))
            b = max(160, min(220, 200 + v))
            img.putpixel((x, y), (r, g, b, 180))
    return img


def _make_glass():
    img = Image.new("RGBA", (TEXTURE_SIZE, TEXTURE_SIZE), (180, 220, 240, 100))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, 15, 15], outline=(200, 230, 250, 200))
    return img


def _make_plank():
    img = Image.new("RGB", (TEXTURE_SIZE, TEXTURE_SIZE))
    for y in range(TEXTURE_SIZE):
        plank_y = y % 8
        for x in range(TEXTURE_SIZE):
            rng = random.Random(x * 11 + (y // 8) * 97)
            v = rng.randint(-10, 10)
            if plank_y == 0 or plank_y == 7:
                r, g, b = 140 + v, 105 + v, 55 + v
            else:
                r, g, b = 160 + v, 125 + v, 65 + v
            img.putpixel((x, y), (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))))
    return img


def _make_ore(base_r, base_g, base_b, ore_r, ore_g, ore_b):
    img = _make_stone()
    draw = ImageDraw.Draw(img)
    for _ in range(5):
        x = random.randint(1, 12)
        y = random.randint(1, 12)
        draw.ellipse([x, y, x+2, y+2], fill=(ore_r, ore_g, ore_b))
    return img


def _make_bedrock():
    img = Image.new("RGB", (TEXTURE_SIZE, TEXTURE_SIZE), (20, 20, 20))
    for x in range(TEXTURE_SIZE):
        for y in range(TEXTURE_SIZE):
            rng = random.Random(x * 53 + y * 79)
            if rng.random() > 0.6:
                v = rng.randint(0, 40)
                img.putpixel((x, y), (v, v, v))
    return img


def _make_gravel():
    img = Image.new("RGB", (TEXTURE_SIZE, TEXTURE_SIZE))
    for x in range(TEXTURE_SIZE):
        for y in range(TEXTURE_SIZE):
            rng = random.Random(x * 17 + y * 59)
            v = rng.randint(100, 160)
            img.putpixel((x, y), (v, v-10, v-15))
    return img


def _make_snow():
    return _make_solid(240, 245, 250, 5)


def _make_ice():
    img = Image.new("RGBA", (TEXTURE_SIZE, TEXTURE_SIZE), (150, 200, 230, 200))
    draw = ImageDraw.Draw(img)
    # Crack lines
    for _ in range(2):
        x1, y1 = random.randint(0, 15), random.randint(0, 15)
        x2, y2 = random.randint(0, 15), random.randint(0, 15)
        draw.line([x1, y1, x2, y2], fill=(180, 220, 245, 255))
    return img


def _make_cactus():
    img = Image.new("RGB", (TEXTURE_SIZE, TEXTURE_SIZE))
    for x in range(TEXTURE_SIZE):
        for y in range(TEXTURE_SIZE):
            rng = random.Random(x * 29 + y * 61)
            v = rng.randint(-15, 15)
            if 4 <= x <= 11:
                r, g, b = 45 + v, 140 + v, 50 + v
            else:
                r, g, b = 30, 30, 30  # Transparent edge
            img.putpixel((x, y), (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))))
    return img


def _make_lava():
    img = Image.new("RGB", (TEXTURE_SIZE, TEXTURE_SIZE))
    for x in range(TEXTURE_SIZE):
        for y in range(TEXTURE_SIZE):
            rng = random.Random(x * 41 + y * 83)
            v = rng.randint(-20, 20)
            hot = rng.random() > 0.7
            if hot:
                r, g, b = 255, 200 + v, 50
            else:
                r, g, b = 200 + v, 60, 10
            img.putpixel((x, y), (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))))
    return img


def generate_all_textures(output_dir):
    """Generate all block textures and save as PNG files."""
    os.makedirs(output_dir, exist_ok=True)
    random.seed(42)  # Consistent textures

    textures = {
        f"grass_top": _make_grass_top(),
        f"grass_side": _make_grass_side(),
        f"dirt": _make_solid(120, 80, 40, 12),
        f"stone": _make_stone(),
        f"sand": _make_sand(),
        f"water": _make_water(),
        f"wood_side": _make_wood(),
        f"wood_top": _make_wood_top(),
        f"leaves": _make_leaves(),
        f"cobblestone": _make_cobblestone(),
        f"planks": _make_plank(),
        f"glass": _make_glass(),
        f"bedrock": _make_bedrock(),
        f"coal_ore": _make_ore(130, 130, 130, 30, 30, 30),
        f"iron_ore": _make_ore(130, 130, 130, 180, 150, 120),
        f"gold_ore": _make_ore(130, 130, 130, 220, 190, 50),
        f"diamond_ore": _make_ore(130, 130, 130, 80, 210, 230),
        f"gravel": _make_gravel(),
        f"snow": _make_snow(),
        f"ice": _make_ice(),
        f"cactus": _make_cactus(),
        f"lava": _make_lava(),
    }

    for name, img in textures.items():
        # Scale up for visibility
        img_scaled = img.resize((TEXTURE_SIZE * 4, TEXTURE_SIZE * 4), Image.NEAREST)
        img_scaled.save(os.path.join(output_dir, f"{name}.png"))

    print(f"Generated {len(textures)} textures in {output_dir}")
    return textures


if __name__ == "__main__":
    generate_all_textures("../assets/textures")
