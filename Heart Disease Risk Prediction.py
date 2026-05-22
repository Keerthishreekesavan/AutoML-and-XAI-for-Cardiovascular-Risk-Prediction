# streamlit_heart_dashboard.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import h2o
from fpdf import FPDF
import os

st.set_page_config(page_title="Heart Disease Dashboard", layout="wide")

# ========== INIT H2O & MODEL ==========
h2o.init()
try:
    model_path = "GBM_2_AutoML_1_20250624_202543"
    h2o_model = h2o.load_model(model_path)
except Exception as e:
    st.error(f"❌ Model load failed: {e}")
    st.stop()

# ========== CUSTOM STYLES ==========
st.markdown("""
    <style>
        .main-card {
            background: linear-gradient(135deg, #f8cdda, #1d2b64);
            border-radius: 15px;
            padding: 25px;
            color: white;
            margin-bottom: 20px;
            box-shadow: 0 4px 30px rgba(0,0,0,0.2);
        }
        .metric-box {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 15px;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    .fade-in-alert {
        animation: fadeIn 1.2s ease-in-out;
    }
    @keyframes fadeIn {
        from {opacity: 0; transform: translateY(-6px);}
        to {opacity: 1; transform: translateY(0);}
    }
    .custom-alert {
        padding: 16px 24px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.15);
        font-size: 15px;
        font-weight: 500;
        margin: 20px auto 20px auto;
        width: 80%;
        text-align: center;
    }
    .alert-success {
        background-color: #e6f5f0;
        color: #1a3d32;
        border-left: 5px solid #46b18b;
    }
    .alert-danger {
        background-color: #fcebea;
        color: #571818;
        border-left: 5px solid #e66c6c;
    }
    </style>
""", unsafe_allow_html=True)

# === DASHBOARD HEADING ===
st.markdown("""
<div class='main-card'>
    <h1 style='text-align: center;'>❤️ Heart Disease Risk Prediction Dashboard</h1>
</div>
""", unsafe_allow_html=True)

# ========== SIDEBAR USER INPUT ==========
with st.sidebar:
    st.header("📋 Input Your Health Data")
    age = st.slider("Age", 18, 100, 30)
    gender = st.radio("Gender", ['Male', 'Female'], horizontal=True)
    height = st.slider("Height (cm)", 100, 250, 170)
    weight = st.slider("Weight (kg)", 30, 200, 70)
    ap_hi = st.number_input("Systolic BP", 80, 250, 120)
    ap_lo = st.number_input("Diastolic BP", 40, 150, 80)
    cholesterol = st.selectbox("Cholesterol", [1, 2, 3], format_func=lambda x: ["Normal", "Above Normal", "Well Above Normal"][x - 1])
    gluc = st.selectbox("Glucose", [1, 2, 3], format_func=lambda x: ["Normal", "Above Normal", "Well Above Normal"][x - 1])
    smoke = st.radio("Do you smoke?", [0, 1], format_func=lambda x: "Yes" if x else "No", horizontal=True)
    alco = st.radio("Alcohol Intake?", [0, 1], format_func=lambda x: "Yes" if x else "No", horizontal=True)
    active = st.radio("Physically Active?", [0, 1], format_func=lambda x: "Yes" if x else "No", horizontal=True)
    submitted = st.button("🔍 Predict")

# ========== PREDICT + VISUALS ==========
if submitted:
    bmi = round(weight / ((height / 100) ** 2), 2)
    input_dict = {
        'age': age,
        'gender': 1 if gender == 'Male' else 0,
        'height': height,
        'weight': weight,
        'ap_hi': ap_hi,
        'ap_lo': ap_lo,
        'cholesterol': cholesterol,
        'gluc': gluc,
        'smoke': smoke,
        'alco': alco,
        'active': active,
        'BMI': bmi
    }

    thresholds = {
        "Age": 55, "Systolic BP": 140, "Diastolic BP": 90,
        "BMI": 25, "Cholesterol": 2, "Glucose": 2
    }

    values = {
        "Age": age, "Systolic BP": ap_hi, "Diastolic BP": ap_lo,
        "BMI": bmi, "Cholesterol": cholesterol, "Glucose": gluc
    }

    risky = sum(values[k] > thresholds[k] for k in values)
    safe = len(values) - risky

    cholesterol_label = {1: "🟢 Normal", 2: "🟠 Above Normal", 3: "🔴 Well Above Normal"}[cholesterol]
    glucose_label = {1: "🟢 Normal", 2: "🟠 Above Normal", 3: "🔴 Well Above Normal"}[gluc]

    input_df = pd.DataFrame([input_dict])
    h2o_input = h2o.H2OFrame(input_df)
    result = h2o_model.predict(h2o_input).as_data_frame()
    prediction = int(result["predict"][0])
    prediction_label = "🔴 High Risk" if prediction == 1 else "🟢 Low Risk"

    # ========== METRICS ==========
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.markdown(f"""
    <div class='metric-box'><h4>BMI</h4><h2>{bmi}</h2>
    <p style='color:{'red' if bmi > 25 else 'lightgreen'};'>{'⚠ Risky' if bmi > 25 else '✔ Healthy'}</p></div>""", unsafe_allow_html=True)

    col2.markdown(f"""
    <div class='metric-box'><h4>BP</h4><h2>{ap_hi}/{ap_lo}</h2>
    <p style='color:{'red' if ap_hi > 140 or ap_lo > 90 else 'lightgreen'};'>{'🔺 Risky' if ap_hi > 140 or ap_lo > 90 else '✔ Safe'}</p></div>""", unsafe_allow_html=True)

    col3.markdown(f"""
    <div class='metric-box'><h4>Risk Score</h4><h2>{risky} / {len(values)}</h2>
    <p style='color:{'red' if risky > 2 else 'lightgreen'};'>{prediction_label}</p></div>""", unsafe_allow_html=True)

    col4.markdown(f"""
    <div class='metric-box'><h4>Cholesterol</h4><h2>{cholesterol_label.split()[0]}</h2><p>{cholesterol_label}</p></div>""", unsafe_allow_html=True)

    col5.markdown(f"""
    <div class='metric-box'><h4>Glucose</h4><h2>{glucose_label.split()[0]}</h2><p>{glucose_label}</p></div>""", unsafe_allow_html=True)

    # prediction: 1 = High Risk, 0 = Low Risk
    if prediction == 1:
        st.markdown(
            """
            <div class="custom-alert fade-in-alert alert-danger">
                ⚠️ <strong>High risk of heart disease detected.</strong> Please consult a healthcare professional.
            </div>
            """, unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div class="custom-alert fade-in-alert alert-success">
                ✅ <strong>No heart disease detected.</strong> Keep up the healthy lifestyle!
            </div>
            """, unsafe_allow_html=True
        )

    # ========== CHARTS ==========
    st.markdown("""
        <h3 style='color:#FFADAD; font-weight:600;'> Prediction Overview </h3>
        """, unsafe_allow_html=True)

    col6, col7 = st.columns(2)
    with col6:
        st.markdown("#### 📈 Measured Values vs Safe Limits")
        df_plot = pd.DataFrame(values, index=["Your Value"]).T
        df_plot["Threshold"] = thresholds.values()
        fig1, ax1 = plt.subplots(figsize=(4.5, 3))
        df_plot.plot(kind='bar', ax=ax1)
        plt.xticks(rotation=45)
        st.pyplot(fig1)
        st.markdown(
            """
            <div style="padding: 10px; border-left: 5px solid #4FC3F7; background-color: #0f1117; border-radius: 8px; margin-top: 10px;">
                <strong>Interpretation:</strong><br>
                This chart compares your current health measurements against recommended threshold values. Bars exceeding thresholds may indicate elevated health risk.
            </div>
            """, unsafe_allow_html=True
        )

    with col7:
        st.markdown("#### 📊 Risk Breakdown")
        fig2, ax2 = plt.subplots(figsize=(3.5, 3))
        ax2.pie([safe, risky], labels=["Safe", "Risky"], autopct="%1.1f%%", colors=["green", "red"])
        st.pyplot(fig2)
        st.markdown(
            """
            <div style="padding: 10px; border-left: 5px solid #66BB6A; background-color: #0f1117; border-radius: 8px; margin-top: 10px;">
                <strong>Interpretation:</strong><br>
                This chart summarizes how many of your health indicators fall into the safe versus risky categories. Aim for a higher proportion of green to minimize heart disease risk.
            </div>
            """, unsafe_allow_html=True
        )

    # ========== SHAP + RADAR ==========
    shap_values = h2o_model.predict_contributions(h2o_input)
    shap_df = shap_values[0, :].as_data_frame().drop(columns="BiasTerm").T
    shap_df.columns = ["SHAP Value"]
    shap_df = shap_df.sort_values(by="SHAP Value")

    user_features = ['age', 'gender', 'height', 'weight', 'ap_hi', 'ap_lo', 'cholesterol', 'gluc', 'BMI']
    engineered_features = [f for f in shap_df.index if f not in user_features]

    name_map = {
        'age': 'Age', 'gender': 'Gender', 'height': 'Height', 'weight': 'Weight',
        'ap_hi': 'Systolic BP', 'ap_lo': 'Diastolic BP', 'cholesterol': 'Cholesterol',
        'gluc': 'Glucose', 'BMI': 'BMI', 'pulse_pressure': 'Pulse Pressure',
        'lifestyle_risk': 'Lifestyle Risk', 'WeightxChol': 'Weight × Chol',
        'BMixAge': 'BMI × Age', 'BP_Category_Normal': 'BP Normal',
        'BP_Category_Prehypertension': 'BP PreHTN'
    }

    def plot_radar(data, title):
        labels = data.index.map(lambda x: name_map.get(x, x)).tolist()
        values = data["SHAP Value"].values
        max_val = np.max(np.abs(values))
        norm_vals = (values + max_val) / (2 * max_val)
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        angles += angles[:1]
        norm_vals = norm_vals.tolist() + [norm_vals[0]]
        fig, ax = plt.subplots(figsize=(4.5, 3), subplot_kw=dict(polar=True))
        color = 'red' if np.sum(values) > 0 else 'green'
        ax.plot(angles, norm_vals, color=color)
        ax.fill(angles, norm_vals, color=color, alpha=0.3)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, fontsize=8)
        ax.set_yticklabels([])
        ax.set_title(title, fontsize=10)
        return fig

    st.markdown("""
    <h3 style='color:#FFADAD; font-weight:600;'>Features Contribution Overview</h3>
    """, unsafe_allow_html=True)
    
    col8, col9 = st.columns(2)
    with col8:
        st.markdown("#### 🔍 How Your Inputs Affect the Prediction")
        user_df = shap_df.loc[user_features]
        user_df.index = [name_map.get(i, i) for i in user_df.index]
        fig3, ax3 = plt.subplots(figsize=(4.5, 3))
        user_df["SHAP Value"].plot(kind="barh", ax=ax3, color=["green" if v < 0 else "red" for v in user_df["SHAP Value"]])
        st.pyplot(fig3)
        st.markdown(
            """
            <div style="padding: 10px; border-left: 5px solid #4FC3F7; background-color: #0f1117; border-radius: 8px; margin-top: 10px;">
                <strong>Interpretation:</strong><br>
                This chart shows how each of your health inputs is influencing the result. <br>
                <span style="color:red;"><strong>Red bars</strong></span> suggest higher risk, while 
                <span style="color:green;"><strong>green bars</strong></span> indicate protective effects.
            </div>
            """, unsafe_allow_html=True
        )

    with col9:
        st.markdown("#### 🌐 Visual Influence of Your Health Metrics")
        st.pyplot(plot_radar(user_df, "User Input Features"))
        st.markdown(
            """
            <div style="padding: 10px; border-left: 5px solid #66BB6A; background-color: #0f1117; border-radius: 8px; margin-top: 10px;">
                <strong>Interpretation:</strong><br>
                This radar chart gives a visual summary of your inputs. The farther a point is from the center, the more it contributes. <br>
                Aim for a balanced spread to maintain good heart health.
            </div>
            """, unsafe_allow_html=True
        )

    st.markdown("""
            <h3 style='color:#FFADAD; font-weight:600;'>Insights from Combined Health Factors</h3>
            """, unsafe_allow_html=True)
    col10, col11 = st.columns(2)
    with col10:
        st.markdown("#### 🔍 How Combined Factors Influence Your Risk")
        eng_df = shap_df.loc[engineered_features]
        eng_df.index = [name_map.get(i, i) for i in eng_df.index]
        fig5, ax5 = plt.subplots(figsize=(4.5, 3))
        eng_df["SHAP Value"].plot(kind="barh", ax=ax5, color=["green" if v < 0 else "red" for v in eng_df["SHAP Value"]])
        st.pyplot(fig5)
        st.markdown(
            """
            <div style="padding: 10px; border-left: 5px solid #FFB74D; background-color: #0f1117; border-radius: 8px; margin-top: 10px;">
                <strong>Interpretation:</strong><br>
                This chart shows how calculated health combinations like BMI × Age or Weight × Cholesterol impact your heart risk. Longer red bars suggest a greater push toward higher risk, while green ones help reduce it.
            </div>
            """, unsafe_allow_html=True
        )

    with col11:
        st.markdown("#### 🌐 Snapshot of Your Derived Health Profile")
        st.pyplot(plot_radar(eng_df, "Engineered Features"))
        st.markdown(
            """
            <div style="padding: 10px; border-left: 5px solid #81C784; background-color: #0f1117; border-radius: 8px; margin-top: 10px;">
                <strong>Interpretation:</strong><br>
                This chart provides a visual overview of your calculated health indicators. Areas closer to the center may signal better control, while stretched edges could highlight areas needing attention.
            </div>
            """, unsafe_allow_html=True
        )
        
    # Risk table
    st.markdown("#### 📋 Metric Risk Status")
    risk_df = pd.DataFrame({
        "Metric": list(values.keys()),
        "Your Value": list(values.values()),
        "Threshold": [thresholds[k] for k in values],
        "Status": ["✅ Safe" if values[k] <= thresholds[k] else "⚠️ Risky" for k in values]
    })
    st.dataframe(risk_df.style.applymap(lambda v: "color: red;" if "Risky" in str(v) else "color: green;", subset=["Status"]))

    st.download_button("📄 Download SHAP CSV", shap_values.as_data_frame().to_csv(index=False), file_name="shap_values.csv")

    from io import BytesIO
    from fpdf import FPDF

    # ==== SAFE USER INPUT DATA ====
    user_input_pretty = {
        "Age": age,
        "Gender": gender,
        "Height (cm)": height,
        "Weight (kg)": weight,
        "BMI": bmi,
        "Systolic BP": ap_hi,
        "Diastolic BP": ap_lo,
        "Cholesterol": ["Normal", "Above Normal", "Well Above Normal"][cholesterol - 1],
        "Glucose": ["Normal", "Above Normal", "Well Above Normal"][gluc - 1],
        "Smokes": "Yes" if smoke else "No",
        "Alcohol Intake": "Yes" if alco else "No",
        "Physically Active": "Yes" if active else "No"
    }

    explanation = (
        "Your health indicators suggest a higher likelihood of heart disease. "
        "Contributing factors may include elevated BMI, blood pressure, cholesterol, or glucose. "
        "It's advised to consult a healthcare provider and consider lifestyle adjustments."
        if prediction == 1 else
        "Your inputs indicate a low risk of heart disease. Maintain your current healthy practices!"
    )

    personal_advice = (
        "- Improve your diet with heart-healthy foods\n"
        "- Exercise regularly (30 mins/day)\n"
        "- Monitor blood pressure and sugar\n"
        "- Consult a doctor for tailored guidance"
        if prediction == 1 else
        "- Keep up your balanced diet\n"
        "- Stay physically active\n"
        "- Continue monitoring your health regularly"
    )

    summary_text = (
        "Higher risk detected. Prompt health interventions are recommended."
        if prediction == 1 else
        "Low risk detected. Great job on keeping your health in check!"
    )

    # ==== BUILD PDF ====
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Heart Disease Prediction Report", ln=True, align='C')

    pdf.set_font("Arial", '', 12)
    pdf.ln(10)
    pdf.multi_cell(0, 10,
                   "Overview:\nThis report summarizes your health inputs, prediction outcome, and personalized advice based on your current health profile.")

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "User Inputs:", ln=True)

    pdf.set_font("Arial", '', 12)
    for k, v in user_input_pretty.items():
        pdf.cell(0, 8, f"{k}: {v}", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Prediction Result:", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, f"Prediction: {'High Risk' if prediction == 1 else 'Low Risk'}\n\n{explanation}")

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Personal Advice:", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, personal_advice)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Summary:", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, summary_text)

    # === Convert to BytesIO for download ===
    pdf_bytes = BytesIO(pdf.output(dest='S').encode('latin1'))

    st.download_button(
        label="Download Full Report (PDF)",
        data=pdf_bytes,
        file_name="Heart_Report.pdf",
        mime="application/pdf"
    )

    st.markdown("""
    <style>
    .footer {
        width: 100%;
        text-align: center;
        padding: 10px;
        margin-top: 40px;

        background-color: var(--background-color);
        border-top: 1px solid rgba(255,255,255,0.1);
        color: var(--text-color);
    }

    .footer a {
        color: #4FC3F7;
        text-decoration: none;
        font-weight: 600;
    }
    </style>

    <div class="footer">
        <b>Keerthishree Kesavan 🌷</b> |
        AI/ML Focused Full Stack Developer |
        <a href="https://github.com/Keerthishreekesavan" target="_blank">
            View GitHub
        </a>
    </div>
    """, unsafe_allow_html=True)