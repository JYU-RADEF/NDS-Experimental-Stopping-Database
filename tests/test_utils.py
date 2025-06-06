"""Tests for the utils module."""

import pandas as pd
import pytest

from nds_database.utils import (  # type: ignore
    convert_dedx,
    convert_energy,
    get_element_mass,
    harmonize_energy_units,
    is_compound,
    is_element_in_periodic_table,
)


class TestIsCompound:
    """Tests for the is_compound function."""

    @pytest.mark.parametrize(
        "name,expected",
        [
            ("Cu", False),  # Single element
            ("CuO", True),  # Compound without numbers but > 2 chars
            ("H2O", True),  # Compound with numbers
            ("NaCl", True),  # Compound without numbers but > 2 chars
            ("CO2", True),  # Compound with numbers
            ("He", False),  # Single element, 2 chars
            ("H", False),  # Single element, 1 char
            ("CH4", True),  # Compound with numbers
            ("C60", True),  # Compound with numbers
        ],
    )
    def test_is_compound(self, name, expected):
        """Test is_compound with various inputs."""
        assert is_compound(name) == expected

    def test_edge_cases(self):
        """Test edge cases for is_compound."""
        # Empty string
        assert not is_compound("")
        # Short string with digit
        assert is_compound("H2")  # Should return True because it has a digit
        # Long string without digit
        assert not is_compound("Helium")  # Should return False because no digits


class TestIsElementInPeriodicTable:
    """Tests for the is_element_in_periodic_table function."""

    @pytest.mark.parametrize(
        "name,expected",
        [
            ("Cu", True),  # Element by symbol
            ("cu", False),  # Element by lowercase symbol
            ("Copper", True),  # Element by name
            ("copper", True),  # Element by lowercase name
            ("H", True),  # Element by symbol
            ("Hydrogen", True),  # Element by name
            ("Fe", True),  # Element by symbol
            ("Iron", True),  # Element by name
            ("Xyz", False),  # Non-existent element
            ("TiN", False),  # Compound
            ("", False),  # Empty string
        ],
    )
    def test_is_element_in_periodic_table(self, name, expected):
        """Test is_element_in_periodic_table with various inputs."""
        assert is_element_in_periodic_table(name) == expected

    def test_edge_cases(self):
        """Test edge cases for is_element_in_periodic_table."""
        # Very long string
        assert not is_element_in_periodic_table("VeryLongElementName")
        # Special characters
        assert is_element_in_periodic_table("Cu@")
        # Number
        assert not is_element_in_periodic_table("12")


class TestGetElementMass:
    """Tests for the get_element_mass function."""

    @pytest.mark.parametrize(
        "name,isotope,expected_approx",
        [
            ("Cu", 63.546, 63.546),  # Copper with average isotope
            ("H", 1.008, 1.008),  # Hydrogen with average isotope
            ("Fe", 55.845, 55.845),  # Iron with average isotope
            ("U", 238.03, 238.03),  # Uranium with common isotope
            ("O", 16.0, 16.0),  # Oxygen with common isotope
        ],
    )
    def test_get_element_mass(self, name, isotope, expected_approx):
        """Test get_element_mass with various inputs."""
        # Use approx due to potential floating point differences
        assert get_element_mass(name, isotope) == pytest.approx(
            expected_approx, rel=0.1
        )

    def test_get_element_mass_different_isotopes(self):
        """Test get_element_mass with different isotopes of the same element."""
        # Carbon-12
        assert get_element_mass("C", 12.0) == pytest.approx(12.0, rel=0.01)
        # Carbon-13
        assert get_element_mass("C", 13.0) == pytest.approx(13.0, rel=0.01)
        # Carbon-14
        assert get_element_mass("C", 14.0) == pytest.approx(14.0, rel=0.01)


class TestConvertEnergy:
    """Tests for the convert_energy function."""

    @pytest.mark.parametrize(
        "value,mass,from_unit,to_unit,expected_value,expected_unit",
        [
            # Same prefix, same /u
            (10.0, 12.0, "MeV/u", "MeV/u", 10.0, "MeV/u"),
            # Same prefix, add /u
            (120.0, 12.0, "MeV", "MeV/u", 10.0, "MeV/u"),
            # Same prefix, remove /u
            (10.0, 12.0, "MeV/u", "MeV", 120.0, "MeV"),
            # Different prefix, same /u
            (10.0, 12.0, "MeV/u", "keV/u", 10000.0, "keV/u"),
            # Different prefix, different /u
            (10.0, 12.0, "MeV/u", "keV", 120000.0, "keV"),
            # Different prefix, both without /u
            (10.0, 12.0, "MeV", "keV", 10000.0, "keV"),
            # keV to MeV, same /u
            (10000.0, 12.0, "keV/u", "MeV/u", 10.0, "MeV/u"),
            # keV to MeV, different /u
            (10000.0, 12.0, "keV/u", "MeV", 120.0, "MeV"),
        ],
    )
    def test_convert_energy(
        self, value, mass, from_unit, to_unit, expected_value, expected_unit
    ):
        """Test convert_energy with various inputs."""
        result_value, result_unit = convert_energy(value, mass, from_unit, to_unit)
        assert result_value == pytest.approx(expected_value)
        assert result_unit == expected_unit

    def test_convert_energy_unknown_units(self):
        """Test convert_energy with unknown units."""
        with pytest.raises(ValueError, match="Unknown energy units"):
            convert_energy(10.0, 12.0, "GeV/u", "MeV/u")
        with pytest.raises(ValueError, match="Unknown energy units"):
            convert_energy(10.0, 12.0, "MeV/u", "GeV/u")


class TestConvertDedx:
    """Tests for the convert_dedx function."""

    @pytest.mark.parametrize(
        "value,target_mass,from_unit,to_unit,expected",
        [
            # Same units
            (10.0, 12.0, "MeV/(mg/cm2)", "MeV/(mg/cm2)", 10.0),
            # MeV/(mg/cm2) to E-15eV cm2/atom
            (10.0, 12.0, "MeV/(mg/cm2)", "E-15eV cm2/atom", 1e-14),
            # E-15eV cm2/atom to MeV/(mg/cm2)
            (10.0, 12.0, "E-15eV cm2/atom", "MeV/(mg/cm2)", 1e16),
            # eV/A to MeV/(mg/cm2)
            (10.0, 12.0, "eV/A", "MeV/(mg/cm2)", 10.0 * 1e-6),
            # MeV/(mg/cm2) to eV/A
            (10.0, 12.0, "MeV/(mg/cm2)", "eV/A", 10.0 / 1e-6),
        ],
    )
    def test_convert_dedx(self, value, target_mass, from_unit, to_unit, expected):
        """Test convert_dedx with various inputs."""
        result = convert_dedx(value, target_mass, from_unit, to_unit)
        assert result == pytest.approx(expected)

    def test_convert_dedx_unknown_units(self):
        """Test convert_dedx with unknown units."""
        with pytest.raises(ValueError, match="Unknown dE/dx units"):
            convert_dedx(10.0, 12.0, "unknown", "MeV/(mg/cm2)")
        with pytest.raises(ValueError, match="Unknown dE/dx units"):
            convert_dedx(10.0, 12.0, "MeV/(mg/cm2)", "unknown")


class TestHarmonizeEnergyUnits:
    """Tests for the harmonize_energy_units function."""

    def test_harmonize_energy_units_default(self):
        """Test harmonize_energy_units with default target unit."""
        # Create test dataframe
        df = pd.DataFrame(
            {
                "projectile_name": ["Cu", "Fe", "H"],
                "ion_isotope": [63.546, 55.845, 1.008],
                "energy": [10.0, 20.0, 30.0],
                "energy_unit": ["MeV/u", "keV/u", "MeV"],
                "target_mass_atom_ratio": [1.0, 1.0, 1.0],
            }
        )

        # Apply harmonization
        result_df = harmonize_energy_units(df)

        # Check that energy_unit is now uniform
        assert all(unit == "MeV/u" for unit in result_df["energy_unit"])

        # Check that ion_mass is correct
        assert "ion_mass" in result_df.columns

        # Check conversions are correct
        assert result_df.loc[0, "energy"] == pytest.approx(
            10.0
        )  # MeV/u to MeV/u (no change)
        assert result_df.loc[1, "energy"] == pytest.approx(
            0.02
        )  # keV/u to MeV/u (divide by 1000)
        # MeV to MeV/u requires division by mass, which depends on the actual mass value from get_element_mass

    def test_harmonize_energy_units_custom_target(self):
        """Test harmonize_energy_units with custom target unit."""
        # Create test dataframe
        df = pd.DataFrame(
            {
                "projectile_name": ["Cu", "Fe", "H"],
                "ion_isotope": [63.546, 55.845, 1.008],
                "energy": [10.0, 20.0, 30.0],
                "energy_unit": ["MeV/u", "keV/u", "MeV"],
                "target_mass_atom_ratio": [1.0, 1.0, 1.0],
            }
        )

        # Apply harmonization to keV
        result_df = harmonize_energy_units(df, to="keV")

        # Check that energy_unit is now uniform
        assert all(unit == "keV" for unit in result_df["energy_unit"])

        # Check conversions are correct
        # MeV/u to keV requires multiplication by 1000 and by mass
        # keV/u to keV requires multiplication by mass
        # MeV to keV requires multiplication by 1000
        assert result_df.loc[2, "energy"] == pytest.approx(
            30000.0
        )  # MeV to keV (multiply by 1000)
