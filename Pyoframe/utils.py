import pyoframe as pf

def plot_results(dispatch_results, save_to="energy_mix.png"):
    """Plot the energy mix of the dispatch results.

    Parameters
    ----------
    dispatch : polars.DataFrame
        The dispatch results DataFrame.
        Should contain columns "gen_id", "datetime", and "solution".
    save_to : str, optional
        The path to save the plot to.
    """
    import altair as alt
    import polars as pl

    COLORS = {
        "Solar": "#F4B942",  # warm solar yellow
        "Wind": "#4C9BE8",  # sky blue
        "Hydropower": "#1769AA",  # deep water blue
        "Nuclear": "#8E5AA6",  # muted purple
        "Coal": "#4A4A4A",  # charcoal
        "Geothermal": "#C65D3A",  # earthy red
        "Biopower": "#5A9E4B",  # forest green
        "Natural Gas": "#9B6B43",  # warm brown
    }

    if dispatch_results is None:

        # Make sure everything is installed properly
        m = pf.Model("highs")
        m.attr.Silent = True
        m.X = pf.Variable(lb=1, ub=2)
        m.minimize = m.X
        m.optimize()
        assert round(m.X.solution, 8) == 1, "Something went wrong!"

        print("No results to plot.")
        return

    _has_datetime = "datetime" in dispatch_results.columns

    if not _has_datetime:
        dispatch_results = dispatch_results.with_columns(
            datetime=pl.datetime(2019, 1, 1, 12)
        )

    gens = pl.read_parquet(INPUT_DIR / "generators.parquet")

    dispatch_results = dispatch_results.join(
        gens.select(["gen_id", "type"]), on="gen_id"
    )
    dispatch_results = dispatch_results.group_by("type", "datetime").agg(
        pl.col("solution").sum()
    )
    dispatch_results = dispatch_results.join(
        dispatch_results.group_by("type").agg(std=pl.col("solution").std()), on="type"
    ).sort("std", "solution", descending=[False, True])

    MISSING_COLORS = set(dispatch_results["type"].to_list()) - set(COLORS.keys())
    EXTRA_COLORS = set(COLORS.keys()) - set(dispatch_results["type"].to_list())
    assert MISSING_COLORS == set(), (
        f"Missing colors for generator types: {MISSING_COLORS}"
    )
    assert EXTRA_COLORS == set(), f"Extra colors for generator types: {EXTRA_COLORS}"

    dispatch_results = dispatch_results.with_columns(
        solution_GW=pl.col("solution") / 1000
    )

    plot = dispatch_results.plot.bar(
        x=alt.X("datetime:T", title="Time"),
        y=alt.Y("solution_GW:Q", title="Dispatched Power (GW)"),
        color=alt.Color(
            "type:N",
            sort=alt.SortField("std", order="descending"),
            title="Generator Type",
            scale=alt.Scale(domain=list(COLORS.keys()), range=list(COLORS.values())),
        ),
        order=alt.Order("std:Q"),
        size=alt.value(30),
    ).properties(title="Modelled Energy Mix")

    plot.save(save_to)

    return plot
