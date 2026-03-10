"""3D voxel renderer using Ursina engine (Panda3D backend)."""

import os
import sys
import math

# Add parent to path for constants
sys.path.insert(0, os.path.dirname(__file__))

from ursina import (
    Ursina, Entity, Vec3, color, load_texture, Texture,
    DirectionalLight, AmbientLight, Sky, camera, window,
    destroy, scene, held_keys, mouse, application,
    Text, Button, Quad, invoke
)
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina import Audio
import numpy as np

from constants import (
    BLOCK_AIR, BLOCK_GRASS, BLOCK_DIRT, BLOCK_STONE, BLOCK_SAND,
    BLOCK_WATER, BLOCK_WOOD, BLOCK_LEAVES, BLOCK_COBBLESTONE, BLOCK_PLANK,
    BLOCK_GLASS, BLOCK_BEDROCK, BLOCK_COAL_ORE, BLOCK_IRON_ORE,
    BLOCK_GOLD_ORE, BLOCK_DIAMOND_ORE, BLOCK_GRAVEL, BLOCK_SNOW,
    BLOCK_ICE, BLOCK_CACTUS, BLOCK_LAVA,
    CHUNK_SIZE, CHUNK_HEIGHT, RENDER_DISTANCE, NON_SOLID_BLOCKS,
    TRANSPARENT_BLOCKS, BLOCK_NAMES, HOTBAR_SIZE
)
from texture_gen import generate_all_textures


ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "textures")
TEXTURE_CACHE = {}


def ensure_textures():
    if not os.path.exists(ASSETS_DIR) or not os.listdir(ASSETS_DIR):
        print("Generating textures...")
        generate_all_textures(ASSETS_DIR)


def get_texture(name):
    if name not in TEXTURE_CACHE:
        path = os.path.join(ASSETS_DIR, f"{name}.png")
        if os.path.exists(path):
            TEXTURE_CACHE[name] = load_texture(path)
        else:
            TEXTURE_CACHE[name] = None
    return TEXTURE_CACHE[name]


def block_texture(block_id, face="side"):
    """Get texture for a block face."""
    mapping = {
        BLOCK_GRASS:       {"top": "grass_top", "side": "grass_side", "bottom": "dirt"},
        BLOCK_DIRT:        "dirt",
        BLOCK_STONE:       "stone",
        BLOCK_SAND:        "sand",
        BLOCK_WATER:       "water",
        BLOCK_WOOD:        {"top": "wood_top", "side": "wood_side", "bottom": "wood_top"},
        BLOCK_LEAVES:      "leaves",
        BLOCK_COBBLESTONE: "cobblestone",
        BLOCK_PLANK:       "planks",
        BLOCK_GLASS:       "glass",
        BLOCK_BEDROCK:     "bedrock",
        BLOCK_COAL_ORE:    "coal_ore",
        BLOCK_IRON_ORE:    "iron_ore",
        BLOCK_GOLD_ORE:    "gold_ore",
        BLOCK_DIAMOND_ORE: "diamond_ore",
        BLOCK_GRAVEL:      "gravel",
        BLOCK_SNOW:        "snow",
        BLOCK_ICE:         "ice",
        BLOCK_CACTUS:      "cactus",
        BLOCK_LAVA:        "lava",
    }
    val = mapping.get(block_id, "stone")
    if isinstance(val, dict):
        name = val.get(face, val.get("side", "stone"))
    else:
        name = val
    return get_texture(name)


class VoxelBlock(Entity):
    """A single rendered voxel block."""

    def __init__(self, world_x, world_y, world_z, block_id):
        tex = block_texture(block_id, "side")
        alpha = 0.7 if block_id in TRANSPARENT_BLOCKS - {BLOCK_AIR} else 1.0
        super().__init__(
            model="cube",
            position=Vec3(world_x + 0.5, world_y + 0.5, world_z + 0.5),
            texture=tex,
            color=color.white if tex else self._default_color(block_id),
        )
        self.block_id = block_id
        self.world_pos = (world_x, world_y, world_z)

    def _default_color(self, bid):
        from constants import BLOCK_COLORS
        c = BLOCK_COLORS.get(bid, [(128, 128, 128)])[0]
        return color.rgba(c[0]/255, c[1]/255, c[2]/255, 1)


class ChunkMesh:
    """Manages block entities for a single chunk, with face culling."""

    def __init__(self, chunk, world):
        self.chunk = chunk
        self.world = world
        self.entities = []
        self._built = False

    def build(self):
        """Build/rebuild all visible block entities."""
        for e in self.entities:
            destroy(e)
        self.entities = []

        cx, cz = self.chunk.cx, self.chunk.cz
        blocks = self.chunk.blocks

        for (lx, ly, lz), bid in blocks.items():
            if bid == BLOCK_AIR:
                continue
            wx = cx * CHUNK_SIZE + lx
            wz = cz * CHUNK_SIZE + lz
            # Face culling: only render if at least one neighbor is air/transparent
            neighbors = [
                (wx+1, ly, wz), (wx-1, ly, wz),
                (wx, ly+1, wz), (wx, ly-1, wz),
                (wx, ly, wz+1), (wx, ly, wz-1),
            ]
            visible = any(
                self.world.get_block(nx, ny, nz) in TRANSPARENT_BLOCKS
                for (nx, ny, nz) in neighbors
            )
            if visible:
                e = VoxelBlock(wx, ly, wz, bid)
                self.entities.append(e)
        self._built = True

    def destroy(self):
        for e in self.entities:
            destroy(e)
        self.entities = []
        self._built = False


class BreakEffect(Entity):
    """Simple particle effect when a block is broken."""

    def __init__(self, pos, block_color):
        super().__init__(
            model="sphere",
            position=Vec3(pos[0] + 0.5, pos[1] + 0.5, pos[2] + 0.5),
            scale=0.3,
            color=block_color,
        )
        invoke(destroy, self, delay=0.3)


class HUD:
    """Heads-up display: hotbar, crosshair, block name, coordinates."""

    def __init__(self, player):
        self.player = player
        self.hotbar_bg = Entity(
            model="quad",
            scale=(0.55, 0.055),
            position=(0, -0.43),
            parent=camera.ui,
            color=color.rgba(0, 0, 0, 0.5),
        )
        self.slot_entities = []
        self.slot_labels = []
        for i in range(HOTBAR_SIZE):
            x = -0.22 + i * 0.055
            slot = Entity(
                model="quad",
                scale=0.05,
                position=(x, -0.43),
                parent=camera.ui,
                color=color.rgba(0.3, 0.3, 0.3, 0.7),
            )
            label = Text(
                text="",
                position=(x - 0.015, -0.405),
                scale=0.5,
                parent=camera.ui,
            )
            self.slot_entities.append(slot)
            self.slot_labels.append(label)

        self.selector = Entity(
            model="quad",
            scale=0.057,
            position=(0, -0.43),
            parent=camera.ui,
            color=color.rgba(1, 1, 1, 0.5),
        )

        # Crosshair
        self.ch_h = Entity(
            model="quad",
            scale=(0.025, 0.003),
            position=(0, 0),
            parent=camera.ui,
            color=color.white,
        )
        self.ch_v = Entity(
            model="quad",
            scale=(0.003, 0.025),
            position=(0, 0),
            parent=camera.ui,
            color=color.white,
        )

        # Info text
        self.info_text = Text(
            text="",
            position=(-0.85, 0.45),
            scale=0.7,
            parent=camera.ui,
            color=color.white,
        )
        self.block_name_text = Text(
            text="",
            position=(-0.05, -0.36),
            scale=0.7,
            parent=camera.ui,
            color=color.white,
        )

    def update(self):
        inv = self.player.inventory
        for i in range(HOTBAR_SIZE):
            slot_data = inv.slots[i]
            if slot_data:
                bid, count = slot_data
                self.slot_labels[i].text = str(count) if count < 64 else ""
                from constants import BLOCK_COLORS
                c = BLOCK_COLORS.get(bid, [(128, 128, 128)])[0]
                self.slot_entities[i].color = color.rgba(c[0]/255*0.6, c[1]/255*0.6, c[2]/255*0.6, 0.9)
            else:
                self.slot_labels[i].text = ""
                self.slot_entities[i].color = color.rgba(0.3, 0.3, 0.3, 0.7)

        # Move selector
        x = -0.22 + inv.hotbar_index * 0.055
        self.selector.position = (x, -0.43)

        # Selected block name
        sel = inv.selected_block()
        self.block_name_text.text = BLOCK_NAMES.get(sel, "")

        # Coords
        p = self.player
        cx, cz = p.chunk_x, p.chunk_z
        mode = "FLY" if p.fly_mode else ("SWIM" if p.in_water else "WALK")
        self.info_text.text = (
            f"XYZ: {p.x:.1f} / {p.y:.1f} / {p.z:.1f}\n"
            f"Chunk: {cx}, {cz}  Mode: {mode}\n"
            f"[F] Fly  [Tab] Inventory  [Esc] Menu"
        )
