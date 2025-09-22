import streamlit as st
import pandas as pd
import altair as alt
from collections import Counter
import random
from datetime import datetime
import os
import difflib
import time


HOUSES = ["Gryffindor", "Slytherin", "Ravenclaw", "Hufflepuff"]


QUESTIONS = [
    {
        "q": "You were in the library and accidentally skipped lunch. What do you do?",
        "opts": [
            ("Try something new from the tuck shop that you've never had before", {"Gryffindor": 3, "Ravenclaw": 1}),
            ("Eat the packet of chips your roommates has kept on their desk for the past 3 weeks", {"Slytherin": 3, "Gryffindor": 1}),
            ("Skip it and stay hungry till snack time", {"Hufflepuff": 3, "Slytherin": 1, "Ravenclaw": -2}),
        ],
    },
    # ... (rest of your QUESTIONS unchanged)
]


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
    """Checks if a new name is similar to any name in a list of past names."""
    for past_name in past_names:
        similarity = difflib.SequenceMatcher(None, new_name.lower(), past_name.lower()).ratio()
        if similarity >= threshold:
            return True
    return False


st.set_page_config(page_title="Sorting Hat LMAO", page_icon="🧙‍♂️")
st.title("🧙‍♂️ SORTING HAT")

# --- Initialize session state ---
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
if "answers" not in st.session_state:
    st.session_state.answers = [None] * len(QUESTIONS)
if "show_results" not in st.session_state:
    st.session_state.show_results = False

try:
    results_df = pd.read_csv("results.csv")
except FileNotFoundError:
    results_df = pd.DataFrame(columns=["name", "house", "timestamp"])

name = st.text_input("What is your name?").strip()

if name:
    # Check for both exact and similar name matches
    if name in results_df['name'].values or is_name_similar(name, results_df['name'].values):
        st.warning("Have you completed this test in the past?")
        st.image("doakes.webp", caption="Interesting")
    
    st.write(f"Hello {name}! Answer the following questions to find out your Hogwarts house.")
    
    # --- Display a single question at a time ---
    if not st.session_state.show_results:
        q = QUESTIONS[st.session_state.q_index]
        st.subheader(f"Q{st.session_state.q_index + 1}. {q['q']}")
        
        # Display the radio buttons for the current question
        current_answer = st.session_state.answers[st.session_state.q_index]
        options = [opt[0] for opt in q["opts"]]

        if current_answer is not None and current_answer[0] in options:
            default_index = options.index(current_answer[0])
        else:
            default_index = None

        choice_text = st.radio(
            "Choose one:",
            options,
            key=f"q{st.session_state.q_index}",
            index=default_index
        )
        
        # Find the full option dictionary from the choice
        selected_option = next((opt[1] for opt in q["opts"] if opt[0] == choice_text), None)
        st.session_state.answers[st.session_state.q_index] = (choice_text, selected_option)
        
        st.write("---")

        col1, col2 = st.columns(2)

        with col1:
            if st.session_state.q_index > 0:
                if st.button("Previous"):
                    st.session_state.q_index -= 1
                    st.rerun()

        with col2:
            # Check if all questions are answered
            all_questions_answered = all(answer is not None for answer in st.session_state.answers)
            
            if st.session_state.q_index < len(QUESTIONS) - 1:
                if st.button("Next", disabled=selected_option is None):
                    st.session_state.q_index += 1
                    st.rerun()
            else: # On the last question
                button_text = "Reveal My House"
                if not all_questions_answered:
                    button_text = "Please answer all questions to proceed!"
                
                if st.button(button_text, disabled=not all_questions_answered):
                    st.session_state.show_results = True
                    st.rerun()
    
    # --- Display results if the quiz is complete ---
    if st.session_state.show_results:
        # Check if they have taken the test before
        if name in results_df['name'].values or is_name_similar(name, results_df['name'].values):
            st.warning("it's almost like you already knew the questions...")
            st.image("sansnoeyes.png", caption="you can't understand how this feels. knowing that one day, without warning, it's all going to be reset.")

        with st.spinner('The Sorting Hat is deciding...'):
            time.sleep(2) # Simulates a thinking process

        # The answers stored in session state are a list of tuples (choice_text, score_dict)
        score_dicts = [ans[1] for ans in st.session_state.answers]
        counts = score_answers(score_dicts)
        house, tied = determine_house(counts)

        st.balloons()

        st.write(f"###  {name}, you have been assigned to...")
        st.write(f"###  {house}!")

        df_scores = pd.DataFrame({
            "House": HOUSES,
            "Score": [counts.get(h, 0) for h in HOUSES]
        })

        house_colors = {
            "Gryffindor": "#7F0909",
            "Slytherin": "#1A472A",
            "Ravenclaw": "#0E1A40",
            "Hufflepuff": "#EEE117"
        }

        base = alt.Chart(df_scores).encode(
            theta=alt.Theta("Score", stack=True)
        )

        pie = base.mark_arc(outerRadius=120).encode(
            color=alt.Color("House", scale=alt.Scale(domain=list(house_colors.keys()),
                                                     range=list(house_colors.values()))),
            order=alt.Order("Score", sort="descending"),
            tooltip=["House", "Score"]
        )

        text = base.mark_text(radius=140).encode(
            text="Score",
            order=alt.Order("Score", sort="descending"),
            color=alt.value("black")
        )

        chart = pie + text

        st.altair_chart(chart)

        st.image(f"https://raw.githubusercontent.com/your-username/hogwarts-images/main/{house.lower()}.png",
                  caption=f"{house} Crest", width=250)

        result = {"name": name, "house": house, "timestamp": datetime.now()}
        df_result = pd.DataFrame([result])

        df_result = pd.concat([results_df, df_result], ignore_index=True)
        df_result.to_csv("results.csv", index=False)

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
