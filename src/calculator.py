"""Consonance Calculator Module

This module implements Sethares' acoustic roughness model to calculate
consonance scores for chords in various equal divisions of the octave (EDO).
"""

from typing import Any

from pydantic import BaseModel, Field, field_validator


class ChordInput(BaseModel):
    """Input validation model for chord consonance calculation."""

    edo: int = Field(gt=0, description="Equal divisions of the octave (N-EDO)")
    notes: list[int] = Field(
        min_length=1, description="List of note indices in the EDO system"
    )

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, v: list[int], info: Any) -> list[int]:
        """Validate that all notes are within the EDO range."""
        edo = info.data.get("edo")
        if edo and any(note < 0 or note >= edo for note in v):
            msg = f"All notes must be in range [0, {edo - 1}]"
            raise ValueError(msg)
        return v


def calculate_consonance(edo: int, notes: list[int]) -> float:
    """Calculate consonance score for a chord.

    Args:
        edo: Equal divisions of the octave (N-EDO)
        notes: List of note indices in the EDO system

    Returns:
        Consonance score (lower roughness = higher consonance)

    Raises:
        ValueError: If input validation fails
    """
    # Validate input using Pydantic
    ChordInput(edo=edo, notes=notes)

    # Placeholder implementation
    # TODO: Implement Sethares' roughness model
    return 0.0
