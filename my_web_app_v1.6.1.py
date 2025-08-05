import streamlit as st
st.warning("⚠️ This app works best on desktop or iOS 13+ (newer Safari/Chrome).")
import pandas as pd
import numpy as np

st.set_page_config(page_title="Car Comparison App", layout="wide")

st.title("🚗 Car Comparison App")

st.markdown("""
### 🎯 Aim and Performance of this App
This **Car Comparison App** helps users make informed decisions by comparing multiple cars based on different criteria 
such as price, fuel efficiency, safety, etc. It uses the **TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution)** method 
to rank cars objectively based on the provided data. The app normalizes, weights, and analyzes input to identify the car that best fits your desire.
""")

# Step 1: Enter Cars
st.header("Step 1: Enter Car Alternatives")

st.markdown("""
#### ℹ️ What are Car Alternatives?
In this step, you will enter the names of the cars you are considering. For example: "Toyota Corolla", "Mazda 3", "Hyundai i30". 
These are the **alternatives** that will be compared using your chosen criteria.
""")

num_cars = st.number_input("How many cars do you want to compare?", min_value=2, step=1)
car_names = []
for i in range(num_cars):
    car = st.text_input(f"Name of Car #{i+1}", key=f"car_{i}")
    car_names.append(car)

# Step 2: Enter Evaluation Criteria
st.header("Step 2: Enter Evaluation Criteria")

st.markdown("""
#### ℹ️ What are Criteria?
Criteria are the features based on which you want to compare cars. Examples include:
- **Price** (Cost)
- **Fuel Efficiency** (Benefit)
- **Safety Rating** (Benefit)
- **Maintenance Cost** (Cost)

For numeric criteria such as price just use those numbers (e.g. 15000 dollars for price).
For other criteria such as car look, simply generate your numeric systme (e.g. on a scale of 0-5, assign value 5 for most good-looking car).

✅ *Type* indicates whether lower values are better (**Cost**) or higher values are better (**Benefit**).

⚖️ Please assign **weights** to each criterion — values between 0 and 1 — representing their importance. The total of all weights **must not exceed 1**.
""")

num_criteria = st.number_input("How many criteria do you want to use?", min_value=2, step=1)
criteria_data = []
for i in range(num_criteria):
    col1, col2, col3 = st.columns([3, 2, 2])
    with col1:
        name = st.text_input(f"Criterion #{i+1} Name", key=f"criterion_name_{i}")
    with col2:
        ctype = st.selectbox(f"Type", ["Cost", "Benefit"], key=f"criterion_type_{i}")
    with col3:
        weight = st.number_input(f"Weight", min_value=0.0, step=0.1, key=f"criterion_weight_{i}")
    criteria_data.append({"name": name, "type": ctype, "weight": weight})

# This is the new code block for weight validation in Step 2
weights = [c['weight'] for c in criteria_data if c['weight'] is not None]
if weights:
    total_weight = sum(weights)
    if total_weight > 1.0:
        st.error("❌ The total weight exceeds 1. Please adjust the weights so they sum to 1 or less.")
    elif total_weight < 1.0:
        st.warning("⚠️ The total weight is less than 1. Results may be biased.")
    else:
        st.success("✅ The total weight is exactly 1.0. Analysis is ready to run.")

# Step 3: Editable Matrix
st.header("Step 3: Fill the Evaluation Table")
if car_names and criteria_data and all(c["name"] for c in criteria_data):
    matrix_data = pd.DataFrame(index=[c["name"] for c in criteria_data], columns=car_names)
    matrix_data = st.data_editor(matrix_data, num_rows="dynamic", use_container_width=True, key="score_table")

# Step 4: Run Analysis
st.header("Step 4: Run Analysis")
if st.button("Run Analysis"):
    # Validate input
    if matrix_data.isnull().values.any():
        st.error("Please fill in all the cells in the table.")
    else:
        # Prepare data
        decision_matrix = matrix_data.astype(float).values
        # Transpose the matrix so alternatives (cars) are rows and criteria are columns
        decision_matrix = decision_matrix.T

        weights = np.array([c["weight"] for c in criteria_data])

        # Normalize the decision matrix
        norm_matrix = decision_matrix / np.sqrt((decision_matrix ** 2).sum(axis=0))

        # Apply weights
        weighted_matrix = norm_matrix * weights

        # Identify ideal and anti-ideal values for each criterion
        num_criteria = len(criteria_data)
        ideal = np.zeros(num_criteria)
        anti_ideal = np.zeros(num_criteria)
        for i in range(num_criteria):
            if criteria_data[i]['type'] == 'Benefit':
                ideal[i] = np.max(weighted_matrix[:, i])
                anti_ideal[i] = np.min(weighted_matrix[:, i])
            else:  # 'Cost'
                ideal[i] = np.min(weighted_matrix[:, i])
                anti_ideal[i] = np.max(weighted_matrix[:, i])

        # Calculate distances to ideal and anti-ideal solutions
        d_pos = np.sqrt(((weighted_matrix - ideal) ** 2).sum(axis=1))
        d_neg = np.sqrt(((weighted_matrix - anti_ideal) ** 2).sum(axis=1))

        # Calculate TOPSIS scores
        scores = d_neg / (d_pos + d_neg)

        # Bar chart of TOPSIS scores
        st.subheader("📊 TOPSIS Scores Bar Chart")
        score_df = pd.DataFrame({ "Car": car_names, "Score": scores })
        st.bar_chart(score_df.set_index("Car"))

        best_car = car_names[np.argmax(scores)]
        st.markdown(f"**✅ The best car based on TOPSIS analysis is: {best_car}**")

        result_df = pd.DataFrame({
            "Car": car_names,
            "TOPSIS Score": scores,
            "Rank": scores.argsort()[::-1].argsort() + 1
        }).sort_values("Rank")

        st.success("Analysis complete!")
        st.dataframe(result_df, use_container_width=True)

        # Allow download of results
        eval_results = pd.DataFrame(decision_matrix, columns=[c["name"] for c in criteria_data])
        eval_results.insert(0, "Car", car_names)
        eval_results["Score"] = scores
        
        # Corrected line to calculate ranks properly
        eval_results["Rank"] = scores.argsort()[::-1].argsort() + 1

        # Sort the DataFrame by rank before converting to CSV
        eval_results = eval_results.sort_values("Rank")

        csv = eval_results.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download Evaluation Results as CSV", data=csv, file_name="car_comparison_results.csv", mime="text/csv")
