import streamlit as st
import pandas as pd
import altair as alt
from collections import Counter
import random
from datetime import datetime
import os
import difflib
import time
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
import io

HOUSES = ["Gryffindor", "Slytherin", "Ravenclaw", "Hufflepuff"]

CERTIFICATE_IMAGES = {
    "Gryffindor": "gryffnd.jpeg",
    "Slytherin": "slythn.jpeg", 
    "Ravenclaw": "rvnclaw.jpeg",
    "Hufflepuff": "huffpuff.jpeg"
}
def create_certificate_pdf(name, house, certificate_image_path):
    """
    Generates a personalized house certificate as a PDF.
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    
    
    try:
        img = Image.open(certificate_image_path)
        img_width, img_height = img.size
        
        
        aspect = img_height / float(img_width)
        page_width, page_height = A4
        
        image_x = 0
        image_y = (page_height - page_width * aspect) / 2
        image_width = page_width
        
        c.drawImage(ImageReader(certificate_image_path), image_x, image_y, width=image_width, height=image_width * aspect)
        
        
        c.setFont("Helvetica-Bold", 36)
        c.setFillColorRGB(0, 0, 0) 
        
        text_width = c.stringWidth(name, "Helvetica-Bold", 36)
        text_x = (page_width - text_width) / 2
        text_y = image_y + (image_width * aspect) * 0.54 

        c.drawString(text_x, text_y, name)
        
    except FileNotFoundError:
        c.drawString(100, 700, "Error: Certificate template not found.")
    
    c.save()
    buffer.seek(0)
    return buffer
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
            ("The dreamer - The one truly believes if an idea is good enough the funds will follow", {"Hufflepuff": 3, "Slytherin": 1, "Ravenclaw": -2}),
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
        "q": "You're sitting with your friends and one seems particularly down and you're the only one who has noticed. What do you do?",
        "opts": [
            ("Say nothing and try to figure out what might have happened.", {"Ravenclaw": 2, "Slytherin": 1}),
            ("Try to lighten their mood by making a joke you know they would appreciate.", {"Gryffindor": 2, "Ravenclaw": 1}),
            ("Look for small ways to help, maybe offer to carry something for them, grab them something from tuck, or do something that eases their day.", {"Ravenclaw": 2, "Hufflepuff": 1}),
            ("Give them space but approach them later and ask about what happened, letting them know you care.", {"Hufflepuff": 3}),
        ],
    },
    {
        "q": "You're at a casual campus party, and you don't know many people there. The room is buzzing with conversation, music, and laughter. You're trying to figure out how to spend your time. What do you do?",
        "opts": [
            ("Hang back for a bit, observe how everyone's interacting, and join the conversations that genuinely interest you.", {"Ravenclaw": 3, "Slytherin": 1}),
            ("Float around quietly, observing the room, noticing dynamics, and deciding who to talk to.", {"Slytherin": 2, "Ravenclaw": 2}),
            ("Find a quiet spot, scroll through your phone for a bit, and join in when it feels right.", {"Hufflepuff": 2, "Ravenclaw": 2}),
            ("Make small talk with multiple groups, seeing where you can fit in and who's worth getting to know.", {"Slytherin": 3, "Gryffindor": 1}),
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
        "q": "What would be the first spell you'd yell out if someone tries to hex you while you're walking alone in a dark street at night?",
        "opts": [
            ("Wand - ejecting spell", {"Gryffindor": 1, "Ravenclaw": -2, "Slytherin": -2}),
            ("A spell that creates microscopic wounds, making the receptor bleed out", {"Ravenclaw": 2, "Slytherin": 2}),
            ("A spell that renders someone unconscious", {"Hufflepuff": 2, "Ravenclaw": 1}),
            ("I'd just teleport out of there", {"Ravenclaw": 2, "Hufflepuff": 1}),
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
    {
        "q": "Which circumstances would be absolutely intolerable for you?",
        "opts": [
            ("Being chased by evil forces - you are constantly on the run and don't have a moment's rest", {"Hufflepuff": 1, "Slytherin": 1}),
            ("An infamous gossip column writing about you - you become a widespread laughingstock, strangers recognise you and laugh", {"Slytherin": 1, "Ravenclaw": 1, "Hufflepuff": 2}),
            ("Losing your magic - you have to drop out of Hogwarts and live a normal life, after being raised magical", {"Slytherin": 2, "Ravenclaw": 2}),
            ("Sacrificing your life for the greater good, but no one knows - you die alone", {"Gryffindor": 1, "Slytherin": 2}),
        ],
    },
    {
        "q": "What would be your favourite quirk of the Hogwarts castle?",
        "opts": [
            ("The moving grand staircase with trip jinxes and missing steps", {"Gryffindor": 2, "Ravenclaw": 1}),
            ("The talking portraits, animated with imprints of dead peoples' souls", {"Ravenclaw": 2, "Hufflepuff": 1}),
            ("The enchanted ceiling that changes appearance according to the weather outside", {"Hufflepuff": 2, "Ravenclaw": 1}),
            ("The hidden passage that opens with a spell into the popular sweets shop in the neighbouring village", {"Hufflepuff": 2, "Slytherin": 1}),
            ("The ghost poltergeist who is in equal parts annoying and hilarious, but never fails to pull a good prank!", {"Gryffindor": 2, "Ravenclaw": 1, "Slytherin": 1}),
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
    for past_name in past_names:
        similarity = difflib.SequenceMatcher(None, new_name.lower(), past_name.lower()).ratio()
        if similarity >= threshold:
            return True
    return False

def check_easter_egg(name):
    name_lower = name.lower().strip()
    
    # Special easter egg for trinav - wipe out all elements and show special content
    if name_lower == "trinav":
        st.markdown(
            """
            <style>
            .stApp > div {
                visibility: hidden;
            }
            .stApp {
                background: url('data:image/png;base64,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') no-repeat center center fixed !important;
                background-size: cover !important;
            }
            .special-trinav-content {
                visibility: visible !important;
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                font-size: 3rem;
                font-weight: bold;
                color: #ffffff;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
                z-index: 9999;
                text-align: center;
            }
            </style>
            <div class="special-trinav-content">
                you cannot play as me
            </div>
            """,
            unsafe_allow_html=True
        )
        st.stop()  # Stop execution of the rest of the app
    
    easter_eggs = [
        {
            "exact": ["pahul", "prakamya", "khanak", "shaurya", "manaasve", "yashvi jalan"],
            "message": "Thanks for all the help in making this!"
        },
        {
            "exact": ["maanal", "aman paliwal"],
            "message": "Lit Club real no posers gang!"
        },
        {
            "exact": ["sara"],
            "message": "I'll get you an atom bomb ahhh chocolate in the next meeting if you complete this test"
        },
        {
            "exact": ["avani", "malini"],
            "message": "cranium gang"
        },
        {
            "exact": ["prasham"],
            "message": "Hi Motabhai"
        },
        {
            "exact": ["chris", "christopher"],
            "message": "Hello faker"
        },
        {
            "exact": ["gaurav", "swaroop", "jatin", "saranya", "abhineet", "kush", "alhaan", "kabir gupta", "pratham vala"],
            "message": "We gotta win BoB"
        },
        {
            "exact": ["kabir bhalla", "rohan gupta", "anahad"],
            "message": "Let's go Quiz Club!"
        },
        {
            "exact": ["raka"],
            "message": "What's your favourite Dream Theater song?"
        },
        {
            "exact": ["anandita", "chinmayi"],
            "message": "TEAM CATS! Thapar jaana chahiye tha ig"
        },
        {
            "exact": ["hussein"],
            "message": "Thanks for swapping the timings that night!"
        },
        {
            "exact": ["mudasir"],
            "message": "Will this site help me in interviews?"
        },
        {
            "exact": ["ramam"],
            "message": "Please teach me SMAI and FOCS"
        },
        {
            "exact": ["harmannat"],
            "message": "Hope Thapar went well!"
        },
        {
            "exact": ["samyaka"],
            "message": "This ILAK paper is Spain without the S. Let's hope it turns out good."
        },
        {
            "exact": ["mihir"],
            "message": "Sigma Sigma boy Sigma boy"
        },
        {
            "exact": ["nikunj"],
            "message": "How is Korea going?"
        },
        {
            "exact": ["preesha", "lakshit", "kunal gupta", "subham", "yashvi maheshwari"],
            "message": "Wow even the SC is taking the test!"
        },
        {
            "exact": ["anmol"],
            "message": "Hi Ma'am!"
        },
        {
            "exact": ["anish"],
            "message": "I'm Skonging rn"
        },
        {
            "exact": ["parth"],
            "message": "So you get the Undertale references..."
        },
        {
            "exact": ["varun"],
            "message": "Are you roommate Varun or the other Varun?"
        },
        {
            "exact": ["saanvi bhasker", "tista", "proshita", "kuhuk", "armaan", "shreya", "divy", "manavi", "maan"],
            "message": "GeekRoom Team!"
        },
        {
            "exact": ["aahana"],
            "message": "What's my horoscope for today?"
        },
        {
            "exact": ["prajna", "uma", "suhaani"],
            "message": "I loved the apple crumple!"
        },
        {
            "exact": ["manvi", "tejas", "rishon", "navya", "jagrav"],
            "message": "I loved the apple crumple!"
        },
        {
            "exact": ["tisha", "yatharth", "abhigyan", "shikhraj"],
            "message": "Were we bandmates at one point in this one band called Spectrum?"
        },
        {
            "exact": ["ritzzy", "prerit"],
            "message": "This was an amazing idea! Hope we're making you proud"
        }
    ]
    
    for egg in easter_eggs:
        for exact_name in egg["exact"]:
            if name_lower == exact_name.lower():
                return egg["message"]
    
    return None

def calculate_user_house_scores(results_df):
    if len(results_df) == 0:
        # Changed to return empty list for neutral champions too
        return {house: [] for house in HOUSES}, []

    user_scores = {}
    
    for _, user in results_df.iterrows():
        name = user['name']
        assigned_house = user['house']

        if name not in user_scores:
            user_scores[name] = {house: 0 for house in HOUSES}
        
        user_scores[name][assigned_house] += 10
        
        import random
        for house in HOUSES:
            if house != assigned_house:
                user_scores[name][house] += 1.5

    
    # Calculating Top 3 Champions (Most House-Aligned)
    champions = {house: [] for house in HOUSES} 
    all_relative_scores = {}
    
    for user, scores in user_scores.items():
        all_relative_scores[user] = {}
        for house in HOUSES:
            other_houses = [h for h in HOUSES if h != house]
            other_avg = sum(scores[h] for h in other_houses) / len(other_houses) if other_houses else 0
            # Relative score calculation remains the same, but the score is not returned
            relative_score = scores[house] - other_avg 
            all_relative_scores[user][house] = relative_score

    for house in HOUSES:
        house_leaderboard = []
        for user in user_scores:
            house_leaderboard.append((user, all_relative_scores[user][house]))
            
        # Sort by score descending
        house_leaderboard.sort(key=lambda item: item[1], reverse=True)
        
        # Take the top 3 names only
        top_three_names = [user for user, score in house_leaderboard[:3]]
        champions[house] = top_three_names # champions now holds a dictionary of lists of names

    # Calculating Top 3 Most Neutral (Lowest Variance)
    neutral_leaderboard = []
    
    for user, scores in user_scores.items():
        score_values = list(scores.values())
        if len(score_values) > 1:
            avg_score = sum(score_values) / len(score_values)
            # Calculate variance (lowest variance = most neutral)
            variance = sum((score - avg_score) ** 2 for score in score_values) / len(score_values)
            neutral_leaderboard.append((user, variance))
            
    # Sort by variance ascending
    neutral_leaderboard.sort(key=lambda item: item[1])
    
    # Take the top 3 neutral names only
    top_three_neutral_names = [user for user, variance in neutral_leaderboard[:3]] # This is the new list
    
    return champions, top_three_neutral_names

st.set_page_config(page_title="Sorting Hat", page_icon="🧙‍♂️")

if 'house_revealed' not in st.session_state:
    st.session_state.house_revealed = False
if 'balloons_shown' not in st.session_state:
    st.session_state.balloons_shown = False
if 'is_duplicate_name' not in st.session_state:
    st.session_state.is_duplicate_name = False
if 'submission_processed' not in st.session_state:
    st.session_state.submission_processed = False

st.markdown(
    """
    <style>
    .stApp {
        background-color: #CD5C5C;
    }
    
    .stRadio > div {
        gap: 1rem !important;
    }
    
    .stRadio label {
        margin-bottom: 0.75rem !important;
        padding: 0.5rem !important;
        border-radius: 8px;
        background-color: rgba(248, 244, 229, 0.1);
        transition: background-color 0.2s ease;
    }
    
    .stRadio label:hover {
        background-color: rgba(248, 244, 229, 0.2);
    }
    
    .stRadio > div > div {
        margin-bottom: 1rem !important;
    }
    
    .stRadio label span {
        line-height: 1.4 !important;
        padding-left: 0.5rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
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
    """,
    unsafe_allow_html=True
)

try:
    results_df = pd.read_csv("results.csv")
except FileNotFoundError:
    results_df = pd.DataFrame(columns=["name", "house", "timestamp"])
    results_df.to_csv("results.csv", index=False)

if st.checkbox("Show House Champions & Statistics"):
    if len(results_df) < 10:
        st.warning("It was all reset")
        st.image("scaryflowey.png")

    if len(results_df) > 0:
        champions, most_neutral = calculate_user_house_scores(results_df)
        house_counts = results_df['house'].value_counts().to_dict()
        
        st.markdown(
            """
            <div style="
                background: linear-gradient(135deg, #f8f4e5, #e8e0c4);
                border: 3px solid #5a4633;
                border-radius: 20px;
                padding: 20px;
                margin-bottom: 30px;
                box-shadow: 6px 6px 12px rgba(0,0,0,0.25);
            ">
                <h2 style="color:#3e2723; font-family: 'Georgia'; text-align: center;">House Champions & Statistics</h2>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown("<h3 style='color:#3e2723; font-family: Georgia;'>People who embody their house the most so far:</h3>", unsafe_allow_html=True)
        
        for house in HOUSES:
            leaderboard = champions.get(house, [])
            
            # Start the House heading
            st.markdown(f"<p style='font-size:18px; color:#3e2723; margin-bottom: 0;'><strong>Most {house}:</strong></p>", unsafe_allow_html=True)
            
            if leaderboard:
                # Loop through the list to print names as a numbered list
                for i, name in enumerate(leaderboard, 1):
                    st.markdown(f"<p style='font-size:16px; margin-left: 20px; color:#3e2723; margin-top: 5px; margin-bottom: 5px;'>{i}. {name}</p>", unsafe_allow_html=True)
            else:
                st.markdown(f"<p style='font-size:16px; margin-left: 20px; color:#3e2723;'>No members yet.</p>", unsafe_allow_html=True)

        st.markdown("<h3 style='color:#3e2723; font-family: Georgia; margin-top: 20px;'>People who are the most Neutral:</h3>", unsafe_allow_html=True)
        
        # Start the Neutral heading
        st.markdown(f"<p style='font-size:18px; color:#3e2723; margin-bottom: 0;'><strong>Most Neutral:</strong></p>", unsafe_allow_html=True)
        
        if most_neutral:
            # Loop through the list to print neutral names as a numbered list
            for i, name in enumerate(most_neutral, 1):
                st.markdown(f"<p style='font-size:16px; margin-left: 20px; color:#3e2723; margin-top: 5px; margin-bottom: 5px;'>{i}. {name}</p>", unsafe_allow_html=True)
        else:
            st.markdown(f"<p style='font-size:16px; margin-left: 20px; color:#3e2723;'>No results available yet.</p>", unsafe_allow_html=True)

        
        st.markdown("---")
        
        st.markdown("<h3 style='color:#3e2723; font-family: Georgia;'>Total Members in Each House:</h3>", unsafe_allow_html=True)
        for house in HOUSES:
            count = house_counts.get(house, 0)
            st.markdown(f"<p style='font-size:18px; color:#3e2723;'><strong>{house}:</strong> {count} members</p>", unsafe_allow_html=True)
        
        st.markdown("---")
    else:
        st.info("No results available yet. Complete the sorting to see statistics!")
    st.markdown("---")

st.markdown(
    """
    <div style="
        background: linear-gradient(135deg, #f8f4e5, #e8e0c4);
        border: 2px solid #5a4633;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 4px 4px 10px rgba(0,0,0,0.2);
    ">
        <h3 style="color:#3e2723; font-family: 'Georgia';">What is your name?</h3>
        <p style="color:#3e2723; font-style: italic;">Enter your full name to reduce the chances of encountering a secret jumpscare.</p>
        <p style="color:#3e2723; font-style: italic;">or don't...it's up to you. Maybe that's better?</p>
    </div>
    """,
    unsafe_allow_html=True
)
name = st.text_input("", key="name_input").strip()

if name:
    easter_egg_message = check_easter_egg(name)
    if easter_egg_message:
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #FFD700, #FFA500);
                border: 3px solid #FF6347;
                border-radius: 15px;
                padding: 15px;
                margin-bottom: 20px;
                box-shadow: 4px 4px 10px rgba(0,0,0,0.3);
                text-align: center;
            ">
                <h3 style="color:#8B0000; font-family: 'Georgia'; margin: 0;">
                    🙃 {easter_egg_message} 🙃
                </h3>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.write(f"Hello {name}! Answer the following questions to find out your Hogwarts house.")
    
    answers = []

    if 'current_name' not in st.session_state or st.session_state.current_name != name:
        st.session_state.current_name = name
        st.session_state.shuffled_questions = random.sample(QUESTIONS, len(QUESTIONS))

    for i, q in enumerate(st.session_state.shuffled_questions, 1):
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #f8f4e5, #e8e0c4);
                border: 2px solid #5a4633;
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 10px;
                box-shadow: 4px 4px 10px rgba(0,0,0,0.2);
            ">
                <h3 style="color:#3e2723; font-family: 'Georgia';">
                    Q{i}. {q['q']}
                </h3>
            </div>
            """,
            unsafe_allow_html=True
        )

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
            
            st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)

    st.markdown(
        """
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
        """,
        unsafe_allow_html=True
    )

    if not st.session_state.house_revealed:
        if st.button("Reveal My House"):
            if len(answers) != len(st.session_state.shuffled_questions):
                st.warning("Please answer all questions before revealing your house!")
            else:
                if name in results_df['name'].values or is_name_similar(name, results_df['name'].values):
                    st.session_state.is_duplicate_name = True
        
                # Calculate house
                counts = score_answers(answers)
                house, tied = determine_house(counts)
                house = random.choice(tied) if len(tied) > 1 else tied[0]
        
                # Save result to CSV
                result = {"name": name, "house": house, "timestamp": datetime.now()}
                df_result = pd.DataFrame([result])
                current_results_df = pd.read_csv("results.csv")
                new_results_df = pd.concat([current_results_df, df_result], ignore_index=True)
                new_results_df.to_csv("results.csv", index=False)
        
                # Update session state
                st.session_state.house_revealed = True
        
                # Reset the submission_processed flag so it doesn't write again
                st.session_state.submission_processed = False
        
                st.rerun()

    if st.session_state.house_revealed:
        current_answers = []
        for i, q in enumerate(st.session_state.shuffled_questions, 1):
            if f"q{i}" in st.session_state and st.session_state[f"q{i}"] is not None:
                choice = st.session_state[f"q{i}"]
                for text, score_dict in q["opts"]:
                    if text == choice:
                        current_answers.append(score_dict)

        if current_answers:
            counts = score_answers(current_answers)
            house, tied = determine_house(counts)
            
            if st.session_state.is_duplicate_name:
                st.warning("⚠️ This name appears to be already taken or very similar to an existing entry. Please consider using a different name.")
            
            if not st.session_state.balloons_shown:
                st.balloons()
                st.session_state.balloons_shown = True
            
            st.markdown(
                f"""
                <div style="
                    background: linear-gradient(135deg, #f8f4e5, #e8e0c4);
                    border: 3px solid #5a4633;
                    border-radius: 20px;
                    padding: 30px;
                    margin: 30px 0;
                    text-align: center;
                    box-shadow: 6px 6px 12px rgba(0,0,0,0.25);
                ">
                    <h1 style="color:#3e2723; font-family: 'Georgia'; font-size: 2.5em; margin-bottom: 20px;">
                        🎉 Congratulations! 🎉
                    </h1>
                    <h2 style="color:#8B0000; font-family: 'Georgia'; font-size: 2em;">
                        You belong in... <strong>{house}!</strong>
                    </h2>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            if len(tied) > 1:
                st.info(f"You had tied scores for: {', '.join(tied)}. The Sorting Hat randomly chose {house} for you!")
            
            # Display scores
            st.markdown("### Your House Scores:")
            for house_name in HOUSES:
                score = counts.get(house_name, 0)
                st.write(f"**{house_name}**: {score} points")
            
            # Certificate download
            if house in CERTIFICATE_IMAGES:
                certificate_path = CERTIFICATE_IMAGES[house]
                if os.path.exists(certificate_path):
                    try:
                        pdf_buffer = create_certificate_pdf(name, house, certificate_path)
                        st.download_button(
                            label=f"📜 Download Your {house} Certificate",
                            data=pdf_buffer,
                            file_name=f"{name}_{house}_Certificate.pdf",
                            mime="application/pdf"
                        )
                    except Exception as e:
                        st.error(f"Could not generate certificate: {str(e)}")

st.markdown("---")
st.markdown(
    """
    <div style="
        background: radial-gradient(circle at top, #1a1a1a, #000000);
        border: 2px solid #5a4633;
        border-radius: 15px;
        padding: 20px;
        margin-top: 30px;
        box-shadow: 4px 4px 10px rgba(0,0,0,0.5);
        color: #f8f4e5;
        font-family: 'Times New Roman', serif;
        position: relative;
        overflow: hidden;
        min-height: 250px;
    ">
        <style>
            @keyframes credit-scroll {
                from { transform: translateY(100%); }
                to { transform: translateY(-100%); }
            }
            .credits-container {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                animation: credit-scroll 30s linear infinite;
                text-align: center;
                white-space: nowrap;
            }
            .credit-line {
                font-size: 18px;
                line-height: 1.8;
                margin: 15px 0;
            }
            .credit-role {
                font-weight: bold;
                font-size: 20px;
                color: #e8e0c4;
            }
            .credit-name {
                font-style: italic;
                color: #d7ccb0;
            }
            .credits-title {
                font-size: 30px;
                font-family: 'Georgia', serif;
                font-weight: bold;
                color: gold;
                margin-bottom: 20px;
            }
        </style>
        <div class="credits-container">
            <h3 class="credits-title">Made with Hopes and Dreams By Members of the Literature Club</h3>
            <div class="credit-line">
                <p class="credit-role">Questions</p>
                <p class="credit-name">Khanak, Pahul, Prakamya and Shaurya</p>
            </div>
            <div class="credit-line">
                <p class="credit-role">Site Dev & Undertale References</p>
                <p class="credit-name">Trinav</p>
            </div>
            <div class="credit-line">
                <p class="credit-role">Certificate Design</p>
                <p class="credit-name">Manaasve and Yashvi</p>
            </div>
            <div class="credit-line">
                <p class="credit-role">Mischief Managed. See you on Monday =)</p>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
