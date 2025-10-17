"""UI layer data models."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Observation:
    """Immutable observation record for EDO analysis.

    Represents a single observation of roughness calculation for a specific
    EDO system and note combination.

    Attributes:
        edo: N-EDO (N Equal Divisions of the Octave) value
        notes: Tuple of selected note indices
        roughness: Calculated acoustic roughness value
    """

    edo: int
    notes: tuple[int, ...]
    roughness: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for backward compatibility with session state.

        Returns:
            dict: Dictionary representation with edo, notes, roughness keys
        """
        return {"edo": self.edo, "notes": self.notes, "roughness": self.roughness}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Observation":
        """Create Observation from dictionary.

        Args:
            data: Dictionary with edo, notes, roughness keys

        Returns:
            Observation: New Observation instance
        """
        return cls(edo=data["edo"], notes=tuple(data["notes"]), roughness=data["roughness"])
