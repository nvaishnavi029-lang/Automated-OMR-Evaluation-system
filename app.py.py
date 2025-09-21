import streamlit as st
import cv2
import numpy as np
from PIL import Image
import pandas as pd
import os

# ------------------------------
# Subjects and Answer Keys
# ------------------------------
subjects = ["PYTHON", "DATA ANALYSIS", "MySQL", "POWER BI", "Adv STATS"]

answer_keys = {
    "A": {subj:[1]*20 for subj in subjects},
    "B": {subj:[0]*20 for subj in subjects},
    "C": {subj:[1,0]*10 for subj in subjects},
    "D": {subj:[0,1]*10 for subj in subjects}
}

# ------------------------------
# Storage setup
# ------------------------------
OUT_DIR = "omr_results"
os.makedirs(OUT_DIR, exist_ok=True)
results_file = os.path.join(OUT_DIR, "evaluation_results.csv")
if not os.path.exists(results_file):
    df_init = pd.DataFrame(columns=["Student","Set"] + subjects + ["Total"])
    df_init.to_csv(results_file, index=False)

# ------------------------------
# Bubble Detection Function (Improved)
# ------------------------------
def detect_bubbles(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    thresh = cv2.threshold(blur, 150, 255, cv2.THRESH_BINARY_INV)[1]
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    bubbles = []
    for c in contours:
        (x, y, w, h) = cv2.boundingRect(c)
        area = cv2.contourArea(c)
        perimeter = cv2.arcLength(c, True)
        if perimeter == 0:
            continue
        aspect_ratio = w / float(h)
        circularity = 4 * np.pi * area / (perimeter * perimeter)

        # Filtering: roughly square, reasonable size, close to circular
        if 0.8 < aspect_ratio < 1.2 and 200 < area < 2000 and 0.7 < circularity < 1.2:
            bubbles.append((x, y, w, h))

    bubbles = sorted(bubbles, key=lambda b: (b[1], b[0]))
    return bubbles, thresh

# ------------------------------
# Extract Student Answers
# ------------------------------
def extract_answers(image):
    bubbles, thresh = detect_bubbles(image)
    answers = []
    for (x, y, w, h) in bubbles:
        roi = thresh[y:y+h, x:x+w]
        filled = cv2.countNonZero(roi) / (w*h) > 0.5
        answers.append(int(filled))
    if len(answers) < 100:
        answers += [0]*(100 - len(answers))
    else:
        answers = answers[:100]
    return answers

# ------------------------------
# Save Results Function
# ------------------------------
def save_results(student_name, selected_set, scores, total_score):
    os.makedirs(OUT_DIR, exist_ok=True)
    if not os.path.exists(results_file):
        df_init = pd.DataFrame(columns=["Student","Set"] + subjects + ["Total"])
        df_init.to_csv(results_file, index=False)
    df = pd.read_csv(results_file)
    df_new = pd.DataFrame([{
        "Student": student_name,
        "Set": selected_set,
        **{subj: int(scores[subj]) for subj in subjects},
        "Total": int(total_score)
    }])
    df = pd.concat([df, df_new], ignore_index=True)
    df.to_csv(results_file, index=False)
    return len(df)

# ------------------------------
# Streamlit App
# ------------------------------
st.title("📄 Automated OMR Evaluation System")

student_name = st.text_input("Enter Student Name")
uploaded_file = st.file_uploader("Upload OMR Sheet Image", type=["jpg","jpeg","png"])
selected_set = st.selectbox("Select OMR Set", ["A","B","C","D"])

if uploaded_file is not None and student_name:
    image = np.array(Image.open(uploaded_file))
    st.image(image, caption="Uploaded OMR Sheet", use_column_width=True)

    # Extract answers
    student_answers = extract_answers(image)

    # Split into subjects
    student_subject_answers = {subjects[i]: student_answers[i*20:(i+1)*20] for i in range(5)}

    # Evaluate
    answer_key = answer_keys[selected_set]
    scores = {}
    for subj in subjects:
        correct = answer_key[subj]
        given   = student_subject_answers[subj]
        score   = sum([1 for c,g in zip(correct,given) if c==g])
        scores[subj] = score
    total_score = sum(scores.values())

    # Display Results
    st.subheader("📊 Subject-wise Scores")
    for subj in subjects:
        st.write(f"{subj}: {scores[subj]} / 20")
    st.success(f"✅ Total Score: {total_score} / 100")

    # Save results
    if st.button("Save Result to CSV"):
        total_entries = save_results(student_name, selected_set, scores, total_score)
        st.success(f"✅ Results saved! Total entries: {total_entries}")

# ------------------------------
# Evaluator Dashboard
# ------------------------------
st.sidebar.subheader("📊 Evaluator Dashboard")
if st.sidebar.button("Show Dashboard"):
    if os.path.exists(results_file):
        df = pd.read_csv(results_file)

        # Convert numeric columns to int
        for subj in subjects + ["Total"]:
            df[subj] = pd.to_numeric(df[subj], errors='coerce')

        # All student results
        st.subheader("All Student Results")
        st.dataframe(df)

        # Per student scores
        st.subheader("📌 Per Student Scores")
        st.dataframe(df[["Student", "Total"]])

        # Per subject statistics
        st.subheader("📚 Per Subject Statistics")
        subject_stats = df[subjects].agg(["mean", "max", "min", "std"]).T
        subject_stats.rename(columns={
            "mean": "Average",
            "max": "Max",
            "min": "Min",
            "std": "Std Dev"
        }, inplace=True)
        st.dataframe(subject_stats)

        # Aggregate statistics
        st.subheader("📈 Aggregate Statistics")
        overall_stats = {
            "Total Students": len(df),
            "Average Total Score": df["Total"].mean(),
            "Highest Total Score": df["Total"].max(),
            "Lowest Total Score": df["Total"].min(),
        }
        st.json(overall_stats)

    else:
        st.warning("No results yet.")
