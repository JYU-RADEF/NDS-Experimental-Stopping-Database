import marimo

__generated_with = "0.23.6"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Notebook for browsing the Stopping Power dataset

    The Stopping Power dataset contains information about the stopping power of various materials for different types of particles. The dataset can be found at the following link: https://www-nds.iaea.org/stopping/
    """)
    return


@app.cell
def _():
    # magic command not supported in marimo; please file an issue to add support
    # %reload_ext autoreload
    # '%autoreload 2' command supported automatically in marimo

    from typing import Optional

    import pandas as pd  # type: ignore
    import plotly.express as px  # type: ignore

    # Import from nds_dedx_database API
    from nds_dedx_database import (
        get_bundled_df,
        harmonize_energy_units,
        get_data_for_ion_target,
    )

    # Use the API to get the stopping power data
    df_original = get_bundled_df()
    df_energy_harmonized = harmonize_energy_units(df_original)
    return Optional, df_energy_harmonized, df_original, px


@app.cell
def _(df_original, mo):
    unique_combinations = df_original[["projectile_name", "target_name"]].drop_duplicates()
    mo.md(f"""
    ## Dataset Summary
    Full dataset information:\n
    Number of entries: {len(df_original)}\n
    Number of unique ions: {df_original["ion_isotope"].nunique()}\n
    Number of unique targets: {df_original["target_mass_atom_ratio"].nunique()}\n
    Number of unique projectile-target combinations: {len(unique_combinations)}
    """)
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
    return projectile_dropdown, target_dropdown


@app.cell
def _(mo):
    mo.md("""
    ### Select Projectile and Target
    """)
    return


@app.cell
def _(mo, projectile_dropdown, target_dropdown):
    mo.hstack(
        [projectile_dropdown, target_dropdown],
    )
    return


@app.cell
def _(Optional, df_energy_harmonized, projectile_dropdown, target_dropdown):
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
    return (filtered_df,)


@app.cell
def _(filtered_df, mo):
    mo.md(f"""
    ### About Selected Projectile-Target Combination

    Dataset summary for the selected projectile-target combination will be displayed here.
    - number of entries: {len(filtered_df)}
    - energy range: {filtered_df["energy"].min():.3e} - {filtered_df["energy"].max():.3e} MeV/u
    - stopping power range: {filtered_df["stopping_power"].min():.3e} - {filtered_df["stopping_power"].max():.3e} MeV/(mg/cm^2)
    """)
    return


@app.cell
def _(filtered_df, px):
    def plot_data(df):

        ion = df["selected_ion"].iloc[0]
        target = df["selected_target"].iloc[0]

        fig = px.scatter(
            data_frame=df,
            x="energy",
            y="stopping_power_converted",
            color="ref_id",
            log_x=True,
            log_y=False,
            hover_data=["energy", "energy_unit", "stopping_unit_converted"],
            width=1200,
            height=600,
        )
        fig.update_layout(
            title=f"Stopping power vs energy for {ion} ions and {target} targets",
            xaxis_title="Energy (MeV/u)",
            yaxis_title="Stopping power (MeV/(mg/cm2))",
        )
        return fig


    plot_data(filtered_df)
    return


@app.cell
def _(df_energy_harmonized):
    df_energy_harmonized
    return


@app.cell
def _(df_original):
    df_original.query("projectile_name == 'O' and target_name == 'C'")
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
