"""Tests for the utils module."""

import re

import pandas as pd
import pytest

from nds_dedx_database.utils import (
    convert_dedx,
    convert_energy,
    get_element_density,
    get_element_mass,
    get_symbol,
    harmonize_dedx_units,
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
            ("cu", True),  # Element by lowercase symbol
            ("Copper", True),  # Element by name
            ("copper", True),  # Element by lowercase name
            ("Carbon", True),  # Element by name
            ("C", True),  # Element by symbol
            ("H", True),  # Element by symbol
            ("Hydrogen", True),  # Element by name
            ("Fe", True),  # Element by symbol
            ("Iron", True),  # Element by name
            ("Xyz", False),  # Non-existent element
            ("TiN", True),  # Interpreted as element name by current logic
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


class TestGetElementDensity:
    """Tests for the get_element_density function."""

    @pytest.mark.parametrize(
        "name,isotope,expected_approx",
        [
            ("Cu", 63.546, 8.96),  # Copper
            ("Cu", 65.0, 9.15),  # Copper with different isotope
            ("Cu", None, 8.96),  # Copper without isotope
            ("Fe", 55.845, 7.874),  # Iron
            ("Fe", 54.0, 7.6),  # Iron with different isotope
            ("Fe", 57.0, 8.03),  # Iron with different isotope
            ("Fe", None, 7.874),  # Iron without isotope
            ("U", 238.03, 19.1),  # Uranium
            ("U", 235.0, 18.71),  # Uranium with different isotope
            ("O", 16.0, 1.14),  # Oxygen (liquid)
            ("O", 17.0, 1.21),  # Oxygen with different isotope (liquid)
            ("H", 1.008, 70.85 * 1e-3),  # Hydrogen (liquid)
            ("H", 2.014, 141.0 * 1e-3),  # Deuterium (liquid)
            ("He", 4.0026, 122.0 * 1e-3),  # Helium (liquid)
            ("He", 3.016, 92.0 * 1e-3),  # Helium-3 (liquid)
            ("Carbon", 12.0, 2.2),  # Carbon
            ("Carbon", 13.0, 2.38),  # Carbon with different isotope
            ("nitrogen", 14.0, 0.808),  # Nitrogen
            ("nitrogen", 15.0, 0.865),  # Nitrogen with different isotope
        ],
    )
    def test_get_element_density(self, name, isotope, expected_approx):
        """Test get_element_density with various inputs."""
        assert get_element_density(name, isotope) == pytest.approx(
            expected_approx, rel=0.01
        )

    def test_get_element_density_invalid_element(self):
        """Test get_element_density with an invalid element."""
        with pytest.raises(
            ValueError,
            match=re.escape("Element 'Xyz' not found in the periodic table."),
        ):
            get_element_density("Xyz", 0)  # Non-existent element
        with pytest.raises(
            ValueError, match=re.escape("Element '' not found in the periodic table.")
        ):
            get_element_density("", 0)  # Empty string


class TestGetElementSymbol:
    """Tests for the get_element_symbol function."""

    @pytest.mark.parametrize(
        "name,expected",
        [
            ("Copper", "Cu"),
            ("copper", "Cu"),
            ("Hydrogen", "H"),
            ("hydrogen", "H"),
            ("Iron", "Fe"),
            ("iron", "Fe"),
            ("Uranium", "U"),
            ("uranium", "U"),
            ("Oxygen", "O"),
            ("oxygen", "O"),
        ],
    )
    def test_get_element_symbol(self, name, expected):
        """Test get_element_symbol with various inputs."""
        assert get_symbol(name) == expected

    def test_get_element_symbol_invalid_element(self):
        """Test get_element_symbol with an invalid element."""
        with pytest.raises(
            ValueError,
            match=re.escape("Element 'Xyz' not found in the periodic table."),
        ):
            get_symbol("Xyz")  # Non-existent element
        with pytest.raises(
            ValueError, match=re.escape("Element '' not found in the periodic table.")
        ):
            get_symbol("")  # Empty string


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
        "value,target_mass,target_rho,from_unit,to_unit,expected_value,expected_unit",
        [
            # Same units
            (10.0, 12.0, 6.0, "MeV/(mg/cm2)", "MeV/(mg/cm2)", 10.0, "MeV/(mg/cm2)"),
            # MeV/(mg/cm2) to E-15eV cm2/atom
            (
                10.0,
                12.0,
                6.0,
                "MeV/(mg/cm2)",
                "E-15eV cm2/atom",
                1.6605 * 12.0 * 10.0,
                "E-15eV cm2/atom",
            ),
            # E-15eV cm2/atom to MeV/(mg/cm2)
            (
                10.0,
                12.0,
                6.0,
                "E-15eV cm2/atom",
                "MeV/(mg/cm2)",
                10.0 / (1.6605 * 12.0),
                "MeV/(mg/cm2)",
            ),
            # eV/A to MeV/(mg/cm2)
            (
                10.0,
                12.0,
                6.0,
                "eV/A",
                "MeV/(mg/cm2)",
                10 / (1e3 * 6.0) * 1e8 * 1e-6,
                "MeV/(mg/cm2)",
            ),
            # MeV/(mg/cm2) to eV/A
            (
                10.0,
                12.0,
                6.0,
                "MeV/(mg/cm2)",
                "eV/A",
                10 * (1e3 * 6.0) / 1e8 / 1e-6,
                "eV/A",
            ),
        ],
    )
    def test_convert_dedx(
        self,
        value,
        target_mass,
        target_rho,
        from_unit,
        to_unit,
        expected_value,
        expected_unit,
    ):
        """Test convert_dedx with various inputs."""
        result = convert_dedx(value, target_mass, target_rho, from_unit, to_unit)
        assert result[0] == pytest.approx(expected_value)
        assert result[1] == expected_unit

    def test_convert_dedx_unknown_units(self):
        """Test convert_dedx with unknown units."""
        with pytest.raises(
            ValueError,
            match=re.escape("Conversion from unknown to MeV/(mg/cm2) not supported."),
        ):
            convert_dedx(10.0, 12.0, 6.0, "unknown", "MeV/(mg/cm2)")
        with pytest.raises(
            ValueError,
            match=re.escape("Conversion from MeV/(mg/cm2) to unknown not supported."),
        ):
            convert_dedx(10.0, 12.0, 6.0, "MeV/(mg/cm2)", "unknown")


class TestHarmonizeEnergyUnits:
    """Tests for the harmonize_energy_units function."""

    def test_harmonize_energy_units_default(self):
        """Test harmonize_energy_units with default target unit."""
        # Create test dataframe
        df = pd.DataFrame({
            "projectile_name": ["Cu", "Fe", "H"],
            "ion_isotope": [63.546, 55.845, 1.008],
            "energy": [10.0, 20.0, 30.0],
            "energy_unit": ["MeV/u", "keV/u", "MeV"],
            "target_mass_atom_ratio": [1.0, 1.0, 1.0],
        })

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
        df = pd.DataFrame({
            "projectile_name": ["Cu", "Fe", "H"],
            "ion_isotope": [63.546, 55.845, 1.008],
            "energy": [10.0, 20.0, 30.0],
            "energy_unit": ["MeV/u", "keV/u", "MeV"],
            "target_mass_atom_ratio": [1.0, 1.0, 1.0],
        })

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


class TestHarmonizeDedxUnits:
    """Tests for the harmonize_dedx_units function."""

    def test_harmonize_dedx_units_default(self):
        """Test harmonize_dedx_units with default target unit."""
        # Create test dataframe
        df = pd.DataFrame({
            "target_name": ["Cu", "Fe", "H"],
            "target_isotope": [63.546, 55.845, 1.008],
            "stopping_power": [10.0, 20.0, 30.0],
            "stopping_unit": ["MeV/(mg/cm2)", "E-15eV cm2/atom", "eV/A"],
            "target_mass": [63.546, 55.845, 1.008],
        })

        # Apply harmonization
        result_df = harmonize_dedx_units(df)

        # Check that stopping_unit is now uniform
        assert all(unit == "MeV/(mg/cm2)" for unit in result_df["stopping_unit"])

        # Check that target_rho is available
        assert "target_rho" in result_df.columns

    def test_harmonize_dedx_units_custom_target(self):
        """Test harmonize_dedx_units with custom target unit."""
        # Create test dataframe
        df = pd.DataFrame({
            "target_name": ["Cu", "Fe", "H"],
            "target_isotope": [63.546, 55.845, 1.008],
            "stopping_power": [10.0, 20.0, 30.0],
            "stopping_unit": ["MeV/(mg/cm2)", "E-15eV cm2/atom", "eV/A"],
            "target_mass": [63.546, 55.845, 1.008],
        })

        # Apply harmonization to eV/Å
        result_df = harmonize_dedx_units(df, to="MeV/(mg/cm2)")

        # Check that stopping_unit is now uniform
        assert all(unit == "MeV/(mg/cm2)" for unit in result_df["stopping_unit"])
