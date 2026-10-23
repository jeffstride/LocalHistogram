import statistics

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def plot_grade_histogram(grades, boundaries, filename):
    """Plot a histogram of grades, annotate stats and per-bucket counts on it, save to filename.

    Buckets are [b0, b1), [b1, b2), ..., with the last bucket including its upper edge.
    Returns the list of counts per bucket.
    """
    if not grades:
        raise ValueError("grades must not be empty")
    if len(boundaries) < 2:
        raise ValueError("boundaries must contain at least two values")
    boundaries = sorted(boundaries)

    fig, ax = plt.subplots()
    counts, _, _ = ax.hist(grades, bins=boundaries, edgecolor="black")
    counts = [int(c) for c in counts]
    percents = [round(100 * c / len(grades)) for c in counts]
    mean = statistics.mean(grades)
    median = statistics.median(grades)

    ax.set_xticks(boundaries)
    ax.set_xlabel("Grade")
    ax.set_ylabel("Number of students")
    ax.set_title("Student Grade Distribution")
    ax.text(
        0.02,
        0.98,
        f"Mean: {mean:.2f}\nmedian: {median:.2f}\nCounts: {counts}\nPercent: {percents}",
        transform=ax.transAxes,
        ha="left",
        va="top",
        bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.8},
    )
    fig.savefig(filename, bbox_inches="tight")
    plt.close(fig)
    return counts

def test_hist():
    sample = [55.5, 62, 70.25, 78, 81, 85.5, 88, 92, 95.5, 99, 73, 67]
    plot_grade_histogram(sample, [50, 60, 70, 80, 90, 100], "grades_histogram.png")

if __name__ == "__main__":
    print("ran main entry")