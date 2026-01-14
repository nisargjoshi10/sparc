import os
import glob
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
from ase.io import read
import ipywidgets as widgets
from IPython.display import display, clear_output
import urllib.request

# ------------------------------------------------------------------------------
# Load Custom Plot Style (Dark Theme)
# ------------------------------------------------------------------------------
style_url = "https://github.com/dhaitz/matplotlib-stylesheets/raw/master/pitayasmoothie-light.mplstyle"
style_path = "pitayasmoothie-light.mplstyle"
if not os.path.isfile(style_path):
    urllib.request.urlretrieve(style_url, style_path)
plt.style.use(style_path)

# ------------------------------------------------------------------------------
# Utilities
# ------------------------------------------------------------------------------
def scan_iterations(root):
    dirs = sorted(glob.glob(os.path.join(root, "iter_*")))
    return [int(d.split("_")[-1]) for d in dirs if d.split("_")[-1].isdigit()]

def load_iteration_data(root, subfolder, traj_file, iterations, prop_fn):
    """
    Return
    ------
        data_dict: {iter_num [values/step]}
        max_len: max among selected iterations
    """
    data_dict = {}
    max_len = 0
    for iter_num in iterations:
        traj_path = os.path.join(root, f"iter_{iter_num:06d}", subfolder, traj_file)
        if not os.path.isfile(traj_path):
            print(f"[Skipped] Missing: {traj_path}")
            continue
        try:
            traj = read(traj_path, index=":")
            values = [prop_fn(atoms) for atoms in traj]
            data_dict[iter_num] = values
            max_len = max(max_len, len(values))
        except Exception as e:
            print(f"[Error] {traj_path} — {e}")
    return data_dict, max_len

def plot_data(data_dict, max_len, ylabel, title=None, cmap=plt.cm.cool, print_means=False):
    fig = plt.figure(figsize=(10, 5), dpi=150)
    colors = cmap(np.linspace(0.2, 0.9, len(data_dict)))

    for i, (iter_num, values) in enumerate(sorted(data_dict.items())):
        plt.plot(values, lw=2.0, alpha=0.8, color=colors[i], label=f"Iter {iter_num}")
        if print_means:
            print(f"✔ Iter {iter_num}: mean = {np.mean(values):.3f}")

    plt.xlabel("Steps", fontsize=16)
    plt.ylabel(ylabel, fontsize=16)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.grid(alpha=0.3, ls='-.')

    # Apply scientific notation to x-axis
    ax = plt.gca()
    ax.xaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax.ticklabel_format(axis='x', style='sci', scilimits=(0, 0))
    
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=5, fontsize=12)
    plt.tight_layout()
    plt.xlim(0, max_len)
    plt.show()

# ------------------------------------------------------------------------------
# Plot Tab Generator for Generic Properties
# ------------------------------------------------------------------------------
def make_plot_tab(label, prop_fn, ylabel):
    print_means = label == "Temperature"  # Only show means for Temperature

    root_input = widgets.Text(value=".", description="Root:", layout=widgets.Layout(width="45%"))
    subfolder_input = widgets.Text(value="02.dpmd", description="Subfolder:", layout=widgets.Layout(width="30%"))
    traj_input = widgets.Text(value="dpmd.traj", description="Trajectory:", layout=widgets.Layout(width="25%"))
    iteration_multi = widgets.SelectMultiple(description="Iterations:", layout=widgets.Layout(width="100%", height="120px"))
    refresh_button = widgets.Button(description="Refresh Iterations", icon='refresh', button_style='info')
    plot_button = widgets.Button(description=f"Plot {label}", icon='line-chart', button_style='success')
    output_plot = widgets.Output()

    def refresh(_):
        found = scan_iterations(root_input.value.strip())
        if not found:
            print("No valid 'iter_xxxxxx' folders found.")
            return
        iteration_multi.options = found
        iteration_multi.value = tuple(found)

    def plot(_):
        with output_plot:
            clear_output(wait=True)
            if not iteration_multi.value:
                print("Please select at least one iteration.")
                return
            root, subfolder, traj_file = root_input.value, subfolder_input.value, traj_input.value
            data_dict, max_len = load_iteration_data(root, subfolder, traj_file, iteration_multi.value, prop_fn)
            if not data_dict:
                print(f"No valid {label.lower()} data found.")
                return
            plot_data(data_dict, max_len, ylabel, print_means=print_means)

    refresh_button.on_click(refresh)
    plot_button.on_click(plot)

    return widgets.VBox([
        widgets.HTML(f"<h3 style='margin-top:10px; color:#1abc9c'><b>{label}</b></h3>"),
        widgets.HBox([root_input, subfolder_input, traj_input]),
        iteration_multi,
        widgets.HBox([refresh_button, plot_button]),
        output_plot
    ])
# ------------------------------------------------------------------------------
# Geometry Plot Tab (Bond / Angle / Dihedral)
# ------------------------------------------------------------------------------
def make_geometry_tab():
    root_input = widgets.Text(value=".", description="Root:", layout=widgets.Layout(width="45%"))
    subfolder_input = widgets.Text(value="02.dpmd", description="Subfolder:", layout=widgets.Layout(width="30%"))
    traj_input = widgets.Text(value="dpmd.traj", description="Trajectory:", layout=widgets.Layout(width="25%"))
    geo_type = widgets.Dropdown(options=["Bond", "Angle", "Dihedral"], value="Bond", description="Type:")
    idx_input = widgets.Text(value="0 1", description="Indices:", placeholder="e.g. 0 1 [or] 0 1 2 [or] 0 1 2 3")
    iteration_multi = widgets.SelectMultiple(description="Iterations:", layout=widgets.Layout(width="100%", height="120px"))
    refresh_button = widgets.Button(description="Refresh Iterations", icon='refresh', button_style='info')
    plot_button = widgets.Button(description="Plot Geometry", icon='chart-line', button_style='success')
    output_plot = widgets.Output()

    def refresh(_):
        found = scan_iterations(root_input.value.strip())
        if not found:
            print("No valid 'iter_xxxxxx' folders found.")
            return
        iteration_multi.options = found
        iteration_multi.value = tuple(found)

    def plot(_):
        with output_plot:
            clear_output(wait=True)
            try:
                indices = list(map(int, idx_input.value.strip().split()))
            except ValueError:
                print("Invalid indices format.")
                return
            if geo_type.value == "Bond":
                need = 2
            elif geo_type.value == "Angle":
                need = 3
            elif geo_type.value == "Dihedral":
                need = 4
            if len(indices) != need:
                print(f"{geo_type.value} requires {need} indices.")
                return

            # --- basic paths ---
            root, subfolder, traj_file = root_input.value, subfolder_input.value, traj_input.value
            if not iteration_multi.value:
                print("Please select at least one iteration.")
                return

            # --- pretty label (Element_{index}) ---
            label_str = "?"
            atoms_sample = None
            try:
                first_iter = iteration_multi.value[0]
                first_path = os.path.join(root, f"iter_{first_iter:06d}", subfolder, traj_file)
                atoms_sample = read(first_path, index=0)
                symbols = atoms_sample.get_chemical_symbols()
                label_str = " - ".join(f"{symbols[i]}_{{{i}}}" for i in indices)  # e.g., C_{0} - N_{1} - C_{2} - O_{3}
            except Exception:
                pass

            # --- property function (with dihedral fallback for older ASE) ---
            if geo_type.value == "Bond":
                prop_fn = lambda at: at.get_distance(*indices)
            elif geo_type.value == "Angle":
                prop_fn = lambda at: at.get_angle(*indices)
            else:
                # Use Atoms.get_dihedral if present, else ase.geometry.dihedral
                has_get_dihedral = hasattr(atoms_sample, "get_dihedral") if atoms_sample is not None else False
                if has_get_dihedral:
                    prop_fn = lambda at: at.get_dihedral(*indices)
                else:
                    from ase.geometry import dihedral
                    prop_fn = lambda at: dihedral(at.positions[indices[0]],
                                                  at.positions[indices[1]],
                                                  at.positions[indices[2]],
                                                  at.positions[indices[3]],
                                                  degrees=True)

            # --- load and plot ---
            data_dict, max_len = load_iteration_data(root, subfolder, traj_file, iteration_multi.value, prop_fn)
            if not data_dict:
                print("No valid geometry data found.")
                return

            # --- ylabel in LaTeX style (consistent with your originals) ---
            if geo_type.value == "Bond":
                ylabel = rf"$d[\mathrm{{{label_str}}}]\,(\mathrm{{\AA}})$"
            elif geo_type.value == "Angle":
                ylabel = rf"$\mathrm{{\theta}}[\mathrm{{{label_str}}}]\,(\mathrm{{deg.}})$"
            else:
                ylabel = rf"$\mathrm{{\phi}}[\mathrm{{{label_str}}}]\,(\mathrm{{deg.}})$"

            plot_data(data_dict, max_len, ylabel, title=f"{geo_type.value}")

    refresh_button.on_click(refresh)
    plot_button.on_click(plot)

    return widgets.VBox([
        widgets.HTML("<h3 style='margin-top:10px; color:#f39c12'><b>Geometry (Bond / Angle / Dihedral)</b></h3>"),
        widgets.HBox([root_input, subfolder_input, traj_input]),
        widgets.HBox([geo_type, idx_input, refresh_button, plot_button]),
        iteration_multi,
        output_plot
    ])
# ------------------------------------------------------------------------------
# Launch the Viewer
# ------------------------------------------------------------------------------
def WorkFlowAnalysis():
    '''
    Interactive analysis and visualization tools for monitoring molecular dynamics
    simulations across multiple active learning iterations. Provides utilities for
    loading trajectory data, extracting physical properties, and creating plots
    with Jupyter widget interfaces.
    
    Main Features
    -------------
    - Scan and load iteration folders with trajectory files.
    - Plot temperature, energies, and user-defined geometric quantities.
    - Interactive Jupyter widgets for selecting iterations, trajectory files, and plotting results.
    - Geometry tab for analyzing bond lengths, angles, and dihedrals.
    
    Dependencies
    ------------
    - numpy
    - matplotlib
    - ase (Atomic Simulation Environment)
    - ipywidgets
    '''
    tab_defs = [
        ("Temperature", lambda a: a.get_temperature(), "Temperature (K)"),
        ("Total Energy", lambda a: a.get_total_energy(), "Total Energy (eV)"),
        ("Potential Energy", lambda a: a.get_potential_energy(), "Potential Energy (eV)"),
        ("Kinetic Energy", lambda a: a.get_kinetic_energy(), "Kinetic Energy (eV)")
    ]
    tabs = widgets.Tab()
    widgets_list = [make_plot_tab(*tup) for tup in tab_defs] + [make_geometry_tab()]
    tabs.children = widgets_list
    for i, (label, _, _) in enumerate(tab_defs):
        tabs.set_title(i, label)
    tabs.set_title(len(tab_defs), "Geometry")
    display(tabs)
########################################################################################################
#                                      End of File
########################################################################################################
