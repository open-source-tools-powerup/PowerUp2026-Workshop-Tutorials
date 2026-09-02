import os
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
import polars as pl
from plotly.subplots import make_subplots
from scipy.signal import find_peaks


def compare_timeseries( df1: pl.DataFrame, 
                        df2: pl.DataFrame,
                        on: list[str] = None,  
                        df1_name: str = 'df1', 
                        df2_name: str = 'df2',
                        left_to_right: dict = None,
                        figure_filepath: str = os.path.join(os.getcwd(), "comparison_plot.html"),
                        df1_color: str = 'blue', 
                        df2_color: str = 'red'):
    """
    Compare two timeseries dataframes and plot the results.
    
    Parameters:
    - df1: First dataframe containing timeseries data.
    - df2: Second dataframe containing timeseries data.
    - on: List of column names to compare.
    - left_to_right: Dictionary where keys are column names in df1 and values are corresponding column names in df2 to compare, e.g. {"p_sh": "p_sh", "q_sh": "q_sh"}.
    - df1_name: Name of the first dataframe (for labeling purposes), e.g., "EMT".
    - df2_name: Name of the second dataframe (for labeling purposes), e.g., "SSM".
    - figure_filepath: File path to save the resulting plot (e.g., "comparison_plot.html").
    - df1_color: Color for the first dataframe's traces (default is 'blue').
    - df2_color: Color for the second dataframe's traces (default is 'red').

    Returns:
    - None. The function saves the plot to the specified file path, defaulting to "comparison_plot.html" in the current working directory. Open it in a web browser to view the comparison.
    """
    if on is not None:
        compare = {col: col for col in on}
    elif left_to_right is not None:
        compare = left_to_right
    else:
        raise ValueError("Either 'on' or 'left_to_right' must be provided.")

    # Number of subplots to create
    nplots = len(compare)

    # Create subplots
    ncols = 2
    nrows = nplots // ncols + int(nplots % ncols > 0)
    fig = make_subplots(rows=nrows, cols=ncols, shared_xaxes=True)

    # Add traces for each comparison
    for i, (df1_col, df2_col) in enumerate(compare.items()):
        row = i // ncols + 1
        col = i % ncols + 1
        subplot_num = i + 1  # For labeling purposes, starting from 1
        legend_name = "legend" if subplot_num == 1 else f"legend{subplot_num}"
        
        fig.add_trace(go.Scatter(x=df1['time'], y=df1[df1_col], 
                                 name=f"{df1_name}: {df1_col}", 
                                 mode= 'lines',
                                 line=dict(color=df1_color),
                                 legend=legend_name),
                                 row=row, col=col,
                                 )
        fig.add_trace(go.Scatter(x=df2['time'], y=df2[df2_col], 
                                 name=f"{df2_name}: {df2_col}", 
                                 mode= 'lines', 
                                 line=dict(color=df2_color, dash='longdash'),
                                 legend=legend_name),
                                 row=row, col=col,
                                 )
        fig.update_xaxes(title_text='Time [s]',row=row, col=col)

    # Update layout for legends and overall figure
    for i in range(1, nrows * ncols + 1):
        legend_name = "legend" if i == 1 else f"legend{i}"

        xaxis_name = "xaxis" if i == 1 else f"xaxis{i}"
        yaxis_name = "yaxis" if i == 1 else f"yaxis{i}"

        xaxis = getattr(fig.layout, xaxis_name)
        yaxis = getattr(fig.layout, yaxis_name)

        # Top-right corner of this subplot
        x = xaxis.domain[1]
        y = yaxis.domain[1]

        fig.update_layout(
        **{
            legend_name: dict(
                x=x- 0.01,
                y=y- 0.01,
                orientation="v",
                xanchor="right",
                yanchor="top",
                borderwidth=0,
                bgcolor="rgba(0,0,0,0)"
            )
        }
        )

    # Height of the figure is 300 pixels per row of subplots
    fig.update_layout(height=300*nrows)

    # Add filepath and timestamp to the title
    date_time = datetime.now().strftime("%B %d, %Y %I:%M %p")
    fig.update_layout(
    title=dict(
        text=f"{df1_name} vs {df2_name}<br>{figure_filepath}<br>{date_time}<br>",
        x=0,
        xanchor="left",
    )
)
    fig.write_html(figure_filepath)


def create_static_figures(output_directory):
    # ----------------------------------------------------------------------
    # Read the outputs of the simulations
    # ----------------------------------------------------------------------

    # Read states of EMT simulation
    emt_no_control = pl.read_csv(os.path.join(output_directory, "emt_without_control", "gfmi_18a_0.csv"))

    # Read states of SSM simulation
    ssm = pl.read_csv(os.path.join(output_directory, "small_signal_model", "gfmi_18a_0.csv"))
    ssm = ssm.with_columns(
                        (pl.col("v_lcl_sh_d") * pl.col("i_bus_d") + pl.col("v_lcl_sh_q") * pl.col("i_bus_q")).alias("p_sh"),
                        )


    # Read states of balanced truncation simulation
    mor = pl.read_csv(os.path.join(output_directory, "model_order_reduction", "gfmi_18a_0.csv"))
    mor = mor.with_columns(
                        (pl.col("v_lcl_sh_d") * pl.col("i_bus_d") + pl.col("v_lcl_sh_q") * pl.col("i_bus_q")).alias("p_sh"),
                        )

    # Read matrix A of the small-signal model
    ssm_A = pl.read_csv(os.path.join(output_directory, "small_signal_model", "A.csv"))
    ssm_A = ssm_A[0:, 1:].to_numpy()

    # Read matrix A of the closed-loop system with output feedback control
    rom_Acl = pl.read_csv(os.path.join(output_directory, "closed_loop_A.csv"))
    rom_Acl = rom_Acl[0:, 0:].to_numpy()

    # Read states of the EMT with control implemented
    emt_with_control = pl.read_csv(os.path.join(output_directory, "emt_with_control", "gfmi_18a_0.csv"))


    # ----------------------------------------------------------------------
    # Make plots
    # ----------------------------------------------------------------------

    # Make a plot 1 x 4
    # Plot 1: EMT simulation without control. Active power injected by the GFMI (proposed project)
    # Plot 2: SSM and ROM simulation without control. Active power injected by the GFMI (proposed project)
    # Plot 3: Eigenvalues of the SSM with and without control.
    # Plot 4: EMT simulation with control. Active power injected by the GFMI (proposed project)

    # Plotting settings
    #plt.style.use(['science','ieee'])
    plt.rcParams['text.usetex'] = False
    # Apply inward direction to all future plots
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    plt.rc('font',**{'family':'serif','serif':['Times'], 'size': 7})
    plt.rcParams['axes.formatter.useoffset'] = False # this prevent scientific notation in y-axis
    orange = "#E69F00"
    blue = "#56B4E9"
    green = "#009E73" 
    purple = "#CC79A7"
    linewidth = 0.80

    # Create a plot
    fig, ax = plt.subplots(nrows=1, ncols=4, figsize=(8.5, 2.3), dpi=1000)

    # Share y-axis between the first 3
    ax[1].sharey(ax[0])
    ax[3].sharey(ax[0])

    # --------------------------------------------------------------------------------------------
    # Plot 1: EMT simulation without control. Active power injected by the GFMI (proposed project)
    # --------------------------------------------------------------------------------------------

    ax[0].plot(emt_no_control['time'], emt_no_control['p_sh'], color=blue, linewidth=linewidth, label='EMT')
    ax[0].set_xlabel("Time [s]")
    ax[0].set_ylabel("Active power [MW]")
    ax[0].set_xlim([0, 1])
    ax[0].set_title("a)")

    # Compute times between two peaks of the active power injected by the GFMI (proposed project) in the EMT simulation without control
    y = emt_no_control['p_sh'].to_numpy()
    t = emt_no_control['time'].to_numpy()
    peaks, _ = find_peaks(y, height=0)
    peak_times, peak_values = t[peaks], y[peaks]
    selected_peak = 9 # select the peak 
    # Compute the time between two peaks
    time_between_peaks = peak_times[selected_peak] - peak_times[selected_peak - 1]
    # Compute the frequency of oscillation
    frequency_of_oscillation = 1 / time_between_peaks

    # add arrow to the plot indicating the time between two peaks
    ax[0].annotate("", xy=(peak_times[selected_peak], peak_values[selected_peak]), xytext=(peak_times[selected_peak - 1], peak_values[selected_peak - 1]),
                arrowprops=dict(arrowstyle="|-|", color='black', linewidth=0.8, mutation_scale=2))
    # add text to the plot indicating the frequency of oscillation
    ax[0].text((peak_times[selected_peak] + peak_times[selected_peak - 1]) / 2, 
            peak_values[selected_peak] + 0.01, f"f = {frequency_of_oscillation:.2f} Hz", ha='center', va='bottom')

    # Legend
    leg = ax[0].legend(loc='lower right', frameon=True, ncol=2, fontsize=6, handlelength=1.0, handletextpad=0.5, borderpad=0.5, labelspacing=0.2, edgecolor="black")
    leg.get_frame().set_linewidth(0.5)

    # ----------------------------------------------------------------------------------------------------
    # Plot 2: SSM and ROM simulation without control. Active power injected by the GFMI (proposed project)
    # ----------------------------------------------------------------------------------------------------
    ax[1].plot(ssm['time'], ssm['p_sh'], color=blue, linewidth=linewidth, label='SSM')
    ax[1].plot(mor['time'], mor['p_sh'], color=purple, linewidth=linewidth, label='ROM')
    ax[1].set_xlabel("Time [s]")
    ax[1].set_xlim([0, 1])
    ax[1].set_title("b)")
    ax[1].set_ylabel("Active power [MW]")

    y = ssm['p_sh'].to_numpy()
    t = ssm['time'].to_numpy()
    peaks, _ = find_peaks(y, height=0)
    peak_times, peak_values = t[peaks], y[peaks]
    selected_peak = 2 # select the peak 
    # Compute the time between two peaks
    time_between_peaks = peak_times[selected_peak] - peak_times[selected_peak - 1]
    # Compute the frequency of oscillation
    frequency_of_oscillation = 1 / time_between_peaks

    ax[1].annotate("", xy=(peak_times[selected_peak], peak_values[selected_peak]), xytext=(peak_times[selected_peak - 1], peak_values[selected_peak - 1]),
                arrowprops=dict(arrowstyle="|-|", color='black', linewidth=0.8, mutation_scale=2))
    # add text to the plot indicating the frequency of oscillation
    ax[1].text((peak_times[selected_peak] + peak_times[selected_peak - 1]) / 2, 
            peak_values[selected_peak] + 0.01, f"f = {frequency_of_oscillation:.2f} Hz", ha='center', va='bottom')

    y = mor['p_sh'].to_numpy()
    t = mor['time'].to_numpy()
    peaks, _ = find_peaks(-y)
    peak_times, peak_values = t[peaks], y[peaks]
    selected_peak = 1 # select the peak
    # Compute the time between two peaks
    time_between_peaks = peak_times[selected_peak] - peak_times[selected_peak - 1]
    # Compute the frequency of oscillation
    frequency_of_oscillation = 1 / time_between_peaks

    ax[1].annotate("", xy=(peak_times[selected_peak], peak_values[selected_peak]), xytext=(peak_times[selected_peak - 1], peak_values[selected_peak - 1]),
                arrowprops=dict(arrowstyle="|-|", color='black', linewidth=0.8, mutation_scale=2))
    # add text to the plot indicating the frequency of oscillation
    ax[1].text((peak_times[selected_peak] + peak_times[selected_peak - 1]) / 2, 
            peak_values[selected_peak] - 0.05, f"f = {frequency_of_oscillation:.2f} Hz", ha='center', va='bottom')

    # Legend
    leg = ax[1].legend(loc='lower right', frameon=True, ncol=1, fontsize=6, handlelength=1.0, handletextpad=0.5, borderpad=0.5, labelspacing=0.2, edgecolor="black")
    leg.get_frame().set_linewidth(0.5)

    # -------------------------------------------------------------
    # Plot 3: Eigenvalues of the SSM with and without control.
    # -------------------------------------------------------------
    eigenvalues_ssm = np.linalg.eigvals(ssm_A)
    eigenvalues_rom_cl = np.linalg.eigvals(rom_Acl)
    ax[2].scatter(eigenvalues_ssm.real, eigenvalues_ssm.imag, color=blue, s=10, marker='x', label='SSM')
    ax[2].scatter(eigenvalues_rom_cl.real, eigenvalues_rom_cl.imag, color=orange, s=10, marker='s', facecolors='none', label='ROM+controller', linewidths=0.8)

    # Find eigenvalues with largest real part
    dominant_ssm_eigenvalue = eigenvalues_ssm[np.argmax(eigenvalues_ssm.real)]
    dominant_rom_eigenvalue = eigenvalues_rom_cl[np.argmax(eigenvalues_rom_cl.real)]

    ax[2].set_yscale("symlog")
    ax[2].set_xscale("symlog")
    ax[2].set_title("c)")

    # Compute the damping ratio of the dominant eigenvalue of the open-loop system
    damping_ratio_ssm = -dominant_ssm_eigenvalue.real / np.abs(dominant_ssm_eigenvalue)
    fn_ssm = np.abs(dominant_ssm_eigenvalue)/(2*np.pi)
    # Compute the damping ratio of the dominant eigenvalue of the closed-loop system
    damping_ratio_rom = -dominant_rom_eigenvalue.real / np.abs(dominant_rom_eigenvalue)
    fn_rom = np.abs(dominant_rom_eigenvalue)/(2*np.pi)

    # Add text to the plot indicating the damping ratio and natural frequency of the dominant eigenvalue of the open-loop system
    x_text = dominant_ssm_eigenvalue.real-2
    y_text = 10*dominant_ssm_eigenvalue.imag
    ax[2].text(x_text, y_text, f"ζ = {damping_ratio_ssm:.1f}\n f = {fn_ssm:.2f} Hz", ha='center', va='bottom')

    # Arrow going from eigenvalue to text
    ax[2].annotate("", xy=(dominant_ssm_eigenvalue.real, dominant_ssm_eigenvalue.imag), xytext=(x_text, y_text),
                arrowprops=dict(arrowstyle="->", color='black', linewidth=0.8))


    # Add text to the plot indicating the damping ratio and natural frequency of the dominant eigenvalue of the closed-loop system
    x_text = dominant_rom_eigenvalue.real+0.9
    y_text = 0.1*dominant_rom_eigenvalue.imag
    ax[2].text(x_text, y_text, f"ζ = {damping_ratio_rom:.1f}\n f = {fn_rom:.2f} Hz", ha='center', va='top')

    # Arrow going from eigenvalue to text
    ax[2].annotate("", xy=(dominant_rom_eigenvalue.real, dominant_rom_eigenvalue.imag), xytext=(x_text, y_text),
                arrowprops=dict(arrowstyle="->", color='black', linewidth=0.8))

    ax[2].set_xlabel("Real")
    ax[2].set_ylabel("Imaginary")

    # Legend
    leg = ax[2].legend(loc='lower right', frameon=True, ncol=1, fontsize=6, handlelength=1.0, handletextpad=0.5, borderpad=0.5, labelspacing=0., edgecolor="black")
    leg.get_frame().set_linewidth(0.5)

    # --------------------------------------------------------------------------------------------
    # Plot 4: EMT simulation with control. Active power injected by the GFMI (proposed project)
    # --------------------------------------------------------------------------------------------
    ax[3].plot(emt_with_control['time'], emt_with_control['p_sh'], color=orange, linewidth=linewidth, label='EMT+controller')
    ax[3].set_xlabel("Time [s]")
    ax[3].set_ylabel("Active power [MW]")
    ax[3].set_xlim([0, 1])
    ax[3].set_title("d)")

    leg = ax[3].legend(loc='lower right', frameon=True, ncol=1, fontsize=6, handlelength=1.0, handletextpad=0.5, borderpad=0.5, labelspacing=0.2, edgecolor="black")
    leg.get_frame().set_linewidth(0.5)

    # Spacing between subplots
    fig.subplots_adjust(wspace=0.30, hspace=0.17)

    # Save figure
    plt.savefig(os.path.join(output_directory, "pipeline_figure.pdf"), dpi=1000, bbox_inches="tight", pad_inches=0.2)

