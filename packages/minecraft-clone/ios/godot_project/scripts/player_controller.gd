## DragonMind Craft - Player Controller (Godot 4 GDScript)
## Handles movement, physics, touch input, and block interaction

extends CharacterBody3D

class_name PlayerController

const MOVE_SPEED := 10.0
const SPRINT_SPEED := 16.0
const JUMP_VELOCITY := 7.0
const GRAVITY := 25.0
const MOUSE_SENSITIVITY := 0.003
const TOUCH_SENSITIVITY := 0.005
const REACH := 5.0

@onready var head: Node3D = $Head
@onready var camera: Camera3D = $Head/Camera3D
@onready var ray: RayCast3D = $Head/Camera3D/RayCast3D
@onready var break_cooldown_timer: Timer = $BreakCooldown
@onready var place_cooldown_timer: Timer = $PlaceCooldown

# Touch input state
var touch_left_id := -1
var touch_right_id := -1
var touch_left_start := Vector2.ZERO
var touch_left_pos := Vector2.ZERO
var touch_right_start := Vector2.ZERO
var touch_right_pos := Vector2.ZERO

var fly_mode := false
var sprint := false
var selected_block := 1  # GRASS by default
var inventory: Array = []

signal block_broken(block_id: int, position: Vector3i)
signal block_placed(block_id: int, position: Vector3i)

func _ready():
    if not OS.has_feature("mobile"):
        Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
    _setup_inventory()

func _setup_inventory():
    inventory = [
        {"id": 1, "count": 64, "name": "Grass"},    # GRASS
        {"id": 2, "count": 64, "name": "Dirt"},     # DIRT
        {"id": 3, "count": 64, "name": "Stone"},    # STONE
        {"id": 4, "count": 64, "name": "Sand"},     # SAND
        {"id": 6, "count": 64, "name": "Wood"},     # WOOD
        {"id": 8, "count": 64, "name": "Cobble"},   # COBBLESTONE
        {"id": 9, "count": 64, "name": "Planks"},   # PLANKS
        {"id": 10, "count": 64, "name": "Glass"},   # GLASS
        {"id": 7, "count": 64, "name": "Leaves"},   # LEAVES
    ]

func _unhandled_input(event: InputEvent):
    # Desktop mouse look
    if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
        rotate_y(-event.relative.x * MOUSE_SENSITIVITY)
        head.rotate_x(-event.relative.y * MOUSE_SENSITIVITY)
        head.rotation.x = clamp(head.rotation.x, -PI/2, PI/2)

    # Desktop keyboard actions
    if event.is_action_pressed("ui_cancel"):
        if Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
            Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
        else:
            Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

    # Touch input
    if event is InputEventScreenTouch:
        _handle_touch(event)
    if event is InputEventScreenDrag:
        _handle_drag(event)

    # Desktop block interaction
    if event is InputEventMouseButton:
        if event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
            _try_break_block()
        if event.pressed and event.button_index == MOUSE_BUTTON_RIGHT:
            _try_place_block()

func _handle_touch(event: InputEventScreenTouch):
    var half_w = get_viewport().size.x / 2.0
    if event.pressed:
        if event.position.x < half_w:
            if touch_left_id == -1:
                touch_left_id = event.index
                touch_left_start = event.position
                touch_left_pos = event.position
        else:
            if touch_right_id == -1:
                touch_right_id = event.index
                touch_right_start = event.position
                touch_right_pos = event.position
    else:
        if event.index == touch_left_id:
            touch_left_id = -1
        elif event.index == touch_right_id:
            touch_right_id = -1

func _handle_drag(event: InputEventScreenDrag):
    var half_w = get_viewport().size.x / 2.0
    if event.index == touch_right_id:
        # Camera look
        touch_right_pos = event.position
        var delta = event.relative
        rotate_y(-delta.x * TOUCH_SENSITIVITY)
        head.rotate_x(-delta.y * TOUCH_SENSITIVITY)
        head.rotation.x = clamp(head.rotation.x, -PI/2, PI/2)
    elif event.index == touch_left_id:
        touch_left_pos = event.position

func _physics_process(delta: float):
    _handle_movement(delta)
    _handle_touch_actions()

func _handle_movement(delta: float):
    var direction := Vector3.ZERO
    var speed = SPRINT_SPEED if sprint else MOVE_SPEED

    # Desktop WASD
    if Input.is_action_pressed("move_forward"):
        direction -= transform.basis.z
    if Input.is_action_pressed("move_backward"):
        direction += transform.basis.z
    if Input.is_action_pressed("move_left"):
        direction -= transform.basis.x
    if Input.is_action_pressed("move_right"):
        direction += transform.basis.x

    # Touch joystick (left side)
    if touch_left_id != -1:
        var stick_delta = touch_left_pos - touch_left_start
        if stick_delta.length() > 10:
            var normalized = stick_delta.normalized()
            direction -= transform.basis.z * normalized.y
            direction += transform.basis.x * normalized.x

    direction = direction.normalized()

    if fly_mode:
        velocity = direction * speed
        if Input.is_action_pressed("jump"):
            velocity.y = speed * 0.6
        else:
            velocity.y = lerp(velocity.y, 0.0, 10.0 * delta)
    else:
        if not is_on_floor():
            velocity.y -= GRAVITY * delta
        else:
            velocity.y = 0
        if Input.is_action_just_pressed("jump") and is_on_floor():
            velocity.y = JUMP_VELOCITY
        velocity.x = direction.x * speed
        velocity.z = direction.z * speed

    move_and_slide()

func _handle_touch_actions():
    # Touch break/place could be handled with button overlays in the scene
    pass

func _try_break_block():
    if not ray.is_colliding():
        return
    var hit_pos = ray.get_collision_point()
    var normal = ray.get_collision_normal()
    var block_pos = Vector3i(
        floori(hit_pos.x - normal.x * 0.5),
        floori(hit_pos.y - normal.y * 0.5),
        floori(hit_pos.z - normal.z * 0.5)
    )
    emit_signal("block_broken", 0, block_pos)

func _try_place_block():
    if not ray.is_colliding():
        return
    var hit_pos = ray.get_collision_point()
    var normal = ray.get_collision_normal()
    var place_pos = Vector3i(
        floori(hit_pos.x + normal.x * 0.5),
        floori(hit_pos.y + normal.y * 0.5),
        floori(hit_pos.z + normal.z * 0.5)
    )
    if selected_block > 0:
        emit_signal("block_placed", selected_block, place_pos)

func toggle_fly():
    fly_mode = !fly_mode

func select_block(idx: int):
    if idx >= 0 and idx < inventory.size():
        selected_block = inventory[idx]["id"]
