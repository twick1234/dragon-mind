## DragonMind Craft - World Generator (Godot 4 GDScript)
## Procedural voxel world generation using FastNoiseLite

extends Node

class_name WorldGenerator

const CHUNK_SIZE := 16
const CHUNK_HEIGHT := 64
const SEA_LEVEL := 12

enum Block {
    AIR = 0,
    GRASS = 1,
    DIRT = 2,
    STONE = 3,
    SAND = 4,
    WATER = 5,
    WOOD = 6,
    LEAVES = 7,
    COBBLESTONE = 8,
    PLANKS = 9,
    GLASS = 10,
    BEDROCK = 11,
    COAL_ORE = 12,
    IRON_ORE = 13,
    GOLD_ORE = 14,
    DIAMOND_ORE = 15,
    SNOW = 16,
    GRAVEL = 17,
    LAVA = 18,
    CACTUS = 19,
}

var terrain_noise: FastNoiseLite
var cave_noise: FastNoiseLite
var ore_noise: FastNoiseLite
var biome_noise: FastNoiseLite
var world_seed: int = 42

func _init(seed_val: int = 42):
    world_seed = seed_val
    _setup_noise()

func _setup_noise():
    terrain_noise = FastNoiseLite.new()
    terrain_noise.seed = world_seed
    terrain_noise.noise_type = FastNoiseLite.TYPE_PERLIN
    terrain_noise.frequency = 0.02
    terrain_noise.fractal_octaves = 4
    terrain_noise.fractal_lacunarity = 2.0
    terrain_noise.fractal_gain = 0.5

    cave_noise = FastNoiseLite.new()
    cave_noise.seed = world_seed + 1
    cave_noise.noise_type = FastNoiseLite.TYPE_PERLIN
    cave_noise.frequency = 0.08

    ore_noise = FastNoiseLite.new()
    ore_noise.seed = world_seed + 2
    ore_noise.noise_type = FastNoiseLite.TYPE_SIMPLEX_SMOOTH
    ore_noise.frequency = 0.1

    biome_noise = FastNoiseLite.new()
    biome_noise.seed = world_seed + 3
    biome_noise.noise_type = FastNoiseLite.TYPE_PERLIN
    biome_noise.frequency = 0.005

func get_biome(wx: float, wz: float) -> String:
    var b = biome_noise.get_noise_2d(wx, wz)
    if b < -0.3:
        return "desert"
    elif b < -0.1:
        return "tundra"
    else:
        return "plains"

func get_height(wx: float, wz: float) -> int:
    var h = terrain_noise.get_noise_2d(wx, wz)
    return int(SEA_LEVEL + h * 20)

func generate_chunk(cx: int, cz: int) -> Dictionary:
    """Returns Dictionary[(lx,ly,lz)] -> Block enum value"""
    var blocks := {}
    var rng = RandomNumberGenerator.new()
    rng.seed = world_seed + cx * 1000 + cz

    # Height map
    var heights := {}
    for lx in range(CHUNK_SIZE):
        for lz in range(CHUNK_SIZE):
            var wx = cx * CHUNK_SIZE + lx
            var wz = cz * CHUNK_SIZE + lz
            heights[Vector2i(lx, lz)] = get_height(wx, wz)

    # Fill blocks
    for lx in range(CHUNK_SIZE):
        for lz in range(CHUNK_SIZE):
            var wx = cx * CHUNK_SIZE + lx
            var wz = cz * CHUNK_SIZE + lz
            var surface = heights[Vector2i(lx, lz)]
            var biome = get_biome(wx, wz)

            for ly in range(CHUNK_HEIGHT):
                var pos = Vector3i(lx, ly, lz)
                if ly == 0:
                    blocks[pos] = Block.BEDROCK
                    continue
                if ly > surface:
                    if ly <= SEA_LEVEL:
                        blocks[pos] = Block.WATER if biome != "tundra" else Block.WATER
                    continue

                # Cave check
                var cave_v = cave_noise.get_noise_3d(wx * 0.08, ly * 0.05, wz * 0.08)
                if cave_v > 0.6 and ly > 2 and ly < surface - 2:
                    if ly < 8:
                        blocks[pos] = Block.LAVA
                    continue

                if ly == surface:
                    match biome:
                        "desert": blocks[pos] = Block.SAND
                        "tundra": blocks[pos] = Block.SNOW
                        _: blocks[pos] = Block.GRASS
                elif ly > surface - 4:
                    blocks[pos] = Block.DIRT if biome != "desert" else Block.SAND
                else:
                    var ore_v = ore_noise.get_noise_2d(wx * 0.1 + ly * 0.07, wz * 0.1)
                    if ly < 15 and ore_v > 0.75:
                        blocks[pos] = Block.DIAMOND_ORE
                    elif ly < 25 and ore_v > 0.72:
                        blocks[pos] = Block.GOLD_ORE
                    elif ly < 40 and ore_v > 0.68:
                        blocks[pos] = Block.IRON_ORE
                    elif ore_v > 0.63:
                        blocks[pos] = Block.COAL_ORE
                    else:
                        blocks[pos] = Block.STONE

    # Trees
    for lx in range(2, CHUNK_SIZE - 2):
        for lz in range(2, CHUNK_SIZE - 2):
            var wx = cx * CHUNK_SIZE + lx
            var wz_val = cz * CHUNK_SIZE + lz
            var biome = get_biome(wx, wz_val)
            var surface = heights[Vector2i(lx, lz)]
            var surface_pos = Vector3i(lx, surface, lz)

            if blocks.get(surface_pos, Block.AIR) == Block.GRASS and rng.randf() < 0.02:
                var trunk_h = rng.randi_range(4, 6)
                for i in range(trunk_h):
                    blocks[Vector3i(lx, surface + 1 + i, lz)] = Block.WOOD
                var top = surface + 1 + trunk_h
                for dx in range(-2, 3):
                    for dz2 in range(-2, 3):
                        for dy in range(-1, 3):
                            if abs(dx) + abs(dz2) + abs(dy) <= 3:
                                var bp = Vector3i(lx + dx, top + dy, lz + dz2)
                                if bp.x >= 0 and bp.x < CHUNK_SIZE and bp.z >= 0 and bp.z < CHUNK_SIZE:
                                    if not blocks.has(bp):
                                        blocks[bp] = Block.LEAVES
            elif blocks.get(surface_pos, Block.AIR) == Block.SAND and biome == "desert" and rng.randf() < 0.01:
                var h = rng.randi_range(2, 4)
                for i in range(h):
                    blocks[Vector3i(lx, surface + 1 + i, lz)] = Block.CACTUS

    return blocks
