from __future__ import annotations
from abc import abstractmethod
from fractions import Fraction
from typing import override


# A base class for target FPS modes in VapourSynth scripts.
# This class defines the interface for different target FPS modes.
# It provides static methods to create instances of specific modes.
class TargetFpsMode:
    @abstractmethod
    def get_fps_fraction(self, source_fps: Fraction) -> Fraction:
        pass

    @staticmethod
    def fixed_fps(target_fps: float) -> TargetFpsMode:
        return FixedFpsMode(target_fps)

    @staticmethod
    def fixed_multiplier(multiplier: float) -> TargetFpsMode:
        return FixedMultiplierMode(multiplier)


# A class representing a target FPS mode that uses a fixed multiplier.
class FixedMultiplierMode(TargetFpsMode):
    def __init__(self, multiplier: float):
        self.target_mult_frac = Fraction(multiplier)

    @override
    def get_fps_fraction(self, source_fps: Fraction) -> Fraction:
        target = self.target_mult_frac
        # Limit denominator early to avoid very complex fractions
        return target


# A class representing a target FPS mode that uses a fixed target FPS value.
class FixedFpsMode(TargetFpsMode):
    def __init__(self, target_fps: float):
        self.target_fps_frac = Fraction(target_fps)

    @override
    def get_fps_fraction(self, source_fps: Fraction) -> Fraction:
        target = self.target_fps_frac / source_fps
        # Limit denominator early to avoid very complex fractions
        return target
