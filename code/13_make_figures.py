"""
13_make_figures.py
====================
Generates Figures 2-7 (300 DPI) from the CSV outputs already written by
scripts 02-08. Must be run after those scripts (run_all.py handles the
ordering automatically).

Produces:
  figures/Figure2_sigma_beta_convergence.png
  figures/Figure3_kernel_density.png
  figures/Figure4_markov_heatmap.png
  figures/Figure5_moran_scatterplot.png
  figures/Figure6_spatial_markov.png
  figures/Figure7_extensive_intensive.png
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from _paths import OUTPUT_DIR, SUPPORTING_DIR, FIG_DIR, FIGURE_DPI


def figure2():
    sigma = pd.read_csv(SUPPORTING_DIR / "sigma_convergence_full_series.csv")
    subperiod = pd.read_csv(OUTPUT_DIR / "Table4c_beta_convergence_by_subperiod.csv")

    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax1.plot(sigma["Year"], sigma["CV"], color="#1f77b4", marker="o", markersize=3, label="Coefficient of variation (CV)")
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Coefficient of variation", color="#1f77b4")
    ax1.tick_params(axis="y", labelcolor="#1f77b4")

    ax2 = ax1.twinx()
    mid_years = [2002.5, 2007.5, 2012.5, 2017.5, 2022]
    betas = subperiod["Beta"].astype(str).str.replace("+", "", regex=False).astype(float)
    ax2.bar(mid_years, betas, width=4, color="#d62728", alpha=0.4, label="Sub-period beta-convergence coefficient")
    ax2.axhline(0, color="#d62728", linewidth=0.6)
    ax2.set_ylabel("Sub-period beta-convergence coefficient", color="#d62728")
    ax2.tick_params(axis="y", labelcolor="#d62728")

    fig.suptitle("Sigma-Convergence (CV) and Sub-Period Beta-Convergence, 2000-2024", fontsize=11, fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "Figure2_sigma_beta_convergence.png", dpi=FIGURE_DPI)
    plt.close(fig)
    print("Figure 2 written.")


def figure3():
    density = pd.read_csv(SUPPORTING_DIR / "kernel_density_grid.csv")
    fig, ax = plt.subplots(figsize=(7, 5))
    colors = {2000: "#1f77b4", 2012: "#ff7f0e", 2024: "#2ca02c"}
    for year, g in density.groupby("year"):
        ax.plot(g["relative_yield"], g["density"], label=str(year), color=colors.get(year))
    ax.set_xlabel("Relative milk yield (district / national mean)")
    ax.set_ylabel("Density")
    ax.set_title("Kernel Density Evolution of Relative Milk Yield", fontsize=11, fontweight="bold")
    ax.legend(title="Year")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "Figure3_kernel_density.png", dpi=FIGURE_DPI)
    plt.close(fig)
    print("Figure 3 written.")


def figure4():
    table7 = pd.read_csv(OUTPUT_DIR / "Table6_markov_transition_matrix.csv", index_col=0)
    fig, ax = plt.subplots(figsize=(5.5, 5))
    im = ax.imshow(table7.values, cmap="YlOrRd", vmin=0, vmax=0.9)
    ax.set_xticks(range(4))
    ax.set_yticks(range(4))
    ax.set_xticklabels(table7.columns)
    ax.set_yticklabels(table7.index)
    for i in range(4):
        for j in range(4):
            ax.text(j, i, f"{table7.values[i, j]:.2f}", ha="center", va="center", fontsize=9)
    ax.set_title("Markov Transition Matrix Heatmap\n(1-year horizon, pooled 2000-2024)", fontsize=11, fontweight="bold")
    fig.colorbar(im, ax=ax, label="Transition probability", shrink=0.8)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "Figure4_markov_heatmap.png", dpi=FIGURE_DPI)
    plt.close(fig)
    print("Figure 4 written.")


def figure5():
    scatter = pd.read_csv(SUPPORTING_DIR / "moran_scatterplot_data.csv")
    morans = pd.read_csv(OUTPUT_DIR / "Table7_morans_i.csv")
    i_val = morans.iloc[0]["Moran's I"]
    p_val = morans.iloc[0]["p (permutation)"]

    fig, ax = plt.subplots(figsize=(6.5, 6))
    ax.scatter(scatter["growth_dev"], scatter["spatial_lag_dev"], color="#1f77b4", edgecolor="white", s=40)
    b = np.polyfit(scatter["growth_dev"], scatter["spatial_lag_dev"], 1)
    xs = np.linspace(scatter["growth_dev"].min(), scatter["growth_dev"].max(), 50)
    ax.plot(xs, np.polyval(b, xs), color="#d62728", label=f"Slope (Moran's I) = {i_val:.3f}")
    ax.axhline(0, color="grey", linewidth=0.6)
    ax.axvline(0, color="grey", linewidth=0.6)
    ax.set_xlabel("District yield growth, 2000-2024 (deviation from mean)")
    ax.set_ylabel("Spatial lag: neighbours' average growth\n(deviation from mean)")
    ax.set_title("Moran Scatterplot: Milk-Yield Growth\n(Queen contiguity weights)", fontsize=11, fontweight="bold")
    ax.legend(loc="upper left", frameon=True)
    ax.text(0.97, 0.03, f"Global Moran's I = {i_val:.3f}, permutation p = {p_val:.3f}\n(no significant spatial clustering)"
            if p_val >= 0.05 else f"Global Moran's I = {i_val:.3f}, permutation p = {p_val:.3f}",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=8,
            bbox=dict(boxstyle="round", facecolor="white", edgecolor="grey"))
    fig.tight_layout()
    fig.savefig(FIG_DIR / "Figure5_moran_scatterplot.png", dpi=FIGURE_DPI)
    plt.close(fig)
    print("Figure 5 written.")


def figure6():
    mats = pd.read_csv(SUPPORTING_DIR / "spatial_markov_matrices.csv")
    uncond = pd.read_csv(OUTPUT_DIR / "Table6_markov_transition_matrix.csv", index_col=0)
    labels = ["Q1(low)", "Q2", "Q3", "Q4(high)"]

    fig, axes = plt.subplots(1, 5, figsize=(18, 4))
    panels = [("Unconditional", uncond.values)] + [
        (f"Neighbour = {'Q'+str(q)+('(low)' if q==1 else '(high)' if q==4 else '')}",
         mats[mats["neighbour_quartile"] == q].pivot(index="from", columns="to", values="probability").reindex(index=labels, columns=labels).values)
        for q in [1, 2, 3, 4]
    ]
    for ax, (title, P) in zip(axes, panels):
        im = ax.imshow(P, cmap="YlOrRd", vmin=0, vmax=0.9)
        ax.set_xticks(range(4)); ax.set_yticks(range(4))
        ax.set_xticklabels(labels, fontsize=7, rotation=45)
        ax.set_yticklabels(labels, fontsize=7)
        for i in range(4):
            for j in range(4):
                ax.text(j, i, f"{P[i, j]:.2f}", ha="center", va="center", fontsize=7)
        ax.set_title(title, fontsize=9, fontweight="bold")
    fig.suptitle("Spatial Markov Chain: Quartile Transitions Conditioned on Neighbouring Districts' Quartile\n(Rey, 2001)", fontsize=11, fontweight="bold")
    fig.colorbar(im, ax=axes, shrink=0.6, label="Transition probability")
    fig.savefig(FIG_DIR / "Figure6_spatial_markov.png", dpi=FIGURE_DPI, bbox_inches="tight")
    plt.close(fig)
    print("Figure 6 written.")


def figure7():
    m = pd.read_csv(SUPPORTING_DIR / "ext_int_by_district.csv")
    m = m.reindex(m["delta_milk"].abs().sort_values(ascending=False).index).head(20)
    m = m.sort_values("delta_milk", ascending=True)

    ext_disp = m["ext_share"].clip(-1, 2) * 100
    int_disp = m["int_share"].clip(-1, 2) * 100
    labels = m["region"].str.replace(" district", "").str.replace(" city", "")

    fig, ax = plt.subplots(figsize=(8, 8))
    y = np.arange(len(m))
    ax.barh(y, ext_disp, color="#e8a598", label="Extensive (herd growth)", height=0.7)
    ax.barh(y, int_disp, left=ext_disp, color="#7fa8c9", label="Intensive (yield growth)", height=0.7)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=8)
    ax.axvline(0, color="#333333", linewidth=0.8)
    ax.set_xlabel("Share of milk production growth, 2000-2024 (%, winsorized at [-100,200])")
    ax.set_title("Extensive vs. Intensive Margins of Dairy Growth by District", fontsize=11, fontweight="bold")
    ax.legend(loc="lower right", frameon=False)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "Figure7_extensive_intensive.png", dpi=FIGURE_DPI)
    plt.close(fig)
    print("Figure 7 written.")


def main():
    figure2()
    figure3()
    figure4()
    figure5()
    figure6()
    figure7()


if __name__ == "__main__":
    main()
