#!/usr/bin/env python3
"""
DragonMind Craft - A Minecraft-inspired voxel game
Main game loop and state management.
"""

import os
import sys
import math
import time

# Ensure src dir is on path
sys.path.insert(0, os.path.dirname(__file__))

# Generate textures before Ursina starts
from texture_gen import generate_all_textures
ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "textures")
if not os.path.exists(ASSETS_DIR) or len(os.listdir(ASSETS_DIR)) < 5:
    print("Generating block textures...")
    generate_all_textures(ASSETS_DIR)

from ursina import (
    Ursina, Entity, Vec3, color, camera, window,
    destroy, scene, held_keys, mouse, application,
    DirectionalLight, AmbientLight, Sky, Text, time as utime,
    invoke, raycast
)
from ursina.shaders import lit_with_shadows_shader

from constants import (
    WINDOW_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT, TARGET_FPS,
    CHUNK_SIZE, RENDER_DISTANCE, BLOCK_AIR, BLOCK_NAMES,
    PLAYER_SPEED, BLOCK_GRASS
)
from world import World
from player import Player
from renderer import ChunkMesh, HUD, BreakEffect, TEXTURE_CACHE
from ui import MainMenuUI, PauseMenuUI, InventoryUI, SettingsUI


class GameState:
    MAIN_MENU = "main_menu"
    PLAYING = "playing"
    PAUSED = "paused"
    INVENTORY = "inventory"
    SETTINGS = "settings"


class DragonMindCraft:
    """Main game class managing state and the Ursina app loop."""

    def __init__(self):
        self.app = Ursina(
            title=WINDOW_TITLE,
            borderless=False,
            fullscreen=False,
            size=(WINDOW_WIDTH, WINDOW_HEIGHT),
            vsync=True,
        )
        window.fps_counter.enabled = True
        window.exit_button.visible = False

        self.state = GameState.MAIN_MENU
        self.world = None
        self.player = None
        self.chunk_meshes = {}   # (cx, cz) -> ChunkMesh
        self.hud = None
        self.current_ui = None
        self.render_dist = [RENDER_DISTANCE]  # mutable ref for settings
        self.last_chunk = (None, None)
        self.break_cooldown = 0.0
        self.place_cooldown = 0.0

        self._setup_lighting()
        self._show_main_menu()

    def _setup_lighting(self):
        self.sun = DirectionalLight(
            shadows=False,
            color=color.rgba(1.0, 0.95, 0.8, 1),
        )
        self.sun.look_at(Vec3(1, -2, 1))
        self.ambient = AmbientLight(color=color.rgba(0.4, 0.45, 0.5, 1))
        self.sky = Sky()

    def _clear_ui(self):
        if self.current_ui:
            self.current_ui.destroy()
            self.current_ui = None

    def _show_main_menu(self):
        self._clear_ui()
        mouse.locked = False
        mouse.visible = True
        self.current_ui = MainMenuUI(
            on_play=self._start_game,
            on_settings=lambda: self._show_settings(from_menu=True),
            on_quit=application.quit,
        )

    def _start_game(self):
        self._clear_ui()
        self.state = GameState.PLAYING

        if self.world is None:
            print("Generating world...")
            self.world = World(seed=42)
            self.player = Player(self.world, spawn_x=0, spawn_z=0)

        # Lock mouse
        mouse.locked = True
        mouse.visible = False

        # Initial chunk load
        self._update_chunks()
        self.hud = HUD(self.player)

    def _show_pause_menu(self):
        self._clear_ui()
        mouse.locked = False
        mouse.visible = True
        self.state = GameState.PAUSED
        self.current_ui = PauseMenuUI(
            on_resume=self._resume_game,
            on_settings=lambda: self._show_settings(from_menu=False),
            on_quit_main=self._quit_to_menu,
            on_quit_game=application.quit,
        )

    def _resume_game(self):
        self._clear_ui()
        self.state = GameState.PLAYING
        mouse.locked = True
        mouse.visible = False

    def _quit_to_menu(self):
        self._clear_ui()
        # Destroy world
        for mesh in self.chunk_meshes.values():
            mesh.destroy()
        self.chunk_meshes = {}
        if self.hud:
            # Destroy HUD entities
            for attr in ["hotbar_bg", "selector", "ch_h", "ch_v",
                         "info_text", "block_name_text"]:
                e = getattr(self.hud, attr, None)
                if e:
                    destroy(e)
            for e in self.hud.slot_entities + self.hud.slot_labels:
                destroy(e)
            self.hud = None
        self.world = None
        self.player = None
        self.last_chunk = (None, None)
        self.state = GameState.MAIN_MENU
        self._show_main_menu()

    def _show_inventory(self):
        self._clear_ui()
        self.state = GameState.INVENTORY
        mouse.locked = False
        mouse.visible = True
        self.current_ui = InventoryUI(
            inventory=self.player.inventory,
            on_close=self._close_inventory,
        )

    def _close_inventory(self):
        self._clear_ui()
        self.state = GameState.PLAYING
        mouse.locked = True
        mouse.visible = False

    def _show_settings(self, from_menu=True):
        self._clear_ui()
        self.state = GameState.SETTINGS
        prev_state = GameState.MAIN_MENU if from_menu else GameState.PAUSED

        def on_back():
            if prev_state == GameState.MAIN_MENU:
                self._show_main_menu()
            else:
                self._show_pause_menu()

        self.current_ui = SettingsUI(
            on_back=on_back,
            render_distance_ref=self.render_dist,
        )

    def _update_chunks(self):
        """Load/unload chunks based on player position."""
        if self.player is None:
            return
        cx, cz = self.player.chunk_x, self.player.chunk_z
        if (cx, cz) == self.last_chunk:
            return
        self.last_chunk = (cx, cz)

        rd = self.render_dist[0]
        needed = set()
        for dx in range(-rd, rd + 1):
            for dz in range(-rd, rd + 1):
                needed.add((cx + dx, cz + dz))

        # Load new chunks
        new_chunks = needed - set(self.chunk_meshes.keys())
        for (ncx, ncz) in new_chunks:
            chunk = self.world.get_or_create_chunk(ncx, ncz)
            mesh = ChunkMesh(chunk, self.world)
            mesh.build()
            self.chunk_meshes[(ncx, ncz)] = mesh

        # Unload distant chunks
        to_remove = set(self.chunk_meshes.keys()) - needed
        for key in to_remove:
            self.chunk_meshes[key].destroy()
            del self.chunk_meshes[key]

    def _handle_player_input(self, dt):
        p = self.player
        if p is None:
            return

        # Movement keys
        move_fwd = held_keys["w"] or held_keys["up arrow"]
        move_back = held_keys["s"] or held_keys["down arrow"]
        move_left = held_keys["a"] or held_keys["left arrow"]
        move_right = held_keys["d"] or held_keys["right arrow"]
        jump = held_keys["space"]
        p.sprint = held_keys["left shift"]

        p.update(dt, move_fwd, move_back, move_left, move_right, jump)

        # Mouse look
        if mouse.locked:
            sens = 40.0
            p.yaw += mouse.velocity[0] * sens
            p.pitch = max(-89, min(89, p.pitch - mouse.velocity[1] * sens))

        # Sync camera to player
        camera.position = Vec3(p.x, p.y + 1.62, p.z)
        camera.rotation_y = p.yaw
        camera.rotation_x = p.pitch

        # Block break (left mouse)
        self.break_cooldown -= dt
        if mouse.left and self.break_cooldown <= 0:
            result = p.break_block()
            if result:
                bid, bx, by, bz = result
                from constants import BLOCK_COLORS
                c = BLOCK_COLORS.get(bid, [(128, 128, 128)])[0]
                bc = color.rgba(c[0]/255, c[1]/255, c[2]/255, 1)
                BreakEffect((bx, by, bz), bc)
                # Rebuild affected chunks
                self._rebuild_chunk_at(bx, bz)
            self.break_cooldown = 0.25

        # Block place (right mouse)
        self.place_cooldown -= dt
        if mouse.right and self.place_cooldown <= 0:
            if p.place_block():
                # Get placed position (last block placed)
                result = None  # already placed, rebuild chunks
                # Rebuild nearby chunks
                bx, bz = int(p.x), int(p.z)
                self._rebuild_chunk_at(bx, bz)
            self.place_cooldown = 0.25

    def _rebuild_chunk_at(self, wx, wz):
        """Rebuild chunk mesh at world x,z and neighbors."""
        import math
        cx = int(math.floor(wx / CHUNK_SIZE))
        cz = int(math.floor(wz / CHUNK_SIZE))
        for dcx in range(-1, 2):
            for dcz in range(-1, 2):
                key = (cx + dcx, cz + dcz)
                if key in self.chunk_meshes:
                    mesh = self.chunk_meshes[key]
                    mesh.build()

    def update(self):
        """Called every frame by Ursina."""
        dt = utime.dt
        if dt <= 0:
            dt = 1.0 / TARGET_FPS

        if self.state == GameState.PLAYING:
            self._handle_player_input(dt)
            self._update_chunks()
            if self.hud:
                self.hud.update()

    def input(self, key):
        """Handle key press events."""
        if key == "escape":
            if self.state == GameState.PLAYING:
                self._show_pause_menu()
            elif self.state == GameState.PAUSED:
                self._resume_game()
            elif self.state in (GameState.INVENTORY, GameState.SETTINGS):
                if self.state == GameState.INVENTORY:
                    self._close_inventory()
                else:
                    self._show_pause_menu()

        elif key == "f" and self.state == GameState.PLAYING:
            if self.player:
                self.player.fly_mode = not self.player.fly_mode

        elif key == "tab" and self.state == GameState.PLAYING:
            self._show_inventory()
        elif key == "tab" and self.state == GameState.INVENTORY:
            self._close_inventory()

        # Hotbar number keys
        elif self.state == GameState.PLAYING and self.player:
            for i in range(1, 10):
                if key == str(i):
                    self.player.inventory.select_hotbar(i - 1)

        # Scroll to cycle hotbar
        elif key == "scroll up" and self.state == GameState.PLAYING and self.player:
            self.player.inventory.scroll_hotbar(-1)
        elif key == "scroll down" and self.state == GameState.PLAYING and self.player:
            self.player.inventory.scroll_hotbar(1)

    def run(self):
        self.app.run()


def main():
    game = DragonMindCraft()
    # Register update and input
    game.app.update = game.update
    game.app.input = game.input
    game.run()


if __name__ == "__main__":
    main()
