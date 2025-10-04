"""Tests for the consonance calculator module."""

import pytest
from pydantic import ValidationError

from src.calculator import ChordInput, calculate_consonance


class TestChordInput:
    """Test cases for ChordInput validation."""

    def test_valid_chord_input(self):
        """Test that valid input is accepted."""
        chord = ChordInput(edo=12, notes=[0, 4, 7])
        assert chord.edo == 12
        assert chord.notes == [0, 4, 7]

    def test_invalid_edo_zero(self):
        """Test that EDO must be greater than zero."""
        with pytest.raises(ValidationError):
            ChordInput(edo=0, notes=[0, 1, 2])

    def test_invalid_edo_negative(self):
        """Test that EDO cannot be negative."""
        with pytest.raises(ValidationError):
            ChordInput(edo=-1, notes=[0, 1, 2])

    def test_invalid_notes_out_of_range(self):
        """Test that notes must be within EDO range."""
        with pytest.raises(ValidationError):
            ChordInput(edo=12, notes=[0, 4, 12])  # 12 is out of range [0-11]

    def test_invalid_notes_negative(self):
        """Test that notes cannot be negative."""
        with pytest.raises(ValidationError):
            ChordInput(edo=12, notes=[-1, 0, 4])


class TestCalculateConsonance:
    """Test cases for consonance calculation."""

    def test_calculate_consonance_returns_float(self):
        """Test that consonance calculation returns a float."""
        result = calculate_consonance(edo=12, notes=[0, 4, 7])
        assert isinstance(result, float)

    def test_calculate_consonance_validates_input(self):
        """Test that invalid input raises ValidationError."""
        with pytest.raises(ValidationError):
            calculate_consonance(edo=12, notes=[0, 4, 12])
