"""Player controller with physics, collision, raycast, and inventory."""

import math
from constants import (
    PLAYER_SPEED, PLAYER_SPRINT_SPEED, PLAYER_JUMP_HEIGHT,
    PLAYER_HEIGHT, PLAYER_REACH, GRAVITY,
    BLOCK_AIR, BLOCK_WATER, BLOCK_LAVA, NON_SOLID_BLOCKS,
    HOTBAR_SIZE, INVENTORY_ROWS, INVENTORY_COLS,
    BLOCK_GRASS, BLOCK_DIRT, BLOCK_STONE, BLOCK_SAND, BLOCK_WOOD,
    BLOCK_COBBLESTONE, BLOCK_PLANK, BLOCK_GLASS, BLOCK_LEAVES,
    CHUNK_HEIGHT
)


class Inventory:
    """Player inventory with hotbar and main inventory."""

    TOTAL_SLOTS = HOTBAR_SIZE + INVENTORY_ROWS * INVENTORY_COLS

    def __init__(self):
        # Each slot: (block_id, count) or None
        self.slots = [None] * self.TOTAL_SLOTS
        self.hotbar_index = 0
        # Default starting items
        self._add_defaults()

    def _add_defaults(self):
        defaults = [
            (BLOCK_GRASS, 64),
            (BLOCK_DIRT, 64),
            (BLOCK_STONE, 64),
            (BLOCK_SAND, 64),
            (BLOCK_WOOD, 64),
            (BLOCK_COBBLESTONE, 64),
            (BLOCK_PLANK, 64),
            (BLOCK_GLASS, 64),
            (BLOCK_LEAVES, 64),
        ]
        for i, item in enumerate(defaults):
            if i < self.TOTAL_SLOTS:
                self.slots[i] = item

    @property
    def hotbar(self):
        return self.slots[:HOTBAR_SIZE]

    def selected_block(self):
        slot = self.slots[self.hotbar_index]
        if slot and slot[1] > 0:
            return slot[0]
        return BLOCK_AIR

    def add_block(self, block_id, count=1):
        # Try stacking into existing slot
        for i, slot in enumerate(self.slots):
            if slot and slot[0] == block_id and slot[1] < 64:
                can_add = min(count, 64 - slot[1])
                self.slots[i] = (block_id, slot[1] + can_add)
                count -= can_add
                if count <= 0:
                    return True
        # Find empty slot
        for i, slot in enumerate(self.slots):
            if slot is None:
                take = min(count, 64)
                self.slots[i] = (block_id, take)
                count -= take
                if count <= 0:
                    return True
        return False  # Inventory full

    def remove_block(self, hotbar_idx, count=1):
        if self.slots[hotbar_idx] is None:
            return
        block_id, current = self.slots[hotbar_idx]
        new_count = current - count
        if new_count <= 0:
            self.slots[hotbar_idx] = None
        else:
            self.slots[hotbar_idx] = (block_id, new_count)

    def scroll_hotbar(self, direction):
        self.hotbar_index = (self.hotbar_index + direction) % HOTBAR_SIZE

    def select_hotbar(self, index):
        if 0 <= index < HOTBAR_SIZE:
            self.hotbar_index = index


class Player:
    """Player with position, physics, collision detection, and raycast."""

    def __init__(self, world, spawn_x=0, spawn_z=0):
        self.world = world
        sy = world.get_surface_y(int(spawn_x), int(spawn_z))
        self.x = float(spawn_x)
        self.y = float(sy + 2)
        self.z = float(spawn_z)
        self.vx = 0.0
        self.vy = 0.0
        self.vz = 0.0
        self.yaw = 0.0    # degrees, horizontal rotation
        self.pitch = 0.0  # degrees, vertical rotation (-90 to 90)
        self.on_ground = False
        self.in_water = False
        self.fly_mode = False
        self.sprint = False
        self.inventory = Inventory()
        self.health = 20
        self.hunger = 20

    @property
    def chunk_x(self):
        return int(math.floor(self.x / 16))

    @property
    def chunk_z(self):
        return int(math.floor(self.z / 16))

    def get_look_vector(self):
        """Return normalized direction vector player is looking."""
        yaw_r = math.radians(self.yaw)
        pitch_r = math.radians(self.pitch)
        dx = math.sin(yaw_r) * math.cos(pitch_r)
        dy = -math.sin(pitch_r)
        dz = math.cos(yaw_r) * math.cos(pitch_r)
        return dx, dy, dz

    def raycast(self, max_dist=None):
        """
        Cast a ray from player eyes and return:
        (hit_block_x, hit_block_y, hit_block_z, prev_x, prev_y, prev_z)
        or None if no block hit.
        """
        if max_dist is None:
            max_dist = PLAYER_REACH
        dx, dy, dz = self.get_look_vector()
        ex = self.x
        ey = self.y + PLAYER_HEIGHT * 0.9  # eye height
        ez = self.z
        steps = int(max_dist / 0.05)
        px, py, pz = int(math.floor(ex)), int(math.floor(ey)), int(math.floor(ez))

        for i in range(1, steps + 1):
            t = i * 0.05
            wx = ex + dx * t
            wy = ey + dy * t
            wz = ez + dz * t
            bx, by, bz = int(math.floor(wx)), int(math.floor(wy)), int(math.floor(wz))
            block = self.world.get_block(bx, by, bz)
            if block != BLOCK_AIR and block not in NON_SOLID_BLOCKS:
                return bx, by, bz, px, py, pz
            px, py, pz = bx, by, bz
        return None

    def _aabb(self):
        """Player AABB as (min_x, min_y, min_z, max_x, max_y, max_z)."""
        hw = 0.3
        return (
            self.x - hw, self.y, self.z - hw,
            self.x + hw, self.y + PLAYER_HEIGHT, self.z + hw
        )

    def _check_collision_axis(self, nx, ny, nz):
        """Check if position (nx,ny,nz) collides with solid blocks."""
        hw = 0.3
        for bx in range(int(math.floor(nx - hw)), int(math.floor(nx + hw)) + 1):
            for by in range(int(math.floor(ny)), int(math.floor(ny + PLAYER_HEIGHT)) + 1):
                for bz in range(int(math.floor(nz - hw)), int(math.floor(nz + hw)) + 1):
                    block = self.world.get_block(bx, by, bz)
                    if block not in NON_SOLID_BLOCKS and block != BLOCK_AIR:
                        return True
        return False

    def _is_in_water(self):
        head_y = int(math.floor(self.y + PLAYER_HEIGHT * 0.5))
        bx = int(math.floor(self.x))
        bz = int(math.floor(self.z))
        return self.world.get_block(bx, head_y, bz) == BLOCK_WATER

    def update(self, dt, move_forward, move_backward, move_left, move_right, jump):
        """Update player physics and position."""
        if dt <= 0:
            return

        speed = PLAYER_SPRINT_SPEED if self.sprint else PLAYER_SPEED
        self.in_water = self._is_in_water()

        if self.in_water:
            speed *= 0.4
            gravity = GRAVITY * 0.15
        else:
            gravity = GRAVITY

        # Compute move direction from yaw
        yaw_r = math.radians(self.yaw)
        fwd_x = math.sin(yaw_r)
        fwd_z = math.cos(yaw_r)
        right_x = math.cos(yaw_r)
        right_z = -math.sin(yaw_r)

        move_x = 0.0
        move_z = 0.0
        if move_forward:
            move_x += fwd_x
            move_z += fwd_z
        if move_backward:
            move_x -= fwd_x
            move_z -= fwd_z
        if move_right:
            move_x += right_x
            move_z += right_z
        if move_left:
            move_x -= right_x
            move_z -= right_z

        # Normalize
        mag = math.sqrt(move_x**2 + move_z**2)
        if mag > 0:
            move_x /= mag
            move_z /= mag

        if self.fly_mode:
            self.vx = move_x * speed
            self.vz = move_z * speed
            if jump:
                self.vy = speed * 0.6
            elif move_backward and move_forward:
                self.vy = 0
            else:
                self.vy *= 0.8
        else:
            self.vx = move_x * speed
            self.vz = move_z * speed
            # Gravity
            self.vy += gravity * dt
            if self.in_water:
                self.vy = max(self.vy, -3)
            # Jump
            if jump and (self.on_ground or self.in_water):
                self.vy = PLAYER_JUMP_HEIGHT * (5 if not self.in_water else 3)

        # Move X
        nx = self.x + self.vx * dt
        if not self._check_collision_axis(nx, self.y, self.z):
            self.x = nx
        else:
            self.vx = 0

        # Move Z
        nz = self.z + self.vz * dt
        if not self._check_collision_axis(self.x, self.y, nz):
            self.z = nz
        else:
            self.vz = 0

        # Move Y
        ny = self.y + self.vy * dt
        if not self._check_collision_axis(self.x, ny, self.z):
            self.y = ny
            self.on_ground = False
        else:
            if self.vy < 0:
                self.on_ground = True
            self.vy = 0

        # Clamp to world bounds
        self.y = max(0, min(self.y, CHUNK_HEIGHT - 2))

    def place_block(self):
        """Place block at position in front of player. Returns True on success."""
        result = self.raycast()
        if result is None:
            return False
        _, _, _, px, py, pz = result
        # Don't place inside player
        hw = 0.4
        pmin = (px, py, pz)
        pmax = (px + 1, py + 1, pz + 1)
        player_min = (self.x - hw, self.y, self.z - hw)
        player_max = (self.x + hw, self.y + PLAYER_HEIGHT, self.z + hw)
        # AABB overlap check
        overlap = (
            player_min[0] < pmax[0] and player_max[0] > pmin[0] and
            player_min[1] < pmax[1] and player_max[1] > pmin[1] and
            player_min[2] < pmax[2] and player_max[2] > pmin[2]
        )
        if overlap:
            return False
        block_id = self.inventory.selected_block()
        if block_id == BLOCK_AIR:
            return False
        self.world.set_block(px, py, pz, block_id)
        self.inventory.remove_block(self.inventory.hotbar_index)
        return True

    def break_block(self):
        """Break block player is looking at. Returns (block_id, x, y, z) or None."""
        result = self.raycast()
        if result is None:
            return None
        bx, by, bz, _, _, _ = result
        block_id = self.world.get_block(bx, by, bz)
        if block_id == BLOCK_AIR:
            return None
        self.world.set_block(bx, by, bz, BLOCK_AIR)
        self.inventory.add_block(block_id)
        return block_id, bx, by, bz
