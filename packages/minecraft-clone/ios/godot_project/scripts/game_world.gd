## DragonMind Craft - Main World Manager (Godot 4)
## Manages chunk loading/unloading and provides world API

extends Node3D

class_name GameWorld

const CHUNK_SIZE := 16
const RENDER_DISTANCE := 4

var generator: WorldGenerator
var loaded_chunks: Dictionary = {}  # Vector2i(cx,cz) -> ChunkRenderer
var world_blocks: Dictionary = {}   # Global: Vector3i -> block_id
var player: PlayerController

@export var render_distance: int = RENDER_DISTANCE
@export var world_seed: int = 42

func _ready():
    generator = WorldGenerator.new(world_seed)
    add_child(generator)
    _find_player()

func _find_player():
    player = get_node_or_null("../Player")
    if player:
        player.block_broken.connect(_on_block_broken)
        player.block_placed.connect(_on_block_placed)

func _process(_delta: float):
    if player:
        var cx = floori(player.global_position.x / CHUNK_SIZE)
        var cz = floori(player.global_position.z / CHUNK_SIZE)
        _update_chunks(cx, cz)

func _update_chunks(cx: int, cz: int):
    var needed := {}
    for dx in range(-render_distance, render_distance + 1):
        for dz in range(-render_distance, render_distance + 1):
            needed[Vector2i(cx + dx, cz + dz)] = true

    # Load new chunks
    for key in needed:
        if not loaded_chunks.has(key):
            _load_chunk(key.x, key.y)

    # Unload distant chunks
    var to_remove := []
    for key in loaded_chunks:
        if not needed.has(key):
            to_remove.append(key)
    for key in to_remove:
        loaded_chunks[key].queue_free()
        loaded_chunks.erase(key)

func _load_chunk(cx: int, cz: int):
    var key = Vector2i(cx, cz)
    var chunk_blocks = generator.generate_chunk(cx, cz)

    # Store in global dict
    for local_pos in chunk_blocks:
        var wx = cx * CHUNK_SIZE + local_pos.x
        var wz = cz * CHUNK_SIZE + local_pos.z
        world_blocks[Vector3i(wx, local_pos.y, wz)] = chunk_blocks[local_pos]

    # Create renderer
    var renderer = ChunkRenderer.new()
    add_child(renderer)
    renderer.setup(cx, cz, chunk_blocks)
    loaded_chunks[key] = renderer

func get_block(wx: int, wy: int, wz: int) -> int:
    return world_blocks.get(Vector3i(wx, wy, wz), 0)

func set_block(wx: int, wy: int, wz: int, block_id: int):
    var global_pos = Vector3i(wx, wy, wz)
    if block_id == 0:
        world_blocks.erase(global_pos)
    else:
        world_blocks[global_pos] = block_id

    # Rebuild affected chunk
    var cx = floori(float(wx) / CHUNK_SIZE)
    var cz = floori(float(wz) / CHUNK_SIZE)
    for dcx in range(-1, 2):
        for dcz in range(-1, 2):
            var key = Vector2i(cx + dcx, cz + dcz)
            if loaded_chunks.has(key):
                var renderer = loaded_chunks[key]
                # Rebuild local blocks for this chunk
                var chunk_blocks = {}
                for gpos in world_blocks:
                    var lcx = floori(float(gpos.x) / CHUNK_SIZE)
                    var lcz = floori(float(gpos.z) / CHUNK_SIZE)
                    if lcx == key.x and lcz == key.y:
                        var lx = gpos.x - key.x * CHUNK_SIZE
                        var lz = gpos.z - key.y * CHUNK_SIZE
                        chunk_blocks[Vector3i(lx, gpos.y, lz)] = world_blocks[gpos]
                renderer.blocks = chunk_blocks
                renderer.build_mesh(self)

func _on_block_broken(_block_id: int, pos: Vector3i):
    set_block(pos.x, pos.y, pos.z, 0)

func _on_block_placed(block_id: int, pos: Vector3i):
    set_block(pos.x, pos.y, pos.z, block_id)

func get_surface_y(wx: int, wz: int) -> int:
    for y in range(63, -1, -1):
        if get_block(wx, y, wz) != 0:
            return y
    return 0
