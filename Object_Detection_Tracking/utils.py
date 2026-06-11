from collections import Counter
import pandas as pd
import os


def count_objects(results):

    counts = Counter()

    result = results[0]

    if result.boxes is not None:

        for cls in result.boxes.cls:

            class_name = result.names[int(cls)]

            counts[class_name] += 1

    return dict(counts)


def update_total_counts(
    current_counts,
    total_counts
):

    for obj, count in current_counts.items():

        total_counts[obj] = (
            total_counts.get(obj, 0)
            + count
        )

    return total_counts


def save_detection_history(
    total_counts,
    filename="detection_history.csv"
):

    df = pd.DataFrame(
        total_counts.items(),
        columns=[
            "Object",
            "Count"
        ]
    )

    df.to_csv(
        filename,
        index=False
    )

    return df


def create_dataframe(
    total_counts
):

    return pd.DataFrame(
        total_counts.items(),
        columns=[
            "Object",
            "Count"
        ]
    )


def ensure_output_folder():

    if not os.path.exists("outputs"):

        os.makedirs("outputs")