# 🚗 Car Comparison App using TOPSIS

This is a simple and interactive web application that helps users compare different car options based on multiple criteria using the **TOPSIS** (Technique for Order Preference by Similarity to Ideal Solution) decision-making method.

Built with [Streamlit](https://streamlit.io), this app allows you to:

- Define custom criteria such as **price**, **fuel efficiency**, **safety rating**, etc.
- Mark each criterion as a **Benefit** (higher is better) or **Cost** (lower is better)
- Assign weights to each criterion (they must add up to 1.0)
- Input the values for each alternative (car)
- Compute a final score for each alternative using TOPSIS
- Download a detailed Excel report of the entire decision-making process

## 🔧 How to Use the App

1. Open the app using the Streamlit Cloud link: https://car-comparison-app.streamlit.app
2. Click on + or - to determine the number of criteria and alternatives
3. Fill in:
   - Criterion names
   - Whether each is a Benefit or Cost
   - Weight for each criterion
4. Enter data for all alternatives (e.g., cars)
5. Click **"Run Analysis"** to compute scores and rankings
6. Optionally download the calculation steps as an Excel file

## 📦 Requirements

The app uses the following Python libraries:

```
streamlit
pandas
numpy
```

Install them using:

```bash
pip install -r requirements.txt
```

## 🚀 Deployment

This app has been deployed on [Streamlit Cloud](https://streamlit.io/cloud) for free.


## 📄 License

This project is open-source and free to use under the MIT License.

---

Made with ❤️ by [Davoudimj@gmail.com]
