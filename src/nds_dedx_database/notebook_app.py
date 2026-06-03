# /// script
# [tool.marimo.display]
# theme = "dark"
# ///

import marimo

__generated_with = "0.23.6"
app = marimo.App(width="Medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Experimental Stopping Power Data

    This notebook contains experimental Stopping Power data for various energetic particles in various materials. The original data can be found at the following link: https://www-nds.iaea.org/stopping/.

    This notebook is intended to be a reference for researchers and students who are interested in understanding the stopping power of different materials for various particles. The user can select a particle and a material from the dropdown menus, and the corresponding stopping power data will be displayed in a graph and a table below.
    """)
    return


@app.cell
def _():
    from typing import Optional

    import pandas as pd  # type: ignore
    import plotly.express as px  # type: ignore

    # Import from nds_dedx_database API
    from nds_dedx_database import (
        get_bundled_df,
        harmonize_energy_units,
    )

    # Use the API to get the stopping power data
    df_original = get_bundled_df()
    df_energy_harmonized = harmonize_energy_units(df_original)
    return Optional, df_energy_harmonized, df_original, pd, px


@app.cell
def _(df_original, pd):
    unique_combinations = df_original[["projectile_name", "target_name"]].drop_duplicates()

    summary_full = pd.DataFrame({
        "Entries": [len(df_original)],
        "Unique Ions": [df_original["ion_isotope"].nunique()],
        "Unique Targets": [df_original["target_mass_atom_ratio"].nunique()],
        "Unique Projectile-Target Combinations": [len(unique_combinations)],
    })
    return (summary_full,)


@app.cell
def _(mo):
    mo.md("""
    ## Full Database Summary
    """)
    return


@app.cell
def _(mo, summary_full):
    mo.ui.table(summary_full, selection=None)
    return


@app.cell
def _(df_energy_harmonized, mo):
    projectile_options = df_energy_harmonized["projectile_name"].unique().tolist()
    projectile_options.insert(0, "All")  # Add "All" option at the beginning of the list
    target_options = df_energy_harmonized["target_name"].unique().tolist()
    target_options.insert(0, "All")  # Add "All" option at the beginning of the list

    # Create dropdowns for selecting projectile and target
    projectile_dropdown = mo.ui.dropdown(
        options=projectile_options,
        label="Projectile:",
        value=projectile_options[0],
        searchable=True,
    )

    target_dropdown = mo.ui.dropdown(
        options=target_options,
        label="Target:",
        value=target_options[0],
        searchable=True,
    )
    logx_checkbox = mo.ui.checkbox(label="Logarithmic Energy Scale", value=True)
    logy_checkbox = mo.ui.checkbox(label="Logarithmic Stopping Power Scale", value=False)
    return logx_checkbox, logy_checkbox, projectile_dropdown, target_dropdown


@app.cell
def _(mo):
    mo.md("""
    ## Select Projectile and Target
    """)
    return


@app.cell
def _(logx_checkbox, logy_checkbox, mo, projectile_dropdown, target_dropdown):
    mo.hstack(
        [projectile_dropdown, target_dropdown, logx_checkbox, logy_checkbox],
    )
    return


@app.cell
def _(
    Optional,
    df_energy_harmonized,
    pd,
    projectile_dropdown,
    target_dropdown,
):
    def filter_data(ion: Optional[str], target: Optional[str]):
        df_ = df_energy_harmonized.copy()
        if "All" != ion:
            df_ = df_[df_["projectile_name"] == ion]
        if "All" != target:
            df_ = df_[df_["target_name"] == target]

        df_["selected_ion"] = ion
        df_["selected_target"] = target
        return df_


    filtered_df = filter_data(projectile_dropdown.value, target_dropdown.value)

    summary_selected = pd.DataFrame({
        "Entries": [len(filtered_df)],
        "E-min (MeV/u)": [filtered_df["energy"].min()],
        "E-max (MeV/u)": [filtered_df["energy"].max()],
        "dE/dx-min (MeV/(mg/cm^2))": [filtered_df["stopping_power_converted"].min()],
        "dE/dx-max (MeV/(mg/cm^2))": [filtered_df["stopping_power_converted"].max()],
    })
    return filtered_df, summary_selected


@app.cell
def _(mo, summary_selected):
    format_mapping = {
        "E-min (MeV/u)": "{:.3e}".format,
        "E-max (MeV/u)": "{:.3e}".format,
        "dE/dx-min (MeV/(mg/cm^2))": "{:.2e}".format,
        "dE/dx-max (MeV/(mg/cm^2))": "{:.2e}".format,
    }

    mo.ui.table(summary_selected, format_mapping=format_mapping, selection=None)
    return


@app.cell
def _(logx_checkbox, logy_checkbox, px):
    def plot_data(df):

        ion = df["selected_ion"].iloc[0]
        target = df["selected_target"].iloc[0]

        fig = px.scatter(
            data_frame=df,
            x="energy",
            y="stopping_power_converted",
            color="ref_id",
            log_x=logx_checkbox.value,
            log_y=logy_checkbox.value,
            hover_data=[
                "energy",
                "energy_unit",
                "stopping_unit_converted",
                "projectile_name",
                "target_name",
            ],
            width=1200,
            height=600,
        )
        fig.update_layout(
            title=f"Stopping power vs energy for {ion} ions and {target} targets",
            xaxis_title="Energy (MeV/u)",
            yaxis_title="Stopping power (MeV/(mg/cm2))",
            autosize=True,
            width=None,
        )

        fig.update_xaxes(exponentformat="power")
        fig.update_yaxes(exponentformat="power")
        return fig

    return (plot_data,)


@app.cell
def _(filtered_df, mo, plot_data):
    mo.plain(plot_data(filtered_df))
    return


@app.cell
def _(filtered_df, mo):
    mo.md("""### Data Table
    The table below shows the data entries for the selected projectile-target combination.
    """)

    mo.ui.dataframe(filtered_df.drop(columns=["selected_ion", "selected_target"]))
    return


if __name__ == "__main__":
    app.run()
