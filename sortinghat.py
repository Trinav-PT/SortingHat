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
    {
        "q": "While working in a group setting for ILGC, what position are you most likely to take?",
        "opts": [
            ("The leader - The one frantically trying to structure your answer so it's optimised, demanding answers and new insights, making sure every member of your team is participating.", {"Gryffindor": 3, "Slytherin": 2}),
            ("The mediator - The one balancing and dialing back wild ideas that your team members present without hurting their feelings", {"Hufflepuff": 3, "Slytherin": -2}),
            ("The realist - The one who keeps reminding others of the 'economic feasibility' of a solution", {"Slytherin": 2, "Ravenclaw": 1}),
            ("The dreamer - The one who truly believes if an idea is good enough the funds will follow", {"Hufflepuff": 3, "Slytherin": 1, "Ravenclaw": -2}),
            ("The chill guy - The one who's just there to get a passing grade", {"Gryffindor": 2, "Hufflepuff": 2, "Ravenclaw": -3}),
        ],
    },
    {
        "q": "You've just received an angry Kannan sir complaint letter in the middle of the Great Hall during breakfast. What is your immediate reaction?",
        "opts": [
            ("The Unfazed - You open it quickly to get it over with, shrugging off the embarrassment. You'll deal with the sender later; for now, you have a Potions essay to think about.", {"Ravenclaw": 3, "Slytherin": 1}),
            ("The Confrontationalist - You flush red with anger and embarrassment, already planning your equally loud and public retaliation against whoever sent it.", {"Gryffindor": 3, "Slytherin": 2, "Hufflepuff": -2}),
            ("The Peacemaker - You are mortified, not just for yourself, but for disrupting everyone's breakfast. You try to silence it quickly and apologise to those around you.", {"Hufflepuff": 3, "Slytherin": -2}),
            ("The Performer - You let it scream, finding the situation grimly amusing. You might even bow ironically when it's done, turning the humiliation into a moment of dark comedy.", {"Slytherin": 2, "Gryffindor": 1, "Hufflepuff": -3}),
        ],
    },
    {
        "q": "Professor Snape accuses you of cheating on a perfect exam paper, simply because he believes you're not clever enough to have written it. How do you respond?",
        "opts": [
            ("The Advocate - You calmly and logically defend your work, referencing the exact pages in Magical Drafts and Potions that support your answers, determined to prove your competence through pure reason.", {"Ravenclaw": 3, "Hufflepuff": 1}),
            ("The Defiant - You argue back passionately, insisting on your innocence and calling out the injustice of the accusation in front of the whole class. It's the principle of the matter.", {"Gryffindor": 3, "Slytherin": -2}),
            ("The Strategist - You say nothing in class but later seek out Professor McGonagall or your Head of House, presenting your case to a higher, fairer authority to overturn the verdict.", {"Slytherin": 3, "Ravenclaw": 1}),
            ("The Conciliator - You don't argue, as it would only make things worse. You simply accept the unfair accusation, hoping your consistent hard work will eventually prove him wrong.", {"Hufflepuff": 3, "Gryffindor": -3}),
        ],
    },
    {
        "q": "You stumble upon the Room of Requirement. What does it become for you?",
        "opts": [
            ("A Dueling Club - A fully equipped room with training dummies and padded floors, perfect for secretly mastering advanced defensive—and offensive—spells with your friends.", {"Gryffindor": 3, "Slytherin": 2}),
            ("A Library of Lost Knowledge - A quiet, towering library filled with rare and forbidden texts that even the Restricted Section doesn't have.", {"Ravenclaw": 3, "Slytherin": 1}),
            ("A Secret Common Room - A cozy, comfortable lounge with plush armchairs, a crackling fire, and an endless supply of snacks, where you and your friends from all houses can relax without judgment.", {"Hufflepuff": 3, "Gryffindor": 1}),
            ("A Personalised Workshop - A sophisticated potions lab or a quiet study with a direct view of the Black Lake, perfectly tailored to help you achieve your ambitions and get ahead of the competition.", {"Slytherin": 3, "Hufflepuff": -2}),
        ],
    },
    {
        "q": "You find a lost wallet next to Bharti Block. What do you do?",
        "opts": [
            ("Put it on the bulletin immediately, someone clearly needs it back.", {"Hufflepuff": 3, "Gryffindor": 1}),
            ("Leave it where it is, the person will maybe return.", {"Ravenclaw": 2, "Hufflepuff": 1}),
            ("Pocket it temporarily while trying to figure out who it belongs to.", {"Slytherin": 3, "Ravenclaw": 1}),
        ],
    },
    {
        "q": "You’re sitting with your friends and one seems particularly down and you’re the only one who has noticed. What do you do?",
        "opts": [
            ("Say nothing and try to figure out what might have happened.", {"Ravenclaw": 2, "Slytherin": 1}),
            ("Try to lighten their mood by making a joke you know they would appreciate.", {"Gryffindor": 2, "Ravenclaw": 1}),
            ("Look for small ways to help, maybe offer to carry something for them, grab them something from tuck, or do something that eases their day.", {"Ravenclaw": 2, "Hufflepuff": 1}),
            ("Give them space but approach them later and ask about what happened, letting them know you care.", {"Hufflepuff": 3}),
        ],
    },
    {
        "q": "You’re at a casual campus party, and you don’t know many people there. The room is buzzing with conversation, music, and laughter. You’re trying to figure out how to spend your time. What do you do?",
        "opts": [
            ("Hang back for a bit, observe how everyone’s interacting, and join the conversations that genuinely interest you.", {"Ravenclaw": 3, "Slytherin": 1}),
            ("Float around quietly, observing the room, noticing dynamics, and deciding who to talk to.", {"Slytherin": 2, "Ravenclaw": 2}),
            ("Find a quiet spot, scroll through your phone for a bit, and join in when it feels right.", {"Hufflepuff": 2, "Ravenclaw": 2}),
            ("Make small talk with multiple groups, seeing where you can fit in and who’s worth getting to know.", {"Slytherin": 3, "Gryffindor": 1}),
            ("Introduce yourself to a few new people, and start chatting, seeing where the conversations take you.", {"Gryffindor": 3}),
            ("Join the card game going on in the corner of the room.", {"Slytherin": 2, "Gryffindor": 1}),
            ("Help someone who seems left out of the party by bringing them a drink or including them in conversation.", {"Hufflepuff": 3, "Gryffindor": 1}),
        ],
    },
    {
        "q": "Where would you most like to live?",
        "opts": [
            ("A cosy cottage by the sea, far removed from the hustle and bustle of the city", {"Ravenclaw": 2, "Slytherin": 1}),
            ("A well-kept and organised house in a prime urban neighbourhood, exactly the same as the others in the line", {"Hufflepuff": 1, "Slytherin": -3}),
            ("A lopsided home with dozens of rooms, held up by magic and filled with the laughter of a big family", {"Hufflepuff": 2, "Gryffindor": 1, "Slytherin": -2}),
            ("A large ancestral manor-house, complete with diamond-paned windows, fine teak doorframes and peacocks in the lawn", {"Ravenclaw": 1, "Slytherin": 3, "Hufflepuff": -2}),
        ],
    },
    {
        "q": "What would be the first spell you’d yell out if someone tries to hex you while you’re walking alone in a dark street at night?",
        "opts": [
            ("Wand - ejecting spell", {"Gryffindor": 1, "Ravenclaw": -2, "Slytherin": -2}),
            ("A spell that creates microscopic wounds, making the receptor bleed out", {"Ravenclaw": 2, "Slytherin": 2}),
            ("A spell that renders someone unconscious", {"Hufflepuff": 2, "Ravenclaw": 1}),
            ("I’d just teleport out of there", {"Ravenclaw": 2, "Hufflepuff": 1}),
        ],
    },
    {
        "q": "Which place in Hogwarts would you be most scared to be alone in?",
        "opts": [
            ("The forest full of fascinating but dangerous magical creatures, at night", {"Slytherin": 1, "Ravenclaw": 1}),
            ("A marble-walled underground chamber, in which a huge magical serpent with a lethal gaze was killed a few years prior", {"Hufflepuff": 1, "Slytherin": 2}),
            ("A shack separate from the main building, which villagers claim is haunted because of the howling sounds heard at night", {"Slytherin": 1, "Ravenclaw": -1}),
            ("A corridor leading to multiple rooms with traps, including a giant three-headed dog, vines that trap you and gigantic, animated chess pieces", {"Gryffindor": 1, "Slytherin": 1, "Ravenclaw": -1}),
        ],
    },
    {
        "q": "Which pet animal would you like the best?",
        "opts": [
            ("A small, round owl who loves treats and delivers letters for their owner", {"Hufflepuff": 2}),
            ("A creature with the body of a horse and the wings and head of an eagle, who allows only the most deserving to fly on it", {"Gryffindor": 2, "Ravenclaw": 1}),
            ("A magical cat that has a strong bond with its owner, directing them to advantageous situations", {"Slytherin": 2, "Gryffindor": -1, "Ravenclaw": 1}),
            ("A phoenix, most faithful to its owner, that bursts into flames at the end of its life and is re-born immediately", {"Gryffindor": 1, "Slytherin": 1, "Ravenclaw": 1}),
            ("A large dangerous, but docile, three-headed dog who falls asleep to the sound of music", {"Hufflepuff": 2, "Gryffindor": 1, "Ravenclaw": -1}),
        ],
    },
    {
        "q": "What would be your favourite magical item?",
        "opts": [
            ("A cauldron for making potions that stirs the concoction by itself", {"Gryffindor": 1, "Slytherin": 1, "Hufflepuff": 1}),
            ("The most powerful wand in existence, created by Death itself", {"Ravenclaw": 1, "Slytherin": 2}),
            ("The latest flying broom, perfect for wizarding sports", {"Gryffindor": 1, "Slytherin": 1}),
            ("A cloak that makes the wearer invisible", {"Ravenclaw": 2, "Slytherin": 2}),
            ("A magically modified car that can fly and become invisible", {"Hufflepuff": 2, "Gryffindor": 1}),
            ("A mirror that shows the viewer their deepest desire", {"Ravenclaw": 2, "Slytherin": 1}),
        ],
    },
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
        choice_text = st.radio(
            "Choose one:",
            [opt[0] for opt in q["opts"]],
            key=f"q{st.session_state.q_index}",
            index=[opt[0] for opt in q["opts"]].index(st.session_state.answers[st.session_state.q_index][0])
            if st.session_state.answers[st.session_state.q_index] is not None else None
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
        if name in results_df['name'].values:
            st.warning("it's almost like you already knew the questions...")
            st.image("sansnoeyes.png", caption="you can't understand how this feels. knowing that one day, without warning, it's all going to be reset.")

        with st.spinner('The Sorting Hat is deciding...'):
            time.sleep(2) # Simulates a thinking process

        # The answers stored in session state are a list of tuples (choice_text, score_dict)
        # We need to extract just the score dictionaries for scoring.
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
