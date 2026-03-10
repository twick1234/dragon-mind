"""World generation and chunk management."""

import random
import math
from constants import (
    BLOCK_AIR, BLOCK_GRASS, BLOCK_DIRT, BLOCK_STONE, BLOCK_SAND,
    BLOCK_WATER, BLOCK_WOOD, BLOCK_LEAVES, BLOCK_BEDROCK,
    BLOCK_COAL_ORE, BLOCK_IRON_ORE, BLOCK_GOLD_ORE, BLOCK_DIAMOND_ORE,
    BLOCK_GRAVEL, BLOCK_SNOW, BLOCK_ICE, BLOCK_CACTUS, BLOCK_LAVA,
    CHUNK_SIZE, CHUNK_HEIGHT, SEA_LEVEL, DIRT_DEPTH,
    TERRAIN_OCTAVES, TERRAIN_FREQUENCY, TERRAIN_AMPLITUDE,
    CAVE_THRESHOLD, TREE_CHANCE, NON_SOLID_BLOCKS
)


class PerlinNoise:
    """Simple 2D Perlin noise implementation."""

    def __init__(self, seed=0):
        self.seed = seed
        rng = random.Random(seed)
        self.perm = list(range(256))
        rng.shuffle(self.perm)
        self.perm *= 2

    def fade(self, t):
        return t * t * t * (t * (t * 6 - 15) + 10)

    def lerp(self, a, b, t):
        return a + t * (b - a)

    def grad(self, h, x, y):
        h = h & 3
        if h == 0: return x + y
        if h == 1: return -x + y
        if h == 2: return x - y
        return -x - y

    def noise(self, x, y):
        xi = int(math.floor(x)) & 255
        yi = int(math.floor(y)) & 255
        xf = x - math.floor(x)
        yf = y - math.floor(y)
        u = self.fade(xf)
        v = self.fade(yf)
        aa = self.perm[self.perm[xi] + yi]
        ab = self.perm[self.perm[xi] + yi + 1]
        ba = self.perm[self.perm[xi + 1] + yi]
        bb = self.perm[self.perm[xi + 1] + yi + 1]
        x1 = self.lerp(self.grad(aa, xf, yf), self.grad(ba, xf - 1, yf), u)
        x2 = self.lerp(self.grad(ab, xf, yf - 1), self.grad(bb, xf - 1, yf - 1), u)
        return (self.lerp(x1, x2, v) + 1) / 2

    def octave_noise(self, x, y, octaves=4, persistence=0.5, lacunarity=2.0):
        total = 0
        frequency = 1
        amplitude = 1
        max_val = 0
        for _ in range(octaves):
            total += self.noise(x * frequency, y * frequency) * amplitude
            max_val += amplitude
            amplitude *= persistence
            frequency *= lacunarity
        return total / max_val


class Chunk:
    """A 16x64x16 section of the world."""

    def __init__(self, cx, cz, world_seed):
        self.cx = cx  # Chunk X coordinate
        self.cz = cz  # Chunk Z coordinate
        self.blocks = {}  # (x, y, z) -> block_id  (local coords)
        self.modified = True
        self._generate(world_seed)

    def _generate(self, world_seed):
        noise = PerlinNoise(world_seed)
        cave_noise = PerlinNoise(world_seed + 1)
        ore_noise = PerlinNoise(world_seed + 2)
        rng = random.Random(world_seed + self.cx * 1000 + self.cz)

        # Generate height map
        height_map = {}
        for lx in range(CHUNK_SIZE):
            for lz in range(CHUNK_SIZE):
                wx = self.cx * CHUNK_SIZE + lx
                wz = self.cz * CHUNK_SIZE + lz
                h = noise.octave_noise(
                    wx * TERRAIN_FREQUENCY,
                    wz * TERRAIN_FREQUENCY,
                    TERRAIN_OCTAVES, 0.5, 2.0
                )
                height_map[(lx, lz)] = int(SEA_LEVEL + h * TERRAIN_AMPLITUDE)

        # Determine biome (simple)
        def get_biome(lx, lz):
            wx = self.cx * CHUNK_SIZE + lx
            wz = self.cz * CHUNK_SIZE + lz
            b = noise.octave_noise(wx * 0.005, wz * 0.005, 2)
            if b < 0.35:
                return "desert"
            elif b < 0.45:
                return "tundra"
            else:
                return "plains"

        # Place blocks
        for lx in range(CHUNK_SIZE):
            for lz in range(CHUNK_SIZE):
                surface_y = height_map[(lx, lz)]
                biome = get_biome(lx, lz)

                for ly in range(CHUNK_HEIGHT):
                    wx = self.cx * CHUNK_SIZE + lx
                    wz = self.cz * CHUNK_SIZE + lz

                    if ly == 0:
                        self.blocks[(lx, ly, lz)] = BLOCK_BEDROCK
                        continue

                    if ly > surface_y:
                        # Above surface - water or air
                        if ly <= SEA_LEVEL:
                            if biome == "tundra":
                                self.blocks[(lx, ly, lz)] = BLOCK_ICE
                            else:
                                self.blocks[(lx, ly, lz)] = BLOCK_WATER
                        # else air (don't add)
                        continue

                    # Cave carving
                    cave = cave_noise.octave_noise(
                        wx * 0.08, wz * 0.08 + ly * 0.05, 2
                    )
                    if cave > CAVE_THRESHOLD and 2 < ly < surface_y - 2:
                        # Lava at bottom of caves
                        if ly < 8:
                            self.blocks[(lx, ly, lz)] = BLOCK_LAVA
                        continue

                    # Surface and subsurface
                    if ly == surface_y:
                        if biome == "desert":
                            self.blocks[(lx, ly, lz)] = BLOCK_SAND
                        elif biome == "tundra":
                            self.blocks[(lx, ly, lz)] = BLOCK_SNOW
                        else:
                            self.blocks[(lx, ly, lz)] = BLOCK_GRASS
                    elif ly > surface_y - DIRT_DEPTH:
                        if biome == "desert":
                            self.blocks[(lx, ly, lz)] = BLOCK_SAND
                        else:
                            self.blocks[(lx, ly, lz)] = BLOCK_DIRT
                    elif ly > surface_y - DIRT_DEPTH - 2:
                        # Gravel layer sometimes
                        if rng.random() < 0.3:
                            self.blocks[(lx, ly, lz)] = BLOCK_GRAVEL
                        else:
                            self.blocks[(lx, ly, lz)] = BLOCK_STONE
                    else:
                        # Stone with ores
                        ore_val = ore_noise.noise(wx * 0.1 + ly * 0.07, wz * 0.1)
                        if ly < 15 and ore_val > 0.75:
                            self.blocks[(lx, ly, lz)] = BLOCK_DIAMOND_ORE
                        elif ly < 25 and ore_val > 0.72:
                            self.blocks[(lx, ly, lz)] = BLOCK_GOLD_ORE
                        elif ly < 40 and ore_val > 0.68:
                            self.blocks[(lx, ly, lz)] = BLOCK_IRON_ORE
                        elif ore_val > 0.63:
                            self.blocks[(lx, ly, lz)] = BLOCK_COAL_ORE
                        else:
                            self.blocks[(lx, ly, lz)] = BLOCK_STONE

        # Trees and features
        for lx in range(2, CHUNK_SIZE - 2):
            for lz in range(2, CHUNK_SIZE - 2):
                surface_y = height_map[(lx, lz)]
                biome = get_biome(lx, lz)
                surface_block = self.blocks.get((lx, surface_y, lz))

                if surface_block == BLOCK_GRASS and rng.random() < TREE_CHANCE:
                    self._place_tree(lx, surface_y + 1, lz, rng)
                elif surface_block == BLOCK_SAND and biome == "desert" and rng.random() < 0.01:
                    # Cactus
                    height = rng.randint(2, 4)
                    for i in range(height):
                        self.blocks[(lx, surface_y + 1 + i, lz)] = BLOCK_CACTUS

    def _place_tree(self, x, y, z, rng):
        trunk_height = rng.randint(4, 6)
        # Trunk
        for i in range(trunk_height):
            self.blocks[(x, y + i, z)] = BLOCK_WOOD
        # Leaves sphere
        top = y + trunk_height
        for lx in range(-2, 3):
            for lz in range(-2, 3):
                for ly in range(-1, 3):
                    if abs(lx) + abs(lz) + abs(ly) <= 3:
                        bx, by, bz = x + lx, top + ly, z + lz
                        if 0 <= bx < CHUNK_SIZE and 0 <= bz < CHUNK_SIZE:
                            if (bx, by, bz) not in self.blocks:
                                self.blocks[(bx, by, bz)] = BLOCK_LEAVES

    def get_block(self, lx, ly, lz):
        return self.blocks.get((lx, ly, lz), BLOCK_AIR)

    def set_block(self, lx, ly, lz, block_id):
        if block_id == BLOCK_AIR:
            self.blocks.pop((lx, ly, lz), None)
        else:
            self.blocks[(lx, ly, lz)] = block_id
        self.modified = True

    def get_surface_y(self, lx, lz):
        for ly in range(CHUNK_HEIGHT - 1, -1, -1):
            if self.blocks.get((lx, ly, lz), BLOCK_AIR) not in NON_SOLID_BLOCKS:
                return ly
        return 0


class World:
    """Manages all chunks and provides a global block interface."""

    def __init__(self, seed=None):
        self.seed = seed if seed is not None else random.randint(0, 999999)
        self.chunks = {}  # (cx, cz) -> Chunk

    def _chunk_key(self, cx, cz):
        return (cx, cz)

    def get_or_create_chunk(self, cx, cz):
        key = self._chunk_key(cx, cz)
        if key not in self.chunks:
            self.chunks[key] = Chunk(cx, cz, self.seed)
        return self.chunks[key]

    def world_to_chunk(self, wx, wz):
        cx = int(math.floor(wx / CHUNK_SIZE))
        cz = int(math.floor(wz / CHUNK_SIZE))
        lx = int(wx) % CHUNK_SIZE
        lz = int(wz) % CHUNK_SIZE
        if lx < 0:
            lx += CHUNK_SIZE
        if lz < 0:
            lz += CHUNK_SIZE
        return cx, cz, lx, lz

    def get_block(self, wx, wy, wz):
        if wy < 0 or wy >= CHUNK_HEIGHT:
            return BLOCK_AIR
        cx, cz, lx, lz = self.world_to_chunk(wx, wz)
        chunk = self.chunks.get(self._chunk_key(cx, cz))
        if chunk is None:
            return BLOCK_AIR
        return chunk.get_block(lx, wy, lz)

    def set_block(self, wx, wy, wz, block_id):
        if wy < 0 or wy >= CHUNK_HEIGHT:
            return
        cx, cz, lx, lz = self.world_to_chunk(wx, wz)
        chunk = self.get_or_create_chunk(cx, cz)
        chunk.set_block(lx, wy, lz, block_id)

    def get_surface_y(self, wx, wz):
        cx, cz, lx, lz = self.world_to_chunk(wx, wz)
        chunk = self.get_or_create_chunk(cx, cz)
        return chunk.get_surface_y(lx, lz)

    def load_chunks_around(self, cx, cz, render_distance):
        for dx in range(-render_distance, render_distance + 1):
            for dz in range(-render_distance, render_distance + 1):
                self.get_or_create_chunk(cx + dx, cz + dz)

    def get_loaded_chunks(self):
        return list(self.chunks.values())
