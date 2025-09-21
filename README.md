# 📄 Automated OMR Evaluation System

## Problem Statement
Evaluating OMR sheets manually is time-consuming and error-prone. This project automates OMR evaluation using Python and Streamlit.

## Approach
1. Detect bubbles in OMR sheet images using OpenCV.
2. Extract student answers from detected bubbles.
3. Compare answers with predefined answer keys.
4. Calculate subject-wise and total scores.
5. Display results in Streamlit.
6. Save results in a CSV file for record keeping.
7. Evaluator Dashboard for statistics and all student results.

## Installation
1. Clone the repository:
   ```bash
   https://github.com/<nvaishnavi029-lang>/OMR-Automation.git

## Usage
1. Open the Streamlit app:
   ```bash
   streamlit run app.py.py

## Folder Structure
OMR-Automation/
│
├── app.py.py             # Main Streamlit app
├── requirements.txt      # Python libraries
├── omr_results/          # Folder where CSV results are saved
└── README.md             # Project description

## License
This project is for hackathon purposes only.






