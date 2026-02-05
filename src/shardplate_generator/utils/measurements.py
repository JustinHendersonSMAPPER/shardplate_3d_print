"""Human body measurements for armor sizing."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class HumanMeasurements:
    """Human body measurements for properly sizing armor pieces.

    All measurements are in meters. Default values are for an average adult.
    Scale factor can be applied for 3D printing at different sizes.
    """

    # Overall dimensions
    height: float = 1.75  # Total body height

    # Head measurements
    head_circumference: float = 0.57  # Around forehead
    head_length: float = 0.20  # Front to back
    head_width: float = 0.16  # Ear to ear
    head_height: float = 0.24  # Chin to top
    neck_circumference: float = 0.40

    # Torso measurements
    chest_circumference: float = 1.00
    waist_circumference: float = 0.85
    shoulder_width: float = 0.46  # Shoulder to shoulder
    torso_length: float = 0.50  # Shoulder to waist
    back_width: float = 0.40

    # Arm measurements
    shoulder_circumference: float = 0.40
    upper_arm_length: float = 0.30
    upper_arm_circumference: float = 0.32
    elbow_circumference: float = 0.28
    forearm_length: float = 0.26
    forearm_circumference: float = 0.27
    wrist_circumference: float = 0.17
    hand_length: float = 0.19
    hand_width: float = 0.09
    palm_circumference: float = 0.22

    # Leg measurements
    hip_circumference: float = 1.00
    thigh_length: float = 0.45
    thigh_circumference: float = 0.58
    knee_circumference: float = 0.40
    calf_length: float = 0.40
    calf_circumference: float = 0.38
    ankle_circumference: float = 0.24
    foot_length: float = 0.27
    foot_width: float = 0.10

    # Armor clearance (extra space for comfort and padding)
    clearance: float = 0.02  # 2cm clearance

    # Scale factor for printing (1.0 = full size, 0.1 = 1/10 scale)
    scale: float = 1.0

    # Armor thickness
    plate_thickness: float = 0.004  # 4mm thick plates

    def scaled(self, value: float) -> float:
        """Apply scale factor to a measurement."""
        return value * self.scale

    def with_clearance(self, value: float) -> float:
        """Add clearance to a measurement for armor fitting."""
        return (value + self.clearance) * self.scale

    @classmethod
    def from_size(cls, size: str) -> HumanMeasurements:
        """Create measurements from a standard size designation."""
        size_multipliers = {
            "XS": 0.90,
            "S": 0.95,
            "M": 1.00,
            "L": 1.05,
            "XL": 1.10,
            "XXL": 1.15,
        }
        multiplier = size_multipliers.get(size.upper(), 1.0)

        measurements = cls()
        # Scale all measurements except clearance, scale, and thickness
        for field_name in [
            "height", "head_circumference", "head_length", "head_width",
            "head_height", "neck_circumference", "chest_circumference",
            "waist_circumference", "shoulder_width", "torso_length", "back_width",
            "shoulder_circumference", "upper_arm_length", "upper_arm_circumference",
            "elbow_circumference", "forearm_length", "forearm_circumference",
            "wrist_circumference", "hand_length", "hand_width", "palm_circumference",
            "hip_circumference", "thigh_length", "thigh_circumference",
            "knee_circumference", "calf_length", "calf_circumference",
            "ankle_circumference", "foot_length", "foot_width",
        ]:
            current_value = getattr(measurements, field_name)
            setattr(measurements, field_name, current_value * multiplier)

        return measurements

    @classmethod
    def for_print_scale(cls, print_scale: float = 0.1) -> HumanMeasurements:
        """Create measurements scaled for 3D printing.

        Default 0.1 scale creates ~17.5cm tall armor pieces suitable
        for desktop 3D printers.
        """
        measurements = cls()
        measurements.scale = print_scale
        # Adjust plate thickness for printing (minimum viable thickness)
        measurements.plate_thickness = max(0.002, 0.004 * print_scale)
        return measurements

    def get_armor_dimensions(self) -> dict[str, dict[str, float]]:
        """Get calculated armor piece dimensions."""
        return {
            "helmet": {
                "inner_width": self.with_clearance(self.head_width),
                "inner_length": self.with_clearance(self.head_length),
                "inner_height": self.with_clearance(self.head_height),
                "outer_width": self.with_clearance(self.head_width) + self.scaled(self.plate_thickness * 2),
                "outer_length": self.with_clearance(self.head_length) + self.scaled(self.plate_thickness * 2),
                "outer_height": self.with_clearance(self.head_height) + self.scaled(self.plate_thickness * 2),
                "visor_width": self.scaled(self.head_width * 0.8),
                "visor_height": self.scaled(0.015),  # Eye slit height
            },
            "chest": {
                "width": self.with_clearance(self.chest_circumference / 2),
                "height": self.with_clearance(self.torso_length),
                "depth": self.with_clearance(self.chest_circumference / 3.14),
            },
            "pauldron": {
                "width": self.with_clearance(self.shoulder_circumference / 2),
                "height": self.scaled(self.upper_arm_length * 0.4),
                "depth": self.with_clearance(self.shoulder_circumference / 2.5),
            },
            "gauntlet": {
                "hand_length": self.with_clearance(self.hand_length),
                "hand_width": self.with_clearance(self.hand_width),
                "wrist_circumference": self.with_clearance(self.wrist_circumference),
            },
            "vambrace": {
                "length": self.with_clearance(self.forearm_length),
                "upper_circumference": self.with_clearance(self.elbow_circumference),
                "lower_circumference": self.with_clearance(self.wrist_circumference),
            },
            "cuisse": {
                "length": self.with_clearance(self.thigh_length),
                "upper_circumference": self.with_clearance(self.thigh_circumference),
                "lower_circumference": self.with_clearance(self.knee_circumference),
            },
            "greave": {
                "length": self.with_clearance(self.calf_length),
                "upper_circumference": self.with_clearance(self.knee_circumference),
                "lower_circumference": self.with_clearance(self.ankle_circumference),
            },
            "sabaton": {
                "length": self.with_clearance(self.foot_length),
                "width": self.with_clearance(self.foot_width),
                "ankle_circumference": self.with_clearance(self.ankle_circumference),
            },
        }
