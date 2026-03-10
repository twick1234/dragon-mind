"""UI screens: main menu, pause menu, inventory screen, settings."""

from ursina import (
    Entity, Text, Button, Quad, camera, color, destroy,
    window, mouse, application, Vec2
)
from constants import (
    BLOCK_AIR, HOTBAR_SIZE, INVENTORY_ROWS, INVENTORY_COLS,
    BLOCK_NAMES, BLOCK_COLORS
)


def _make_panel(w, h, y=0, alpha=0.85):
    return Entity(
        model="quad",
        scale=(w, h),
        position=(0, y),
        parent=camera.ui,
        color=color.rgba(0.1, 0.1, 0.15, alpha),
    )


class MainMenuUI:
    def __init__(self, on_play, on_settings, on_quit):
        self.entities = []
        bg = _make_panel(2.5, 2.5)
        self.entities.append(bg)

        title = Text(
            text="DragonMind Craft",
            position=(0, 0.3),
            scale=2.5,
            parent=camera.ui,
            color=color.rgba(0.2, 0.8, 0.2, 1),
            origin=(0, 0),
        )
        subtitle = Text(
            text="A Minecraft-inspired voxel adventure",
            position=(0, 0.2),
            scale=1.0,
            parent=camera.ui,
            color=color.rgba(0.8, 0.8, 0.8, 1),
            origin=(0, 0),
        )
        self.entities += [title, subtitle]

        btn_play = Button(
            text="Play",
            position=(0, 0.05),
            scale=(0.3, 0.06),
            parent=camera.ui,
            color=color.rgba(0.2, 0.6, 0.2, 1),
            on_click=on_play,
        )
        btn_settings = Button(
            text="Settings",
            position=(0, -0.05),
            scale=(0.3, 0.06),
            parent=camera.ui,
            color=color.rgba(0.3, 0.3, 0.5, 1),
            on_click=on_settings,
        )
        btn_quit = Button(
            text="Quit",
            position=(0, -0.15),
            scale=(0.3, 0.06),
            parent=camera.ui,
            color=color.rgba(0.6, 0.2, 0.2, 1),
            on_click=on_quit,
        )
        controls = Text(
            text=(
                "Controls:\n"
                "WASD - Move     Mouse - Look\n"
                "Space - Jump    Left Click - Break\n"
                "Right Click - Place    Scroll - Select block\n"
                "F - Toggle fly mode    Tab - Inventory\n"
                "1-9 - Hotbar    Esc - Pause"
            ),
            position=(0, -0.30),
            scale=0.8,
            parent=camera.ui,
            color=color.rgba(0.7, 0.7, 0.7, 1),
            origin=(0, 0),
        )
        self.entities += [btn_play, btn_settings, btn_quit, controls]

    def destroy(self):
        for e in self.entities:
            destroy(e)
        self.entities = []


class PauseMenuUI:
    def __init__(self, on_resume, on_settings, on_quit_main, on_quit_game):
        self.entities = []
        bg = _make_panel(1.0, 0.6, 0)
        self.entities.append(bg)

        title = Text(
            text="Paused",
            position=(0, 0.22),
            scale=2.0,
            parent=camera.ui,
            color=color.white,
            origin=(0, 0),
        )
        self.entities.append(title)

        for label, y, fn, col in [
            ("Resume", 0.10, on_resume, color.rgba(0.2, 0.6, 0.2, 1)),
            ("Settings", 0.02, on_settings, color.rgba(0.3, 0.3, 0.5, 1)),
            ("Main Menu", -0.06, on_quit_main, color.rgba(0.5, 0.3, 0.1, 1)),
            ("Quit Game", -0.14, on_quit_game, color.rgba(0.6, 0.2, 0.2, 1)),
        ]:
            btn = Button(
                text=label,
                position=(0, y),
                scale=(0.28, 0.055),
                parent=camera.ui,
                color=col,
                on_click=fn,
            )
            self.entities.append(btn)

    def destroy(self):
        for e in self.entities:
            destroy(e)
        self.entities = []


class InventoryUI:
    """Full inventory screen with drag-and-drop (click to pick up / place)."""

    CELL = 0.07

    def __init__(self, inventory, on_close):
        self.inventory = inventory
        self.on_close = on_close
        self.entities = []
        self.held_item = None  # (block_id, count, original_slot)
        self.held_label = None
        self._build()

    def _build(self):
        bg = _make_panel(1.1, 0.75)
        self.entities.append(bg)

        title = Text(
            text="Inventory",
            position=(0, 0.33),
            scale=1.2,
            parent=camera.ui,
            color=color.white,
            origin=(0, 0),
        )
        self.entities.append(title)

        self.slot_btns = []
        # Main inventory (3x9)
        for row in range(INVENTORY_ROWS):
            for col in range(INVENTORY_COLS):
                slot_idx = HOTBAR_SIZE + row * INVENTORY_COLS + col
                x = -0.28 + col * self.CELL
                y = 0.20 - row * self.CELL
                btn = self._make_slot_btn(x, y, slot_idx)
                self.slot_btns.append((btn, slot_idx))

        # Hotbar
        for i in range(HOTBAR_SIZE):
            x = -0.28 + i * self.CELL
            y = -0.12
            btn = self._make_slot_btn(x, y, i)
            self.slot_btns.append((btn, i))

        close_btn = Button(
            text="Close [Tab]",
            position=(0, -0.27),
            scale=(0.25, 0.055),
            parent=camera.ui,
            color=color.rgba(0.4, 0.2, 0.2, 1),
            on_click=self.close,
        )
        self.entities.append(close_btn)

    def _make_slot_btn(self, x, y, slot_idx):
        slot_data = self.inventory.slots[slot_idx]
        if slot_data:
            bid, count = slot_data
            c = BLOCK_COLORS.get(bid, [(128, 128, 128)])[0]
            bc = color.rgba(c[0]/255*0.6, c[1]/255*0.6, c[2]/255*0.6, 0.9)
            label = f"{BLOCK_NAMES.get(bid,'?')[:3]}\n{count}"
        else:
            bc = color.rgba(0.25, 0.25, 0.25, 0.8)
            label = ""

        btn = Button(
            text=label,
            position=(x, y),
            scale=(self.CELL * 0.92, self.CELL * 0.92),
            parent=camera.ui,
            color=bc,
            text_size=0.5,
            on_click=lambda si=slot_idx: self._on_click_slot(si),
        )
        self.entities.append(btn)
        return btn

    def _on_click_slot(self, slot_idx):
        slot_data = self.inventory.slots[slot_idx]
        if self.held_item is None:
            if slot_data:
                self.held_item = (slot_data[0], slot_data[1], slot_idx)
                self.inventory.slots[slot_idx] = None
                self._refresh()
        else:
            bid, count, orig = self.held_item
            if slot_data is None:
                self.inventory.slots[slot_idx] = (bid, count)
            else:
                # Swap
                self.inventory.slots[slot_idx] = (bid, count)
                self.held_item = (slot_data[0], slot_data[1], slot_idx)
                self._refresh()
                return
            self.held_item = None
            self._refresh()

    def _refresh(self):
        self.destroy()
        self._build()

    def close(self):
        if self.held_item:
            bid, count, orig = self.held_item
            self.inventory.slots[orig] = (bid, count)
            self.held_item = None
        self.destroy()
        if self.on_close:
            self.on_close()

    def destroy(self):
        for e in self.entities:
            destroy(e)
        self.entities = []
        self.slot_btns = []


class SettingsUI:
    def __init__(self, on_back, render_distance_ref):
        self.entities = []
        self.on_back = on_back
        self.render_dist = render_distance_ref

        bg = _make_panel(1.2, 0.7)
        self.entities.append(bg)

        title = Text(
            text="Settings",
            position=(0, 0.28),
            scale=1.8,
            parent=camera.ui,
            color=color.white,
            origin=(0, 0),
        )
        self.entities.append(title)

        self.rd_label = Text(
            text=f"Render Distance: {self.render_dist[0]}",
            position=(0, 0.12),
            scale=1.0,
            parent=camera.ui,
            color=color.white,
            origin=(0, 0),
        )
        self.entities.append(self.rd_label)

        for label, delta, x in [("-", -1, -0.08), ("+", 1, 0.08)]:
            btn = Button(
                text=label,
                position=(x, 0.05),
                scale=(0.05, 0.05),
                parent=camera.ui,
                color=color.rgba(0.3, 0.3, 0.5, 1),
                on_click=lambda d=delta: self._change_rd(d),
            )
            self.entities.append(btn)

        controls_text = Text(
            text=(
                "Keyboard Shortcuts:\n"
                "WASD: Move        Space: Jump\n"
                "Shift: Sprint     F: Toggle Fly\n"
                "Tab: Inventory    Esc: Pause\n"
                "1-9: Hotbar       Scroll: Cycle blocks\n"
                "LMB: Break block  RMB: Place block"
            ),
            position=(0, -0.07),
            scale=0.75,
            parent=camera.ui,
            color=color.rgba(0.8, 0.8, 0.8, 1),
            origin=(0, 0),
        )
        self.entities.append(controls_text)

        back_btn = Button(
            text="Back",
            position=(0, -0.27),
            scale=(0.2, 0.055),
            parent=camera.ui,
            color=color.rgba(0.4, 0.2, 0.2, 1),
            on_click=self._back,
        )
        self.entities.append(back_btn)

    def _change_rd(self, delta):
        self.render_dist[0] = max(2, min(8, self.render_dist[0] + delta))
        self.rd_label.text = f"Render Distance: {self.render_dist[0]}"

    def _back(self):
        self.destroy()
        if self.on_back:
            self.on_back()

    def destroy(self):
        for e in self.entities:
            destroy(e)
        self.entities = []
