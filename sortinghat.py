import streamlit as st
import pandas as pd
import altair as alt
from collections import Counter
import random
from datetime import datetime
import os
import difflib
import time

# --- Constants ---
HOUSES = ["Gryffindor", "Slytherin", "Ravenclaw", "Hufflepuff"]

QUESTIONS = [
    {
        "q": "You were in the library and accidentally skipped lunch. What do you do?",
        "opts": [
            ("Try something new from the tuck shop that you've never had before",
             {"Gryffindor": 3, "Ravenclaw": 1}),
            ("Eat the packet of chips your roommates has kept on their desk for the past 3 weeks",
             {"Slytherin": 3, "Gryffindor": 1}),
            ("Skip it and stay hungry till snack time",
             {"Hufflepuff": 3, "Slytherin": 1, "Ravenclaw": -2}),
        ],
    },
    {
        "q": "While working in a group setting for ILGC, what position are you most likely to take?",
        "opts": [
            ("The leader - The one frantically trying to structure your answer so it's optimised, "
             "demanding answers and new insights, making sure every member of your team is participating.",
             {"Gryffindor": 3, "Slytherin": 2}),
            ("The mediator - The one balancing and dialing back wild ideas that your team members present "
             "without hurting their feelings",
             {"Hufflepuff": 3, "Slytherin": -2}),
            ("The realist - The one who keeps reminding others of the 'economic feasibility' of a solution",
             {"Slytherin": 2, "Ravenclaw": 1}),
            ("The dreamer - The one who truly believes if an idea is good enough the funds will follow",
             {"Hufflepuff": 3, "Slytherin": 1, "Ravenclaw": -2}),
            ("The chill guy - The one who's just there to get a passing grade",
             {"Gryffindor": 2, "Hufflepuff": 2, "Ravenclaw": -3}),
        ],
    },
    # --- Add the remaining questions here in the same format ---
]

# --- Functions ---
def score_answers(selected_options):
    scores = Counter()
    for option in selected_options:
        for house, pts in option.items():
            scores[house] += pts
    return scores


def determine_house(counts):
    if not counts:
        return None, []
    max_points = max(counts.values())
    top = [h for h, v in counts.items() if v == max_points]
    if len(top) == 1:
        return top[0], top
    return random.choice(top), top


def is_name_similar(new_name, past_names, threshold=0.8):
    for past_name in past_names:
        similarity = difflib.SequenceMatcher(None, new_name.lower(), past_name.lower()).ratio()
        if similarity >= threshold:
            return True
    return False


# --- Streamlit App ---
st.set_page_config(page_title="Sorting Hat LMAO", page_icon="🧙‍♂️")

# Global background
st.markdown("""
<style>
.stApp { background-color: #CD5C5C; }
</style>
""", unsafe_allow_html=True)

# Title banner
st.markdown("""
<div style="
    background: linear-gradient(135deg, #f8f4e5, #e8e0c4);
    border: 3px solid #5a4633;
    border-radius: 20px;
    padding: 20px;
    margin-bottom: 30px;
    text-align: center;
    box-shadow: 6px 6px 12px rgba(0,0,0,0.25);
">
    <h1 style="color:#3e2723; font-family: 'Georgia';">SORTING HAT</h1>
</div>
""", unsafe_allow_html=True)

# Load past results
try:
    results_df = pd.read_csv("results.csv")
except FileNotFoundError:
    results_df = pd.DataFrame(columns=["name", "house", "timestamp"])

# Name input
st.markdown("""
<div style="
    background: linear-gradient(135deg, #f8f4e5, #e8e0c4);
    border: 2px solid #5a4633;
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 4px 4px 10px rgba(0,0,0,0.2);
">
    <h3 style="color:#3e2723; font-family: 'Georgia';">What is your name?</h3>
</div>
""", unsafe_allow_html=True)

name = st.text_input("", key="name_input").strip()

if name:
    st.write(f"Hello {name}! Answer the following questions to find out your Hogwarts house.")
    answers = []

    for i, q in enumerate(QUESTIONS, 1):
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #f8f4e5, #e8e0c4);
            border: 2px solid #5a4633;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 10px;
            box-shadow: 4px 4px 10px rgba(0,0,0,0.2);
        ">
            <h3 style="color:#3e2723; font-family: 'Georgia';">Q{i}. {q['q']}</h3>
        </div>
        """, unsafe_allow_html=True)

        choice = st.radio(
            "Choose one:",
            [opt[0] for opt in q["opts"]],
            key=f"q{i}",
            index=None
        )

        if choice:
            for text, score_dict in q["opts"]:
                if text == choice:
                    answers.append(score_dict)
        st.write("---")

    # Styled button
    st.markdown("""
    <style>
    div.stButton > button {
        background: linear-gradient(135deg, #e8e0c4, #f8f4e5);
        color: #3e2723;
        border: 2px solid #5a4633;
        border-radius: 12px;
        padding: 10px 20px;
        font-size: 18px;
        font-family: Georgia, serif;
        box-shadow: 3px 3px 6px rgba(0,0,0,0.2);
    }
    div.stButton > button:hover {
        background: #d7ccb0;
        color: black;
    }
    </style>
    """, unsafe_allow_html=True)

    if st.button("Reveal My House"):
        if len(answers) != len(QUESTIONS):
            st.warning("Please answer all questions before revealing your house!")
        else:
            if name in results_df['name'].values or is_name_similar(name, results_df['name'].values):
                st.warning("it's almost like you already knew the questions...")
                st.image("sansnoeyes.png", caption="you can't understand how this feels.")

            with st.spinner('The Sorting Hat is deciding...'):
                time.sleep(2)

            counts = score_answers(answers)
            house, tied = determine_house(counts)

            st.balloons()

            # Results card
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #f8f4e5, #e8e0c4);
                border: 3px solid #5a4633;
                border-radius: 20px;
                padding: 20px;
                margin-top: 30px;
                box-shadow: 6px 6px 12px rgba(0,0,0,0.25);
                text-align: center;
            ">
                <h2 style="color:#3e2723; font-family: 'Georgia';">{name}, you have been assigned to...</h2>
                <h1 style="color:#3e2723; font-family: 'Georgia';">{house}!</h1>
            </div>
            """, unsafe_allow_html=True)

            # Save result
            result = {"name": name, "house": house, "timestamp": datetime.now()}
            df_result = pd.DataFrame([result])
            results_df = pd.concat([results_df, df_result], ignore_index=True)
            results_df.to_csv("results.csv", index=False)

# Password-protected past results
st.write("---")
if st.checkbox("Show past results"):
    password_input = st.text_input(
        "Do you really think you can comprehend this knowledge? Then enter the magic word...",
        type="password"
    )
    try:
        correct_password = st.secrets["passwords"]["admin"]
    except KeyError:
        st.error("The admin password is not configured. Please add it to your secrets.toml file.")
        st.stop()

    if password_input == correct_password:
        try:
            df_admin = pd.read_csv("results.csv")
            st.dataframe(df_admin)
            st.write("---")
        except FileNotFoundError:
            st.warning("No past results found yet.")

        if st.button("Reset All Results"):
            try:
                os.remove("results.csv")
                st.success("Results file has been reset.")
                st.rerun()
            except FileNotFoundError:
                st.info("No results file to reset.")
