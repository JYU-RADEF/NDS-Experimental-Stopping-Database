import marimo

__generated_with = "0.23.5"
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

    import plotly.express as px

    # Import from nds_dedx_database API
    from nds_dedx_database import (
        get_bundled_df,
        get_element_density,
        harmonize_energy_units,
        harmonize_dedx_units,
        is_element_in_periodic_table,
    )

    # Use the API to get the stopping power data
    get_bundled_df()

    return (
        get_element_density,
        harmonize_dedx_units,
        harmonize_energy_units,
        is_element_in_periodic_table,
        px,
    )


@app.cell
def _(df_original, mo):
    mo.md(f"""
    Energy units: {df_original["energy_unit"].unique()}\n
    Stopping power units: {df_original["stopping_unit"].unique()}
    """)
    return


@app.cell
def _(df_original, harmonize_energy_units):
    df_harmonized_energy = harmonize_energy_units(df_original, to="MeV/u")
    df_harmonized_energy
    return (df_harmonized_energy,)


@app.cell
def _(df_harmonized_energy):
    df_harmonized_energy["target_name"].unique()
    return


@app.cell
def _(df_harmonized_energy, harmonize_dedx_units):
    df_harmonized_dedx = harmonize_dedx_units(df_harmonized_energy, to="MeV/(mg/cm2)")
    df_harmonized_dedx
    return (df_harmonized_dedx,)


@app.cell
def _(df_original):
    projectiles = list(df_original["projectile_name"].unique())
    targets = list(df_original["target_name"].unique())

    print(f"number of projectiles: {len(projectiles)}")
    print(f"number of targets: {len(targets)}")

    unique_combinations = df_original[["projectile_name", "target_name"]].drop_duplicates()
    print(f"number of unique combinations: {len(unique_combinations)}")
    unique_combinations
    return


@app.cell
def _(df_harmonized_dedx, is_element_in_periodic_table):
    df_elemental_only = df_harmonized_dedx[
        df_harmonized_dedx["target_name"].apply(is_element_in_periodic_table)
    ]

    all(df_elemental_only == df_harmonized_dedx)
    return (df_elemental_only,)


@app.cell
def _(df_elemental_only):
    df_elemental_only["target_name"].unique()
    return


@app.cell
def _(df_elemental_only, px):
    df_elemental_only.sort_values(["projectile_name"], inplace=True)
    projectiles_1 = list(df_elemental_only["projectile_name"].unique())


    def filter_by_ion(ion: str):
        df_ = df_elemental_only.copy()
        df_ = df_[df_["projectile_name"] == ion]
        fig = px.scatter(
            df_,
            x="energy",
            y="stopping_power",
            symbol="stopping_unit",
            color="target_name",
            log_x=True,
            log_y=True,
            hover_data=["energy", "energy_unit", "stopping_unit"],
            width=1200,
            height=600,
        )
        fig.update_layout(
            title=f"Stopping power vs energy for {ion} ions",
            xaxis_title="Energy (MeV/u)",
            yaxis_title="Stopping power (MeV/(mg/cm2))",
        )
        return fig


    return filter_by_ion, projectiles_1


@app.cell
def _(mo, projectiles_1):
    selected_ion = mo.ui.dropdown(
        options=projectiles_1,
        value=projectiles_1[0],
        label="Select ion:",
    )
    selected_ion
    return (selected_ion,)


@app.cell
def _(filter_by_ion, selected_ion):
    filter_by_ion(selected_ion.value)
    return


@app.cell
def _(df_elemental_only, mo, px):
    df_1 = df_elemental_only.sort_values(["target_name"])
    targets_1 = df_1["target_name"].unique()


    def filter_by_target(target: str):
        df_ = df_1.copy()
        df_ = df_[df_["target_name"] == target]
        fig = px.scatter(
            df_,
            x="energy",
            y="stopping_power",
            color="projectile_name",
            symbol="ref_id",
            log_x=True,
            log_y=True,
            hover_data=["energy", "energy_unit", "stopping_unit"],
            width=1200,
            height=600,
        )
        fig.update_layout(
            title=f"Stopping power vs energy for {target} targets",
            xaxis_title="Energy (MeV/u)",
            yaxis_title="Stopping power (MeV/(mg/cm2))",
        )
        return fig


    selected_target = mo.ui.dropdown(
        options=targets_1.tolist(),
        value=targets_1[0],
        label="Select target:",
    )
    selected_target
    return df_1, filter_by_target, selected_target


@app.cell
def _(filter_by_target, selected_target):
    filter_by_target(selected_target.value)

    return


@app.cell
def _(df_1, px, selected_ion, selected_target):
    def filter_by_target_and_ion(ion: str, target: str):
        df_ = df_1.copy()
        df_ = df_[(df_["target_name"] == target) & (df_["projectile_name"] == ion)]
        fig = px.scatter(
            data_frame=df_,
            x="energy",
            y="stopping_power",
            color="ref_id",
            symbol="stopping_unit",
            log_x=True,
            log_y=False,
            hover_data=["energy", "energy_unit", "stopping_unit"],
            width=1200,
            height=600,
        )
        fig.update_layout(
            title=f"Stopping power vs energy for {ion} ions and {target} targets",
            xaxis_title="Energy (MeV/u)",
            yaxis_title="Stopping power (MeV/(mg/cm2))",
        )
        return fig


    filter_by_target_and_ion(selected_ion.value, selected_target.value)

    return


@app.cell
def _(df_elemental_only):
    df_elemental_only
    return


@app.cell
def _(df_elemental_only, get_element_density, px):
    # check density values as sanity check
    df_elemental_only["pt_rho"] = df_elemental_only["target_name"].apply(
        get_element_density
    )
    tabulated_density = df_elemental_only["target_rho"]
    df_elemental_only["density_ratio"] = df_elemental_only["pt_rho"] / tabulated_density

    px.scatter(
        df_elemental_only,
        x="target_rho",
        y="density_ratio",
        hover_data=["target_name", "pt_rho", "target_rho"],
        labels={"x": "tabulated density", "y": "density ratio"},
    )
    return


if __name__ == "__main__":
    app.run()
