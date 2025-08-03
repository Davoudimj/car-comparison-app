import streamlit as st
import pandas as pd
import numpy as np
import io

st.set_page_config(page_title="Car Comparison App (TOPSIS)", layout="centered")
st.title("🚗 Car Comparison App using TOPSIS")

st.markdown("""
This app allows you to:
- Enter up to 5 criteria (e.g., price, mileage)
- Specify whether each criterion is a **Cost** (lower is better) or **Benefit** (higher is better)
- Assign a weight to each criterion (total must be 1.0)
- Enter values for each alternative (car)
- Compute scores using the **TOPSIS** method
- Download detailed calculation steps
""")

# Step 1: Input number of criteria and alternatives
num_criteria = st.sidebar.slider("Number of Criteria", min_value=2, max_value=5, value=3)
num_alternatives = st.sidebar.slider("Number of Alternatives (Cars)", min_value=2, max_value=10, value=3)

# Step 2: Input criteria names, types and weights
st.header("Step 1: Define Criteria")
criteria = []
types = []
weights = []

col1, col2, col3 = st.columns(3)
for i in range(num_criteria):
    with col1:
        crit = st.text_input(f"Criterion {i+1} Name", key=f"crit_{i}")
    with col2:
        typ = st.selectbox(f"Type", ["Benefit", "Cost"], key=f"type_{i}")
    with col3:
        wt = st.number_input(f"Weight (0-1)", min_value=0.0, max_value=1.0, step=0.01, key=f"wt_{i}")
    criteria.append(crit)
    types.append(typ)
    weights.append(wt)

# Validate weight sum
if sum(weights) > 1.0:
    st.error("The total weight exceeds 1. Please adjust the weights so they sum to 1.")
elif sum(weights) < 1.0:
    st.warning("The total weight is less than 1. Results may be biased.")

# Step 3: Input data for each car
st.header("Step 2: Enter Alternative (Car) Data")
alternatives = []
data = []

for i in range(num_alternatives):
    car_name = st.text_input(f"Alternative {i+1} Name", key=f"alt_{i}")
    alternatives.append(car_name)
    row = []
    for j in range(num_criteria):
        value = st.number_input(f"{car_name} - {criteria[j]}", key=f"val_{i}_{j}")
        row.append(value)
    data.append(row)

# Run TOPSIS Calculation
if st.button("🔍 Run TOPSIS Analysis"):
    df = pd.DataFrame(data, columns=criteria, index=alternatives)
    matrix = df.to_numpy(dtype=float)
    weights_np = np.array(weights)

    steps_log = []

    # Step 1: Normalize matrix
    norm_matrix = matrix / np.sqrt((matrix**2).sum(axis=0))
    steps_log.append(pd.DataFrame(norm_matrix, columns=criteria, index=alternatives).round(4).rename_axis("Normalized Matrix"))

    # Step 2: Weighted normalized matrix
    weighted_matrix = norm_matrix * weights_np
    steps_log.append(pd.DataFrame(weighted_matrix, columns=criteria, index=alternatives).round(4).rename_axis("Weighted Normalized Matrix"))

    # Step 3: Identify ideal and negative-ideal solutions
    ideal = []
    negative_ideal = []
    for j in range(num_criteria):
        if types[j] == "Benefit":
            ideal.append(np.max(weighted_matrix[:, j]))
            negative_ideal.append(np.min(weighted_matrix[:, j]))
        else:  # Cost
            ideal.append(np.min(weighted_matrix[:, j]))
            negative_ideal.append(np.max(weighted_matrix[:, j]))
    ideal = np.array(ideal)
    negative_ideal = np.array(negative_ideal)

    steps_log.append(pd.DataFrame([ideal, negative_ideal], index=["Ideal", "Negative Ideal"], columns=criteria).round(4).rename_axis("Ideal Solutions"))

    # Step 4: Distance to ideal and negative-ideal
    dist_to_ideal = np.sqrt(((weighted_matrix - ideal) ** 2).sum(axis=1))
    dist_to_negative = np.sqrt(((weighted_matrix - negative_ideal) ** 2).sum(axis=1))

    steps_log.append(pd.DataFrame({"Distance to Ideal": dist_to_ideal, "Distance to Negative Ideal": dist_to_negative}, index=alternatives).round(4).rename_axis("Distances"))

    # Step 5: TOPSIS score
    scores = dist_to_negative / (dist_to_ideal + dist_to_negative)

    # Step 6: Ranking
    df_results = pd.DataFrame({"Alternative": alternatives, "TOPSIS Score": scores})
    df_results["Rank"] = df_results["TOPSIS Score"].rank(ascending=False, method="min")
    df_results.sort_values("TOPSIS Score", ascending=False, inplace=True)

    st.header("Results")
    st.dataframe(df_results.set_index("Alternative"))

    csv = df_results.to_csv(index=False).encode('utf-8')
    st.download_button("Download Results as CSV", csv, "topsis_results.csv", "text/csv")

    # Combine all steps into one CSV-like format for download
    with io.StringIO() as calc_io:
        for step_df in steps_log:
            step_df.to_csv(calc_io)
            calc_io.write("\n")
        calc_content = calc_io.getvalue().encode("utf-8")

    st.download_button("📥 Download Detailed Calculations", calc_content, "topsis_calculation_steps.csv", "text/csv")
