"""Game constants for DragonMind Craft (Minecraft Clone)"""

# Window settings
WINDOW_TITLE = "DragonMind Craft"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
TARGET_FPS = 60

# World generation
CHUNK_SIZE = 16          # Width/depth of a chunk in blocks
CHUNK_HEIGHT = 64        # Max height of world
RENDER_DISTANCE = 4      # Chunks rendered around player
SEA_LEVEL = 12
DIRT_DEPTH = 4

# Block IDs
BLOCK_AIR = 0
BLOCK_GRASS = 1
BLOCK_DIRT = 2
BLOCK_STONE = 3
BLOCK_SAND = 4
BLOCK_WATER = 5
BLOCK_WOOD = 6
BLOCK_LEAVES = 7
BLOCK_COBBLESTONE = 8
BLOCK_PLANK = 9
BLOCK_GLASS = 10
BLOCK_BEDROCK = 11
BLOCK_COAL_ORE = 12
BLOCK_IRON_ORE = 13
BLOCK_GOLD_ORE = 14
BLOCK_DIAMOND_ORE = 15
BLOCK_GRAVEL = 16
BLOCK_SNOW = 17
BLOCK_ICE = 18
BLOCK_CACTUS = 19
BLOCK_LAVA = 20

# Block colors (R, G, B) for procedural texture generation
BLOCK_COLORS = {
    BLOCK_GRASS:       [(85, 130, 50), (60, 100, 30)],   # top, side
    BLOCK_DIRT:        [(120, 80, 40), (120, 80, 40)],
    BLOCK_STONE:       [(130, 130, 130), (130, 130, 130)],
    BLOCK_SAND:        [(200, 185, 120), (200, 185, 120)],
    BLOCK_WATER:       [(30, 80, 180), (30, 80, 180)],
    BLOCK_WOOD:        [(110, 80, 40), (110, 80, 40)],
    BLOCK_LEAVES:      [(40, 100, 30), (40, 100, 30)],
    BLOCK_COBBLESTONE: [(100, 100, 100), (100, 100, 100)],
    BLOCK_PLANK:       [(165, 130, 70), (165, 130, 70)],
    BLOCK_GLASS:       [(180, 220, 240), (180, 220, 240)],
    BLOCK_BEDROCK:     [(30, 30, 30), (30, 30, 30)],
    BLOCK_COAL_ORE:    [(110, 110, 110), (110, 110, 110)],
    BLOCK_IRON_ORE:    [(120, 110, 100), (120, 110, 100)],
    BLOCK_GOLD_ORE:    [(130, 120, 80), (130, 120, 80)],
    BLOCK_DIAMOND_ORE: [(100, 130, 150), (100, 130, 150)],
    BLOCK_GRAVEL:      [(140, 130, 120), (140, 130, 120)],
    BLOCK_SNOW:        [(240, 245, 250), (240, 245, 250)],
    BLOCK_ICE:         [(150, 200, 230), (150, 200, 230)],
    BLOCK_CACTUS:      [(50, 140, 50), (50, 140, 50)],
    BLOCK_LAVA:        [(200, 60, 10), (200, 60, 10)],
}

BLOCK_NAMES = {
    BLOCK_GRASS: "Grass",
    BLOCK_DIRT: "Dirt",
    BLOCK_STONE: "Stone",
    BLOCK_SAND: "Sand",
    BLOCK_WATER: "Water",
    BLOCK_WOOD: "Wood",
    BLOCK_LEAVES: "Leaves",
    BLOCK_COBBLESTONE: "Cobblestone",
    BLOCK_PLANK: "Planks",
    BLOCK_GLASS: "Glass",
    BLOCK_BEDROCK: "Bedrock",
    BLOCK_COAL_ORE: "Coal Ore",
    BLOCK_IRON_ORE: "Iron Ore",
    BLOCK_GOLD_ORE: "Gold Ore",
    BLOCK_DIAMOND_ORE: "Diamond Ore",
    BLOCK_GRAVEL: "Gravel",
    BLOCK_SNOW: "Snow",
    BLOCK_ICE: "Ice",
    BLOCK_CACTUS: "Cactus",
    BLOCK_LAVA: "Lava",
}

# Non-solid / transparent blocks
TRANSPARENT_BLOCKS = {BLOCK_AIR, BLOCK_WATER, BLOCK_GLASS, BLOCK_LEAVES, BLOCK_ICE}
NON_SOLID_BLOCKS = {BLOCK_AIR, BLOCK_WATER, BLOCK_LAVA}

# Player settings
PLAYER_SPEED = 10
PLAYER_SPRINT_SPEED = 16
PLAYER_JUMP_HEIGHT = 2.5
PLAYER_HEIGHT = 1.8
PLAYER_REACH = 5.0
GRAVITY = -25

# Hotbar
HOTBAR_SIZE = 9
INVENTORY_ROWS = 3
INVENTORY_COLS = 9

# Noise settings for terrain generation
TERRAIN_OCTAVES = 4
TERRAIN_FREQUENCY = 0.02
TERRAIN_AMPLITUDE = 20
CAVE_THRESHOLD = 0.6
TREE_CHANCE = 0.02
