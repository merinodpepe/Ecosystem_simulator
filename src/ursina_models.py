#!/usr/bin/env python3
"""
3D agent models for the Ursina terrain viewer.
Dummy models built from primitives, colored by guild.

Usage (from viewer):
    from ursina_models import Agent3D
    agent = Agent3D(agent_id=1, species_key="Rupicapra_pyrenaica",
                    nick="Isard", guild="HERBIVORE", x=100, y=200,
                    terrain_height_fn=my_height_fn)
"""

from ursina import *
from ursina.models.procedural.cone import Cone

on_click_callback = None


GUILD_COLORS = {
    "HERBIVORE": color.hex("#4ade80"),  # green
    "CARNIVORE": color.hex("#dc2626"),  # red
    "OMNIVORE": color.hex("#f97316"),  # orange
    "BIRD": color.hex("#3b82f6"),  # blue
    "FISH": color.hex("#64748b"),  # slate
}

GUILD_SHAPES = {
    "HERBIVORE": "sphere",
    "CARNIVORE": "cube",
    "OMNIVORE": "sphere",
    "BIRD": Cone(),
}


def darken(col, factor=0.7):
    return color.rgb(col.r * factor, col.g * factor, col.b * factor)


class Agent3D(Entity):
    """3D representation of a simulation agent."""

    def __init__(
        self,
        agent_id,
        species_key,
        nick,
        guild,
        x=0,
        y=0,
        terrain_height_fn=None,
        scale=1.0,
        **kwargs,
    ):
        super().__init__(
            collider="box",
            **kwargs,
        )
        self.agent_id = agent_id
        self.species_key = species_key
        self.nick = nick
        self.guild = guild
        self.body_color = GUILD_COLORS.get(guild, color.white)
        self.move_speed = 3.0
        self.target_pos = self.position
        self.is_alive = True
        self.stats = {"energy": 0, "age": 0}

        # Body (main shape)
        shape = GUILD_SHAPES.get(guild, "sphere")
        body_scale = {
            "HERBIVORE": Vec3(0.6, 0.35, 0.35),
            "CARNIVORE": Vec3(0.5, 0.35, 0.5),
            "OMNIVORE": Vec3(0.55, 0.35, 0.4),
            "BIRD": Vec3(0.3, 0.1, 0.5),
        }.get(guild, Vec3(0.4, 0.3, 0.3))

        self.body = Entity(
            parent=self,
            model=shape,
            scale=body_scale * scale,
            color=self.body_color,
        )

        # Head (secondary shape)
        if guild == "BIRD":
            # Beak
            self.head = Entity(
                parent=self,
                model=Cone(),
                scale=Vec3(0.15, 0.08, 0.05) * scale,
                position=Vec3(0.2, 0, 0) * scale,
                rotation=Vec3(0, 0, -90),
                color=color.hex("#fbbf24"),
            )
        else:
            self.head = Entity(
                parent=self,
                model=Cone(),
                scale=Vec3(0.25, 0.15, 0.15) * scale,
                position=Vec3(0.3, 0.08, 0) * scale,
                rotation=Vec3(0, 0, -90),
                color=darken(self.body_color, 0.8),
            )

        # Shadow
        self.shadow = Entity(
            parent=self,
            model="circle",
            scale=Vec3(0.7, 1, 0.7) * scale,
            color=color.rgba(0, 0, 0, 60),
            y=-0.1 * scale,
        )

        # Label
        self.label = Text(
            text=nick,
            parent=self,
            scale=1.5,
            billboard=True,
            position=Vec3(0, 1.0, 0) * scale,
            color=color.white,
            outline=color.black,
        )

        # Place on terrain
        self.teleport_to(x, y, terrain_height_fn)

    def on_click(self):
        if on_click_callback:
            on_click_callback(self)

    def teleport_to(self, x, y, terrain_height_fn=None):
        """Instantly move to grid position (x, y)."""
        if terrain_height_fn:
            h = terrain_height_fn(x, y)
        else:
            h = 0
        z = -y
        self.position = Vec3(x, h, z)
        self.target_pos = self.position

    def move_to(self, x, y, terrain_height_fn=None):
        """Set target position for smooth movement."""
        if terrain_height_fn:
            h = terrain_height_fn(x, y)
        else:
            h = 0
        z = -y
        self.target_pos = Vec3(x, h, z)

    def update(self):
        """Called every frame by Ursina: smooth movement + orientation."""
        if not self.is_alive:
            return

        # Smooth interpolation toward target
        diff = self.target_pos - self.position
        dist = diff.length()
        if dist > 0.05:
            step = min(1, time.dt * self.move_speed)
            self.position += diff * step

        # Face movement direction
        if dist > 0.3:
            self.look_at_2d(self.target_pos)

        # Bobbing animation (subtle vertical oscillation)
        if dist > 0.1:
            bob = math.sin(time.time() * 6) * 0.02
            self.y += bob


class AgentDebug(Agent3D):
    """Agent that follows a predefined path for testing."""

    def __init__(self, path_points, **kwargs):
        super().__init__(**kwargs)
        self.path = path_points
        self.path_index = 0
        self.path_timer = 0

    def update(self):
        super().update()
        # Move along path every N seconds
        self.path_timer += time.dt
        if self.path_timer > 1.0 and self.path:
            self.path_timer = 0
            px, py = self.path[self.path_index]
            self.move_to(px, py)
            self.path_index = (self.path_index + 1) % len(self.path)
