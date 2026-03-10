## DragonMind Craft - Touch HUD for iPad (Godot 4)
## Joystick, action buttons, hotbar

extends CanvasLayer

class_name TouchHUD

@onready var joystick_bg = $LeftZone/JoystickBg
@onready var joystick_knob = $LeftZone/JoystickKnob
@onready var btn_jump = $RightZone/BtnJump
@onready var btn_break = $RightZone/BtnBreak
@onready var btn_place = $RightZone/BtnPlace
@onready var btn_fly = $TopBar/BtnFly
@onready var btn_inventory = $TopBar/BtnInventory
@onready var hotbar_container = $BottomBar/Hotbar
@onready var block_name_label = $BottomBar/BlockNameLabel
@onready var coords_label = $TopBar/CoordsLabel
@onready var crosshair = $Crosshair

var player: PlayerController
var joystick_active := false
var joystick_touch_id := -1
var joystick_start := Vector2.ZERO
const JOYSTICK_RADIUS := 80.0

signal jump_pressed
signal break_pressed
signal place_pressed
signal inventory_toggled
signal fly_toggled
signal hotbar_selected(index: int)

func _ready():
    # Only show touch controls on mobile
    visible = OS.has_feature("mobile") or OS.has_feature("web")
    _setup_buttons()

func _setup_buttons():
    if btn_jump:
        btn_jump.button_down.connect(func(): emit_signal("jump_pressed"))
    if btn_break:
        btn_break.button_down.connect(func(): emit_signal("break_pressed"))
    if btn_place:
        btn_place.button_down.connect(func(): emit_signal("place_pressed"))
    if btn_fly:
        btn_fly.pressed.connect(func(): emit_signal("fly_toggled"))
    if btn_inventory:
        btn_inventory.pressed.connect(func(): emit_signal("inventory_toggled"))

func setup_hotbar(inventory: Array, selected: int):
    if not hotbar_container:
        return
    for child in hotbar_container.get_children():
        child.queue_free()
    for i in range(min(9, inventory.size())):
        var item = inventory[i]
        var btn = Button.new()
        btn.text = item["name"].substr(0, 3)
        btn.tooltip_text = item["name"]
        if i == selected:
            btn.add_theme_color_override("font_color", Color.YELLOW)
        btn.pressed.connect(func(idx = i): emit_signal("hotbar_selected", idx))
        hotbar_container.add_child(btn)

func update_coords(x: float, y: float, z: float):
    if coords_label:
        coords_label.text = "%.0f / %.0f / %.0f" % [x, y, z]

func update_block_name(name: String):
    if block_name_label:
        block_name_label.text = name

func get_joystick_direction() -> Vector2:
    if not joystick_active:
        return Vector2.ZERO
    var knob_pos = joystick_knob.position if joystick_knob else Vector2.ZERO
    var bg_pos = joystick_bg.position if joystick_bg else Vector2.ZERO
    var delta = knob_pos - bg_pos
    if delta.length() < 10:
        return Vector2.ZERO
    return delta.normalized()
