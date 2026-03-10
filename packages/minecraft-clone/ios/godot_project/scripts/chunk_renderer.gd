## DragonMind Craft - Chunk Renderer (Godot 4)
## Generates optimized mesh for a 16x64x16 chunk with face culling

extends Node3D

class_name ChunkRenderer

const CHUNK_SIZE := 16
const CHUNK_HEIGHT := 64

var chunk_x: int = 0
var chunk_z: int = 0
var blocks: Dictionary = {}
var mesh_instance: MeshInstance3D
var collision_body: StaticBody3D

# Block colors (for procedural coloring without texture atlas)
const BLOCK_COLORS := {
    1:  Color(0.33, 0.51, 0.20),  # GRASS
    2:  Color(0.47, 0.31, 0.16),  # DIRT
    3:  Color(0.51, 0.51, 0.51),  # STONE
    4:  Color(0.78, 0.73, 0.47),  # SAND
    5:  Color(0.12, 0.31, 0.71, 0.7),  # WATER
    6:  Color(0.43, 0.31, 0.16),  # WOOD
    7:  Color(0.16, 0.39, 0.12, 0.85),  # LEAVES
    8:  Color(0.39, 0.39, 0.39),  # COBBLESTONE
    9:  Color(0.65, 0.51, 0.27),  # PLANKS
    10: Color(0.71, 0.86, 0.94, 0.5),  # GLASS
    11: Color(0.12, 0.12, 0.12),  # BEDROCK
    12: Color(0.43, 0.43, 0.43),  # COAL_ORE
    13: Color(0.47, 0.43, 0.39),  # IRON_ORE
    14: Color(0.51, 0.47, 0.31),  # GOLD_ORE
    15: Color(0.31, 0.51, 0.59),  # DIAMOND_ORE
    16: Color(0.94, 0.96, 0.98),  # SNOW
    17: Color(0.55, 0.51, 0.47),  # GRAVEL
    18: Color(0.78, 0.24, 0.04),  # LAVA
    19: Color(0.20, 0.55, 0.20),  # CACTUS
}

const NON_SOLID := [0, 5, 7, 10]  # AIR, WATER, LEAVES, GLASS

func _ready():
    mesh_instance = MeshInstance3D.new()
    add_child(mesh_instance)
    collision_body = StaticBody3D.new()
    add_child(collision_body)

func setup(cx: int, cz: int, chunk_blocks: Dictionary):
    chunk_x = cx
    chunk_z = cz
    blocks = chunk_blocks
    position = Vector3(cx * CHUNK_SIZE, 0, cz * CHUNK_SIZE)
    build_mesh()

func _is_solid(pos: Vector3i) -> bool:
    var bid = blocks.get(pos, 0)
    return bid != 0 and bid not in NON_SOLID

func _get_neighbor(lx: int, ly: int, lz: int, world) -> int:
    var pos = Vector3i(lx, ly, lz)
    if pos in blocks:
        return blocks[pos]
    # Ask world for cross-chunk blocks
    if world:
        var wx = chunk_x * CHUNK_SIZE + lx
        var wz = chunk_z * CHUNK_SIZE + lz
        return world.get_block(wx, ly, wz)
    return 0

func build_mesh(world = null):
    var st = SurfaceTool.new()
    st.begin(Mesh.PRIMITIVE_TRIANGLES)

    var face_dirs := [
        Vector3i(1, 0, 0),   # +X
        Vector3i(-1, 0, 0),  # -X
        Vector3i(0, 1, 0),   # +Y
        Vector3i(0, -1, 0),  # -Y
        Vector3i(0, 0, 1),   # +Z
        Vector3i(0, 0, -1),  # -Z
    ]

    for pos in blocks:
        var bid: int = blocks[pos]
        if bid == 0:
            continue

        var lx: int = pos.x
        var ly: int = pos.y
        var lz: int = pos.z
        var block_color: Color = BLOCK_COLORS.get(bid, Color.GRAY)

        for dir in face_dirs:
            var neighbor_pos = pos + dir
            var neighbor_bid: int = blocks.get(neighbor_pos, 0)

            # Show face if neighbor is air/transparent
            var show_face := false
            if neighbor_bid == 0 or neighbor_bid in NON_SOLID:
                # Edge of chunk - check world
                if neighbor_pos.x < 0 or neighbor_pos.x >= CHUNK_SIZE or \
                   neighbor_pos.z < 0 or neighbor_pos.z >= CHUNK_SIZE:
                    show_face = true  # Show edge faces
                else:
                    show_face = true

            if not show_face:
                continue

            # Face shade for depth perception
            var shade := 1.0
            match dir:
                Vector3i(0, 1, 0): shade = 1.0   # top - brightest
                Vector3i(0, -1, 0): shade = 0.5  # bottom - darkest
                Vector3i(1, 0, 0), Vector3i(-1, 0, 0): shade = 0.75
                _: shade = 0.85

            var fc = Color(block_color.r * shade, block_color.g * shade, block_color.b * shade, block_color.a)
            _add_face(st, lx, ly, lz, dir, fc)

    st.generate_normals()
    var mesh = st.commit()
    mesh_instance.mesh = mesh

    # Generate collision shape
    for child in collision_body.get_children():
        child.queue_free()
    var col_shape = CollisionShape3D.new()
    col_shape.shape = mesh.create_trimesh_shape()
    collision_body.add_child(col_shape)

func _add_face(st: SurfaceTool, x: int, y: int, z: int, dir: Vector3i, fc: Color):
    # Vertices for each face direction
    var verts := _face_verts(x, y, z, dir)
    st.set_color(fc)

    # Two triangles per face
    var uvs := [Vector2(0, 0), Vector2(1, 0), Vector2(1, 1), Vector2(0, 1)]
    for vi in [0, 1, 2, 0, 2, 3]:
        st.set_uv(uvs[vi])
        st.set_color(fc)
        st.add_vertex(verts[vi])

func _face_verts(x: int, y: int, z: int, dir: Vector3i) -> Array:
    var x0 := float(x); var x1 := float(x + 1)
    var y0 := float(y); var y1 := float(y + 1)
    var z0 := float(z); var z1 := float(z + 1)

    match dir:
        Vector3i(1, 0, 0):   # +X face
            return [Vector3(x1,y0,z1), Vector3(x1,y0,z0), Vector3(x1,y1,z0), Vector3(x1,y1,z1)]
        Vector3i(-1, 0, 0):  # -X face
            return [Vector3(x0,y0,z0), Vector3(x0,y0,z1), Vector3(x0,y1,z1), Vector3(x0,y1,z0)]
        Vector3i(0, 1, 0):   # +Y face (top)
            return [Vector3(x0,y1,z0), Vector3(x1,y1,z0), Vector3(x1,y1,z1), Vector3(x0,y1,z1)]
        Vector3i(0, -1, 0):  # -Y face (bottom)
            return [Vector3(x0,y0,z1), Vector3(x1,y0,z1), Vector3(x1,y0,z0), Vector3(x0,y0,z0)]
        Vector3i(0, 0, 1):   # +Z face
            return [Vector3(x0,y0,z1), Vector3(x1,y0,z1), Vector3(x1,y1,z1), Vector3(x0,y1,z1)]
        _:                   # -Z face
            return [Vector3(x1,y0,z0), Vector3(x0,y0,z0), Vector3(x0,y1,z0), Vector3(x1,y1,z0)]
    return []
