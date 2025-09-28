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
        # {
        #     "exact": ["trinav"],
        #     "message": "So it's you"
        # },
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
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
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
headimage = "hp event poster (1).png"
image_width = 900 # You can adjust this width

# Use columns to create space on the left and right, effectively centering the image
col1, col2, col3 = st.columns([1, 2, 1]) # 1:2:1 ratio for centering (adjust the ratio as needed)

with col2:
    try:
        st.image(headimage, width=image_width)
    except FileNotFoundError:
        st.error(f"Image file '{image_file}' not found. Please ensure it's in your directory.")
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
    name_lower = name.lower()
    if name_lower == "trinav":
        new_tab_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" 
        
        st.markdown(
            f"""
            <script>
                window.open('{new_tab_url}', '_blank');
            </script>

            <style>
            /* 1. Define the SHAKE animation */
            @keyframes shake {{
                0% {{ transform: translate(1px, 1px) rotate(0deg); }}
                10% {{ transform: translate(-1px, -2px) rotate(-1deg); }}
                20% {{ transform: translate(-3px, 0px) rotate(1deg); }}
                30% {{ transform: translate(3px, 2px) rotate(0deg); }}
                40% {{ transform: translate(1px, -1px) rotate(1deg); }}
                50% {{ transform: translate(-1px, 2px) rotate(-1deg); }}
                60% {{ transform: translate(-3px, 1px) rotate(0deg); }}
                70% {{ transform: translate(3px, 1px) rotate(-1deg); }}
                80% {{ transform: translate(-1px, -1px) rotate(1deg); }}
                90% {{ transform: translate(1px, 2px) rotate(0deg); }}
                100% {{ transform: translate(1px, -2px) rotate(-1deg); }}
            }}

            /* 2. Target the BROWSER BODY for the shake and background */
            /* This is the most reliable way to shake the WHOLE viewport */
            body {{
                margin: 0 !important; /* Remove any margins that interfere */
                overflow: hidden !important; /* Prevents scrollbars from appearing during shake */
                
                /* Apply the Shake animation to the root element */
                animation: shake 0.3s cubic-bezier(.36,.07,.19,.97) both infinite;
                
                /* Apply the Jumpscare Background to the root element */
                background: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAOsAAADWCAMAAAAHMIWUAAAAjVBMVEUAAAD///8BAQHz8/P29vbp6en5+fns7Oz8/Pzy8vLo6OhoaGjv7+/j4+PV1dXPz8/Jycnc3Ny7u7uysrJ5eXmSkpKfn59ycnKJiYnBwcFAQECtra1iYmJdXV24uLjOzs5MTEwODg6ZmZlLS0s0NDSBgYEnJydUVFQXFxdDQ0MwMDA6OjptbW0qKiogICCPadbGAAAgAElEQVR4nO2dC4OqOLKAw/uNoIIgoqIivv//z7tVCYEEwe5zzszs3N1md04rSSUpEmLlo1IQ8nP8HD/Hz/Fz/Bw/x8/x54cK/yMqHPgPP6fSsyyVZ2BZ1TY3E2jztkJUpj2ndn+ZqMqL6mRVVn77//az2pbE28Zb0P9f5ZWI+frTXRXjug4/jH1XByfePo8mqsMMoy2YOt4yjzbirY5Px/l2IerzVhFyup9uhFQ3+Hy5PQm5nO53+PO6nSHX6UXI874+Qb4nSFS3J3y6re8nKkF6iRdKvFguyLC+dxI3aMvtfr+1ErTc1/1+P3cSkPUMGfAPFA91qKQ6UQlaPJV4ntZYxxkkVFrHCepQmQqXJ+SqWLPHDktJyElRjnXgNo1r1VdFOZNEMchWKZqVEj4LJSYkVtJ7qHjl1twSX6nJXVGemRGXjR8sG0W5kAPkys20rJWwWigRIYGSHKmEXhBHWZI95DpYs6bUAs9TtIoUSkhyJWkyZUYiJSdYbhPrmybSUqIrG1IqSnXQoqZ0gnKlOARalJOdkpUJlL9TCqL6ymMTm2Uz8w8XRWnIQ9FJ6uTlxo6bsV52QdebqVxTqJqESrpmugZwETLyVJR7Cm0BXQ/Q2IomBEzXV4EqxUqyV+wLJMQgscSES8F0zUpFr+AihJCwQl1VbCxI1KXiVCRVdlQlSCBzZYstWXqKRQiK+0oJuppwMRaYsHrAxYeEnNigEpQLV6fABG8JDSILZV7pyp54cEXwIoD4Y6xf4fqTs62sqa4x1fVFslZX6PBTq2uCHUNVMkRdQbxRTNavBugKwwL6laqEul5ISnV9kCMkbJU5StQbpusMOtwjDdc1UJYbxVffdTWU1Upxma4mJHhcVwN1dbHD5yrXFRMqLHekXwMlPYMaoq778wF0NVpdYaxdXtCvx17X5NnIuh5vhaTr7nai/WpyXbPng+qat7pq6+dW0jW63S2qK1PJV5a3laSrf3/OIUGHft1QXee3q9XpmkO/es8liH/W1dRNSVdbse1W1xvV1TYhA9OVdZ9t2jDSe11tOCRdqQT2q9rqSk90unoKiki62qauoK4W09WhdbS6WjiGFRNOiLqaNhTJdMUxbNIMPozhlBBtXFe8X590DNu6bktjmNYPus7wRkZddbgqgTCGaQbQVecXwcQTwhim11G8X21Ns7FfQSU2hvEi2FU/hkECVdK6MQytUtr7dUF1NTVT0YQxrGAG1BXHsAa60lZN6nqj/Rqf7jjd4tyUUZUOp5KNYTo3HRX7CDeveL/uTifWrzhUMSE7eVTXiN+v+3vR368qNPZ2N+gY5vdrfV/SDme6wg13vW9BXKPzMOo6P11hQD/w6jBdl/e6vV9VOoat+ynv5iZ6EU5X/StdhXl4ZG7Cfq3EuQnG8K4dw0o/N625rnwe5nPTnunK71dpbqr6edhn87De6drdr1xXnIdZv8JvDh/DuaBrOnm/GqirPfjNQV1dputd0PUy0JWqdJB0hfv10verzXT12RiuFt392v6+ap2u87Zf23mY6zpn9+uy0xXnYbxf25+Wfm4yO11hbvLHdd2GS3KOZvc6BOEirE/h7EWWcU7ycEWes/CZYcIiXN53uwtZhluSxw9yCsMXTdjGy2s4u5A6XJAo9jDhkoQplrvah1FFsNw8LMk6DCuWEHtNDAkoHoUNWc921SFOCOTaNGGOCSkk7Mk+3KkpJFQgXoa5SlA8mh3JPopIGmaY0HghXL5kd6ii2ZU0YZ8woqtoZEpGt5RpmDBqq34rYdL+Hm3Zx4TPdY2Y/4PFh/yBr1LkE8Ovo2c+J384MWyM2q2K2vXShzIIz8y+/xz/s8fv9L48ZPiw+71x9D2hwTD9zVH7O2J/oa4cTnwhO9T1G7X1TKUlHrwUga1IDRfmAF5nB3F4iUTlLEYsoWudKqAdVS6CyMKDDETEL+KspXbS/Z9RXT9QFPH7FO0YRSzjEp9OvLXuy0q/rmN4xCYsZwz/SEpfc/wNOVrGmdQ+2EoLTfNjggt9QiI/IWrgaxqYD6EPS3LLP5GV5Wt+QxoneJGDDhJzR9PB+ip8sPh2GvymW5qupeQSax45+v6ZLDXH8ddk48RgQWs55tJRcKGDeRRrS3ILNM1JQMIvSWO5Z5LAdwuqcmIwwZwFtkRzwCxbWClRY98jd9f3tZqcXX/Pyk0cRwvOY6pye/i6jIOmiQPOYAKy1ZHB7M5FayPeI8UrC70AiZbBuPG+MeJVZ/sv7LRcmrOOS1x35qbZ+ikatGgKXrJgVpZG7HX28NxOmtqOwOxl9vA+dDZN7h+6dc7BiJqNHzYPbiPmdlYmes7WOWBnl6FfNpGRXHTlSNfqB3/ebPRRu4npKtjDd9H2v/E1HWMwasdgwFA+t2Yv4xIpZTCr1vbvuAS3/Zk9zLlEybkEmr1wqXA5Q3V9cNvfEW1/F21/q2cwG76mg3VOjQxm29n+7fp1cq3O168jvOkkremo7R/wfu14U8dgrM72z+V1Dvbrka5fqUrIYFSqK7P97Y7BeJhQ0DWdzGAeXFezW6vLDKbShYswzSUOZxhf4jrn+kqHDCbouATqmpxlBmPfL2mr65Gtc85PV+rX+gXLcNLrqt1fRacrcon55WYJujrK6iUyGE+xbq+txCUWr5Ml6eqdl1+s6ZDB6DJvshWOH85UVwWRC1+/YoKN+IOtX2OBwVhs/Qq60gyoK+EMBjKI/YpfQdzpOKKCEv36VcNW2GK/UhHUdd/qCukyg8E6mK5TYxjv1xMdw6bvmFTXZ8slTF3ja3XOYPT2IqwZg9Ecm47hV7t+1Rxd4hJUor1fbcpgfF+hY/hCmamv6JqumGo/hukJPoZ1ymA0ymBcvlbXNY0PVdqvFOuIXMLUfGQw0/MwMpjrlTMY1n3pdUN17RhMcy0kBhNe14EwN8Gy/yozGLO5Llpd2f26Ox7dlksUVNfsWvP7lXGJ5jrvGAzqml/3fnu/LiiIqo8yg/GPa5nBLK6N/pWuwjyctN0nzsMdg7He5iZbYDD2CIMxBvNwpytnMNtW1wfifTaGvQELt8YZzKq/XzkfTimwmGQwygj3d7u5aUZnMKrrQRrD3dwkzcOirpdPDAZ/c+g8rM6Hvzl616+Mma64rhILp/1qEJzaBAYzPTfN4yV5huG9juHSLuIM6QpjMDFlMLcsXCA4qddheIGEOWMwcfxK4oKKX8NZRVA8D8GMQQZDE4JlE0NCBl+iuCTXMKwOMWcwO0xYkF3ckCMkpPGBQLleGUYtg4GEJgwZg5mH5SaGy5eA+Cw8QsKO0ATI5WHCIUyrWbgmJXxJ4wwTyonl0pdQY5Kk/Dqc+T6DmTymmymdHONN/XqhW60IqwiRcRDhLxHTiQBqSFeGSFAG3IR0i53+ZLfAEtdSRHzKLIiLCX1OQsQm//bF/Dn+Px8cCfz2EPglsT8aZh/b+B0FOl1/tx2iv8aXyvzjuorzSXd/s8mGt0ecggifWCRI009n7HM3x3TFdd8I6eYQ0mfnOUiXQxQZRx/98OvqEUjR6Dz8XT4yzl2+wUcGYt89fpPB8Axj/bpzwRQM3CvZGL5vwW9+EJxJbVHM4ftgSx18ZDBOAvag7/tgDITWipwMAxkM5IDffDd+kcSFXAvDt2DtkxrISoyaXALDMA6kCl2PHIPgSZYg4N5JGYBZkhhgK+VQZITUBqyPHZT7DCzLAishtqDcAMrNDMsKbuThhm25ueVbtKoD5tqQe+BbPqzIYgMWQAYyGCgBGcwUlwAbcRW7ZRmAFcRtxMIpyqUddQzmFimrzYISFcZg6iBGovIAI4+tcwoz9TI76mzEa2SvyrmVUhsRGUwdzDaeBVYQM5R3ZGEeykzPOy5xnDmPMjISsBFxnWPDJYxKT0MGY3EGk5SJue0YTBP6Xrlzswsu4tFGTKx889Bmxw8M5p1L+APbf//+/PWNS6za9WvHYNRRBtPxJjTxcf2a988kRxiMITAYU/SDoQzG4Aymaf1gPq9fBwzm1a5fBdtfZDCjuqbS81eua+cbQtd0F4FLqMKzZpHBdLa/wGAsQVddZDCyb8j+SwbjKunryNc5jEusq4EfTFWJDAYSLkfmQ8D9YO4V17VlMNVF9oNZViXvV6br6VJIvGl+eRoSb3pcPGlN5z8vW4k3LS5PWdfysmrXOZdJXalDiairqdiUrdXk1TIY5gdjk3YMUx4irOkUxmDcbgwjQWkZDPPloicEXfEr1XWDVwf9YLBI3q85YzASW4Nm2t36FXVVWgbT+XLhCe3L9StjMLblMz+YWztU3xgMIhZx/Wo6HYNhbE13NJnBaD5nMA3lEqYPdcD61b/Q9asDEg5dv/K1Opww6Rj2oPtQVxOpjegHY2t6O4ZbBuNoZssRWwaDzf60VkcGc9zHwtxkKOnek+5XuzwOGczVkOam5Lii3df5wWyOMoOJ9o2FunZ+a8m+lnz0/OaYS/drjhI9M0UGk0n3q9UcI2mtvm3KCf+mYMwPJhFYuOSPeOgZzPnNRw9Vuo77wcjzcKdry0zVnsF0HFGYh4M3BqMLfjDG9xnMpK7GwOen+81x2Rh+vjGYdz+YAYMRfPQuAoNRRAZTCbraVNfKEHRlDMbkfqYig2m+ZDB5vCTnMLhn8RzBSXaP4zNjMMGS3OL4lCCcmcf1OgajpIZckYt+MPGNopY8qI8xWEEoHsUPco+DyyEoaLn7gCbAD3+wIdc4ZgwmCh5NMIPLBrl2QUn2cVilASbEjxKpDZY7C8BuikM1DQ4o4ZUUtUCuMD5CwowUyGBA3AvQDyZMqzC4kjLekSJgCb/NYL6dc3rlMZXwFx5SHeO2v7By4SyESAxFWHb05XCA0q95et4i5hCWiJzedOuJDueIiyCpRd3iUFh7qcNMHdbh//Fn2f/tx/8SaPo1XcVl9y/XI3CJL5Hen/XAhPSvccTf502SrhyE/E26TrXxg679ja128KQjH8KsI2bjc0T/ucvVnlB7ssM/dsylL5vPNm+XhBPgDq70U1+boddV7SVUVe2/f2IwwvdfYzBk+JnX/VbPpMSw+NEMUi6VTBUpNPvt2BkIMGL4IQ7cAH7B13HwInWAYCRwDbClEmOL5CMBqypwXfjN3wUrcgqCE3kEhhscyZ6yEvxNBwkXBNOAGRkIX1wXftpngUeOaKOs4Ht8h9/8GSyFgwUaLwEVdAtqZEBLXDfIULAkTRBiS+DEmXgBsh2Xlhu4VALKDQNkMJZhLMkrhpZsqPGCdbzGVOW2//4Rup4XxCuBwSy82o5eHYOZg22OXi2tPXyr49jbuKHXMxi98BJ73tnD99xcPubGgduIlzoOPc8JS48ZymD96KmXmDlpbcT6GmmPTe4m7XM6u8qCnffQo31rI0akMJPNQV/0DGbnPDa7ABnMnuAjzczNHyt9t/+8zunWr8wPxm/3IglcgnTPJO+SD4Fs+1+2ve1Pur1IR27iB51vyI6ava2/hMwltAGDEexhmUvU/VqdMZjZVwzGHNmLNMpg5HXOTl7nGFN+MJboBxN89IPpdJ3wg9FbH3jp+etWeK6++8BgsF/v8r6ru5rIDEaVdIWE6ij7/DzJgMEQdahrI++7epIBg1FfrsTWHqrMYKwz6RkMw0rn/lkzZTDqg+r6aW8D7uGRdGUMxugZjDJgMNSLRfQhgK80YYVXB/1ghgyG+8HwMUyPGe2+Y+sHYysSW0MJ1LVodaWVyAxGGWMwnzgi7Veqq2kZjMGc2vWrjvjj1N6W2K+GpdP1a4ZDFRkMEhXs13Pb4brvyAzGt0yZwViWQhnMq2Uwvuu3DKZiDEaDOnK6sGX9alpQJHLES7tWdzo/mBdjML6vU11LwvpVxzpGfUOMjg/HZTnwg2keEh+2N01BdV1yBlM2lrAXyVIOTS3vRfKahcQldk1pSXsHkzKD8bLtGUzZ5NLcFDWlLzHTuskkvzWrbCJp39W8KZ0Puo75wQz9EY8il5D5sD2yFyl+34sk3K++6AfT+/yMMxjqj2j0fLhj4b7gy/UdBjPJ/ft9V7v3eXgt7x1kCa7oBzNk4Q1NYD+jHvpyyT56nc+PuBeJMRjVEPxgGAs3Bf+m1udHYjATukZg3zzj4JqhNbKNk1MA9k0N5k/kojtvwBhMHmRXymAgF2UwQfA8uJjg1scAEtBu2oF51DGYyK0bN6wgYUtCd4PPxFrU4q4a+uwKxEPKYOI2IXiUQcjgTBjQZ1dgHqVEjYLNhttNYbBvEw4tg9lRQ62K3SOYfjNuUI361ArHHyw7voQz/8TxDQbDaUf3yLc/KeEOYQ0gSIh2+RDKCDV237uHwcOieD7xhCotXroiBuuAPreo5j96lX9zEfzvKP7Xjv8dXX8fbny/gi9q/wuq+Ha+QX393fSbrRgU9+u6duyWMxI+ufRgRfzUfe61VrtOlN1n+o1CLJewcYiXIE5IIodRhQKEf4W5s2/EAAp1qGgKvXX/TDEY4TsZfh4t4kNF5D3XqMR4q4YSnzK8Hex5TrgmTRzHjMGcGYNJgwB/qFtWkhF1BicO9LkLOcXhiXhxEMRH+kCGPughBWTA5y4xe55DLiGcQBfXYIP7ml/kgRKUwTBnW7KFDHOsKqU+tfhkKQbj5jKLGywXvXtB4kk2uBOaPg6aMwl8nqPiYxswXoJgRV74oIeynQy+hx8ZzNHbuY9VED46LpH620dt55fWHk5vW7teza1Dx2CWYbBa+chgWuMx1YpVYm9Jx2DmIJELDGYZh6uVtWs2+AAPy031dHUwt8w3BBaR61xbPiK4PJzB1EG4XOrRsduvXpjp4+AX6EOAy9RHE/mrxyyoX8z2d0DVaLXU81E/mGBgD99FBjPwgyGSH8xCtP1xneN3PgScwWhs/YoJR7vnEh6PB9Pu41AlBpNKcQgK2Qde9IPBJfnA9ve/ZjACl8DVmmj73wRd+XKmiy8x6gN/efOBp+scu92fw7gEafdxMNt/O81gtu8+P54US6Oz/Y9k08a++S6DufdrdUHXQPL5yXp/f9avT5IqY/uu5HWOyJvO7T6OXteLHF+C+0t0DKbqGAz397+I6xy782+ajrlgKLYuMpg73QXUMphL6wejKy1HbBmMKTMYKMJsu+9EOSLfi6T1e5FMaS8SrQN15XuR7CGDQe8cmcHQvUh4W5bje5Hwe+vLNe0Ho14ZgzFcm+rK/JssRXMNdr9ytuZbDtuGozK2RiWQwZxatkYlcP2qVrRfFdfV6P1aqxvGYIKAxoNxbiqOF19xLIuxtYqxNdt1darrSn1QXbXANekYfl3YHjOkNnQbDrnRtbptuMwPpqxWVFfdcif9YLKWSwSUwXTzsKEUm6UU+8Z+lIsWP5yoruiPKN2v6abut6bg/foo572/BOg622zeGYxChP05j00kzU3RxpMZTFImsh+MV/YMxqEMxvsUD2bKR+/5PX/ELi6XsCdUZKatrkSYh7l/0wiDSacYzHAeVv03LvHZH9GYYjAG2+Z6Socs3Hjz+Wn71X+Ly2UO+TD3g9GnGEzrByMymIrvf90OuD/qOvC9/OyPiM+unoFxTQxoR24kdxefXRkRmVnIYIxbm5Ad3QCMEgsTVuQeuGfKYCIrYwzGzUloPMg6cC/Mf9ivG+rOSxM8AuJqajA3YZZgzQlu1d4HQVXQBOOxcWMwj9wFiQ1kMIFaWCmpQsvbuHDBUwsSLJibgpju4YaE8mFgglFUsQV2kxGTrY/ux8aUH8x/9Pi7mjRSrmRAC2TlDbWwDBIfeUcs79xpnI8MwMlkUeqoxBiDIW8S/8J+/Tn+weMvgSefwcGfVP1XDs+/BBR9ZD7TrjHfqPv3IY7sozKAG9K/RPrYbyXikgJHETkIL7kHNKTjJUSqo4PHXCOVdBkEysP/9OSGiPBF4tKSrn1jhJYPMwwhyTj+GDKYcawiJL7N2m+ZJxCLOtps+TdlpNA5bl8OQwzMFsfxkdxpbLkQwQh8B8uoDSFXg3kQxiGNAfcgt5AymDgOj2Q/i140thwp4ARzcWUx6y4zOEFDvZXkOpshgwGJO8aAaxnMAk5scWNyQtQ5lHvGRsD6CoPOHcMIGUyMLrubOK/ovmayCMN4wRgM3b58ChmD2YEKJYamqyHD7jV6AVt7+LiZGculO/M6P5jE2i4Te/viz5qfW6Veoe+P1RqPj1mwXGmzsuMSB3+7PJgF4fbwaatnSyQqVhuTdxnGy6UTNV7HYLRilYJEayPW61yvVztQtrX9qzoO61rPewaTmuky1VK6zlEd5bHPtSUUW18Yl9CRwYDE/PodBkPjSyTtPo7nWDyYLxmM4Acz3IuUywxGe4vJO2n7S88kNeH5a8BiQbJ1TstgPvjAd34wYz7wbwzGevP5sSvJ9t+OxeQd+MBz3iTH5J30gxkwmMGzZtnff5pLBCyutOgbchrVVdiLJPAmpuuLCPFgqr5fJ9c5Dou54AtrOjWYYjBMV5XweDBM10W7Z0WIffP4QleXRoaV+lU3zTacz4uu6WgO7svFwtGaMoNBiZh2350xGAwxI/rBsAC2PW+iiGVGGcyR7qez5XgwOq2jZzArtiFKXL9SMiTFgzE7P5hJXdNzQ+9XPQ50Fmu5jfPjuC7zb3phnB8YhHHgMwZzYXF+9Dg2KYO5Xgqqqx8EjMG8zjTOjxLEDmMwL49yCZ0zmPWLrdWNwKD9mp9v9H5V3ECjui7bOD9aDBIYu/V2ZrGWUQJ13b7ujMEE0Oz5xVS815Lq6gSx/dVaPfAegRS7tYCVcO/zA7quvLnETGPvYUk+eqmXyftzlo+c6spj8obeyu9ipKCu6SqR1+regMHsHiuZwRweBzkm78qLqK576vMTKfljOcFgPnCJNxY+Eg9G3p+zwgRRV9IymEcfG53vz/lin6TAwoe+IXJMXoOPYcEP5gML/+gHM4jLJeq6G2UwYyx8ODdpPW8que/lux+MKTOYReePqAkMpvW9tJX9lwwm9JHBWOsEd0bnfnI3XBZHDxNuhnVK6B5uP7taBmMwoQ/dZzjn1GLh8vYWwhk/IrEGv6+udUFWQnZ+XVoUteQE490dLaOiW7Vn/pImHHxkMBvSGG5VODQ+32pjIYOBcmOrhIRALfyUqKHveSyi35YEfsNQCzIYEF9ZuLnbLyrXOZKNjwyGbu7+VzKYv+141/UNZgz/68TUsQyTwGRY/ihRIVMJnxiMOizih8H8HCPHn3MJVRx+g5R3+PAf9N75LQYjy0z7/Ah+JBOyf9+hDvbwdH3Cu4ZjF3WYoWumgEj4fiHBJUUAFaKIeLZ3clE7itPm6rOIX1Wpiq44CeK8a9rVODgpZRAm5VHkIs3aw2I+8Jjh2eEsPlnE1wxmWB8e83BFzjv0g4nCMDyS+y56kVVIwUiIwfOzGY3vXxM1hxMJSMw8ctvNTmQD38Mrhtt/kRpzpfAdBJMZMpjZilQ7OFHT4HDkutu9iDcLQxBsZvmFlYsSBVKbBCU8csZGLEmV7xpyRLazBAkQ3MzmWO4BWjKjEuksQ2pTklMEJx7kFc1AhZbBILwZO3g8mDKy6tqNNgKDybODWVy47X8u7CTDfULte5Fu3izIaj8vS84lEn9bI1Gh61dY55wWZlLvKINhfjBeGGeZlu89Hg/m4BR1oaedjXhfmFm9i2uVxUix0XMmy/TttbMRD1qRFU7KbETKYPysDuPly2xj8tbxrs70xSiDGXkfx7Ozh8/y3nzyFYNZSgxm08czZQwGF2XEFbgE24vUx5cQ/GCG70UaiZEyeCa575+/foq5MLXOeWMwiTKIucAZTCrY/gKXuIi6snWO2z1X7/39BT+Yd9v/TdfOD8YaMJguHgwurEb7NcP3XYkM5jnQNZSfNb/Hl+j2cSzbEDdv+66Gazqn6p+r2zZ5e8+KM9avC4nBCD4/zL/p2On6IR6Mo48xmD4mr611DIb1K43iK/Sror0zGFtmMBi3BNbq3V4kTTe7vUj4+JwGl+3f7aUrOkhIDEbXTKrrsWUwtBHiXiQ88Tkmr6Gkt5IxmDDUqK7NLaVcwopjuncwvD1bBhMbVKXsWVJd9ThkDGZ/YwzGDWO2Vn+eKIOx49hnDOb2oP4SThhSBqMfbwvarwHUQRnMaU1jLYOERXWtT0uqqxPHjMGsT4zBBHHAQqHcrozBxLFGdX3caprgxOEkg8lav7XgsZIZzGJZ21RXfr/Wq3k7hk9U1/jx8AVm6ioFEhVxz0q9FBnMVgmXS1/iiMUytUUuoS29gR/MasBg0mUqx+RdrnbKVmCm+bL+lfciCe+nE5mp2kHyEd8QFnp3Pc5ghvFgOi6xkfjw453BLMYYjN6hUYEjfnMv0pSuX+wJ7XStyHhMXnPIYPheJMEPpuQxyBiD6f1gOB9WXeUxuhepEveEMrams71IE785oQbdZznrRIswXN7h7jswhrWQhDoMVV87HfCdAzMtufoWGDvaDiRW5O77z9SZI1HJ9r4LP0bIYHToV1+7ICshM71utAAugoZwBhmMXxX4yoJQW5ZaAJcNyg10fGWB0TIYbbVxYhWdeUnsQILvVgsd3V2ch+fE0OH6lgQO9KsVEAxyV8X6ZqXRhEXl6jAPa/haAmQw/g+D6U9Pe5x0Caps5kvAhAifJS4iJZCRnN9iMJMYZ0Lif6lff46/4vg+WRjLOXruPdO/Y1j+wj6nMTbzXV3/UNmObrTF8brbG10VHFz6HO9IQMjCc3XzmIBp5FSB0vQeLbw5PEMHV4TC+vhWA2rzNgUOr944URFOvPnBDEt4L184MX51Bp/ev3+cTH+PwSx2D3KOojtpot1sxhnMboFvLtztwCioIzC6igjByCzaZWClRBtyi6Ib2czC2e5KjlH+IssdgpEoQsEsSlDiARJwoibVNmrIOs8vxIt2u+gEVW0rVm66iyIQzPKMqAWU+8ohw4Nc5rsjK3cVwXEmZbRVSbY7YLk7FDxEUO4Cyr3lUKZHLjm0pNnlFVlCnfnHvUjXMiQ8n+oAAA2ESURBVPKTzIrKK1+/ZkaepXba7UU6F/YhQa+WlsGcvMjNaifv/WBqf56hj8qiZTA3pDa7oO4ZzC7IMm179Hic2kzfJgswdPhepPtCT7JZuOTvqKhWcZwl5uLa+cEkWpEUfsIZzGq90JIsDh8v5kOgq6s4TA7mYj1pD8t7VnoucabvCd2JDGYiFuQYg+nWr9zffz70DdE7HwK6DYe95nXMD2Y0Howq+sFwYNH6wE++m/omx0gZZzDD56+Crnr//PUox4OR3k0tMBhNZjCcrX2OfSP6weTvDOb4DQbz9h7ukXVOMKrr7r1fB8+aq8GablTXdk1nDHTdfOrX/P0dUNfvMBh82Y64pvM1jTMYmzIYDGArMhgaPEXoV0XTzHYfx53Fg8GXCIljWNMc2Q/G8nWqa9nqSsPRirrSlwgxlQLKYBzNlvYimQ4UuRF4E574ksHcBwymvDM/GDcMGVu731m/xqHLQqHcPaqrFoY67dfmzhhMgBL4zvH7lTGYMLSorsmdBbB1wplJ+7VZs3eOB2FMeVO+PrYMJvSprvW9Zn4wSG2QweArgSiDAQn6zvH7kTGYcOZTXVfrmq7VLWzEpG8IYzDuUmIwhrKtM85g2F6kbJlLYzhYrRzpnW3F8iDtzzGzOu99Q0DXsK4daS9SUaeSb4hWL3cSH54ta01mMHUq7UVy6nomMZiozszvvRepe9+V+85gRubheMBM170LyDSDEXTl76eb9IMZ8UfkfjCd39ov+cFMcf/vMph+bpL5cMtgnIEfjNf7N7G5Ke/5sPo+D7uD9yJtxnRFP5hHq+skg9EzcnP09UFHBqMf7poPY1gPSWyCSo5+OujIYPTk6jgvSJhBwgoTzqkJCaGZ7TULLoI5o34wV0e/FOYWy61L3a3IQd+RwMT3STpVYSKD0ZeQABcBxGMd+tW3VPY+SXO10eHXMtURzoCuukW2JvyMxubDw4RC2xJXh37VXDLXkMHY3spEBmMuKgsZjA4J5oFUgTbBYNTRj3/jMWQWkzVXfE0yJj1Z+KRF/EZUxJMSH1EFK36ajwyKemcxbyc+NeLjiR8G83NMHeKi+z3pz4v/7RcRfbP8X8s8GWDkr2jkt7Yb/S3Fd+HAOeLoMIsQ3YX7qXRTlNqDlf4szy24znQkh9fSS3DiIqb1jRQnQtI7ufS+QiJ0kTxnhKa+6/oN8vGRdvTFDHN8/E2RpvGxY7zSYbM/ZXg7kJWc5/mdNDkce3LP8xfxcgQjURTBT/wyP8Dve75ClBJFGVgpjME8SYl8ZE2u+bYiq5yCkQgF65wzmC0UuSRVkTfkvt2+yAbruJF9vqhYuQf4jlXNodwiL8lrDkU+yGWRH8kxB4kHSrxIMy9UVm4KdUBVSY4MBsq9zfMcGnSZ52tQgbYkyuef48E0uZVkRt4c+fq1dvMkVXoGc4EvSRTXPGYgZTCZPt93fjC1lScFmC3cRryldpqE8bKLB7OJ3MPBWVw7BlPr+WGrJ/xdQfWp0EEiXFEGA+vXizeLD6le3Jc8Jm+iLZKtn/UMptAOSTDzXq1zgfoIw+QAEl8yGPmZJPUhuBcyg+mevz5HbP+3vUgSgxGev+pTDEbiEjZbzoChLNjD+0Ecgm4vksBgvvP8lcfklRnM7isGI6xz5PciCe/jOCpSPJjxuJee/D6O7vmr/F4kzmDUDwxm0ofgPIw/LMZcGHnX7bL1Idj1z5q/0PUx0FUj7wzGndp3NVzTdbzJn/CDmVrnGIruWvJ7kXxf68cwMhjfGjAYa8BgfBrAtvWDgbW6jiFvxZhGvuNLutqWxRkMi8lLg+T2fjCa4jiO7Afj+6IfTM5C3m6E9avjdwxmcs9KgS9ZBl312Y4xGO9aMAYzm9H7NT4emR9MOAsYg7k+qK7OLmJ+MOVxQRNilABdZ8e9QRnMLgoYgzkuKUf0dzvGYMrjnDGYWUjHMH2JEDKY3c6iumZHxmBAgjIYC18ihLqG0Yxtw7k2GvarOdv5VNflMaMJFmT46AcDuhpZHQhj2FK2WcLnJvYOqKSOZAZT1363FwnR6KI+yGv1pN7JfjB15ggxtB1lkaW26BuCLFziEiAhM5giW0jxm5wsC6V3U7cMZoI3Te7PGfGDmWTh9HVlLUec2Iu0+Mhg3CkGM7UXqRqLF/5HMXnf/BGN6d+coT/i4B1QC3keZvskWdiX+Yd52JAYDN//umh9fgz5N6fbizRyhGZGbr62PpjIYMzDWtfOJDNjEtsIZ0wwCCBhZidHE2bVzA4hAbpPN5+MwdjZ3vRh1OszEpgrctX0S2HP6Tzc2BTORCSwPbLX9YrBGaUuMQHLxYRG09QFwpnYXm1MZDB2TlwTdDV96DH4aQnsh2cjgwFxw4R+NS06aV1cpWUw9qKy7D3ZmAbJ7ZRUrjnar1VV4T9gm+Jf+B89SdCihH/hpIoZ8HNFjVDIorJMvV1esdxUgpZRtfykYhLMuOd1QHlVK1GhRVy1khXLxIqidVetPV8JiKTN1UqqKpegreS5IeFXGAw/IVn147RjcHJYwhcnBgm/IPGxjn+Jw8HP8XP8HL95cPTC/UsIhyjSa4wE5sJhRzcP95xl4P0igBmVvyKpF++EW2ii8ui7gpQIiISNXDzoi1wZ96mZnJmmYYY6noEMM8i5xMRPRUqfvtWIj81+yzXJYF6L7Yk023ye78lpvkUGkyIYoXxkOU9gtTJ/gHky385rxkqe8+2NNJBhfifX+aJlMAl8hz81EpV07iEkyefIYLYNuS8WF1LO5yi43xYggeUm28WWStRELeYlOUMjoCqQuGK5L/KAOkGw2SKDwXIP2znCm4SxnT15budzaNBlAS3Zz7HcPM9BYuzgDOa49Q8Ha950e5GWQZQWdlJ1DOZgp4dZvOT28KnJjUNiL44lGo9oIy6t6FDoSReT93lQigMSlZZLvMrISFOtWHfvRar1PJ1rGbcRazDSikMcemprI142UZymZnpaMj+YiNTaPJ23DAZtz3uqp4dg5724jeiFAZX4wCWOUixIYS/SvVDGY/IK9nCrq9P5EAh7kQ6KuBeJ28N61b4ndNO+m5oxmNVoTF6ewNY5QwbjMnuYP5P8tBeJ7s+x27V6OMJghPf6fmAw4jug3riEIca97H1D3uNeehgK5e3d1MYIg3nbi8TiEDhfvJs6IxdT0vVCn6tb77r28SVusq7qRExemcGI76Ym0rPmNwaDKjU9g3l81pVxiWu/2Jvcx+EYlvxc3TB8mcFYAwajIbURGYwbOLIfDAaw7devjuL71sAPxtLa9SuLaaS7EoPRFccaMBjDGuxFwiL7vUgm1OF/+W7qolnRMaxFectg9gXVNYh21DckbhrmBxNFjMGkzYoxmDynDMbeNC2DiZgfzKwpGYPJc8Zg2EuEtoqVR5TB6F6TU13jnDGYHb4SCBlMBBKoa7LPGINBCfSDwVcCUQaT76iu+X5DY2ibec4YTN0kdAwbUTTJJfheJCNJDOl+RRbezU0pMpgsaodqy2CyzBH251jKtk6ltbqdZjNpDMdJ4kjxYLZJIfnB6IcsbNfqbAyHKCHer4tkK+0d1A5J2PqGbKiuuySZ0PUjC3/KewdH/WAyiYXLDMaU/GCEGNqaHJM3H+5Fcr7PYNx+f84vvRdp3Ecv7BkMczvkvzk7mYVLPnqu5KMn7JN0JV0f0l6kAW+yZRYux4NZ9Puutm2cn+69SNo4g4nxN0dX1gds+c5O17aOvlwxXn9y0m32DiiYh6+2jYM7ZO+70u1b2v2+6mwMB+jfpJuXopuHHRbOJ6Bx4PWK7pOM6fuuGIMxkDfZOlwEfLW4ufRst6JD1bc3dApiDAbnYfYzCgllx2CqwPZWbG7aXhylZTCoq2tPM5jLS60uYFddqgvjI5STVN1fSKgIZmAAhYETxmbaD/TvBT9ACayoSr1UvYR6aRNYTvb3cuEJWMeF13HpE2jZl0qlRV5aelPxBCi4ErAOoUViEZdPDEZ21ycDa34Mf3xmMEOiQgYJk9TmM5wZtnKydf8iBvM3OxL8q47/bl1l5f6rVR305Je6/h3XQoik2973nWdKW2cPTbrZqEMgHbQZFNFDne6VRnzfkFBHT34En5gex4gt6qabDsqI2Ia3UZi6/hIGo05KiH4wfS4yyDVVx2jLvpb4pSLTrUdexeJEmkVRLPbktFi8yAbBSAYnkGlskcFArgt8XdQgsWjIc7E4kxIlrmS9gFyPBYIROAGCy0XLYKDcxWJJqnRxJKeiuJByu1hs1+RIGQzmOhRUIoNyIVdJnlgHZTBrskYJD+s4Q+NSlZV7gCKxqu2KqKxcKHIDjQMVjrS9kGEx7gez3p9Jtd9fyOsKx4tU63VFzsc1IXf4vlbJ7XqCXNcnqa7r9foG59dtrhd8X8Pv/vVakef1TsgJJODPc00lzphrfUWJaycBObAqKJdK3JnEDXKpbblXrIqVC7loq0AQG3RjZV1ZVfD5irnWbbMh14XlWmNVE8f4aBEzjI5I4fP76HkrYnJgiT/7b+WOVvSx2Z+mND5piGiY9Hy4nRW6E9IM1KXxf0g7PQhRpPpphPQzTf+3j1PVe9qpYhP4TNbT5f47n4v6+bK70v/Fv2g/x8/xc/wcP8fP8XP8w8f/Ac53B/Z2gBV2AAAAAElFTkSuQmCC') no-repeat center center fixed !important; 
                background-size: cover !important;
            }}
            
            /* 3. Ensure the Streamlit App container is fully hidden and positioned */
            .stApp {{
                background-color: transparent !important; /* Ensure the body background shows through */
                width: 100vw; 
                height: 100vh;
                position: fixed;
                top: 0;
                left: 0;
            }}
            
            /* 4. Hide all regular Streamlit content */
            .stApp > header, .stApp > section,
            [data-testid="stAppViewBlockContainer"] > div {{
                 display: none !important;
            }}
            
            /* 5. CSS for the standalone, non-shaking text */
            #jumpscare-text {{
                position: fixed;
                top: 90%;
                left: 50%;
                transform: translate(-50%, -50%);
                font-size: 3rem;
                font-weight: bold;
                color: white;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
                z-index: 1000000;
                /* Ensure this element does NOT shake by not giving it the 'shake' animation */
            }}
            </style>
            
            <div id="jumpscare-text">you cannot play as me you cannot play as me you cannot play as me you cannot play as me you cannot play as me you cannot play as me sorry</div>

            """, 
            unsafe_allow_html=True
        )
        st.stop()
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
                        break
        
        if len(current_answers) == len(QUESTIONS):
            
            if st.session_state.is_duplicate_name:
                st.warning("it's almost like you already knew the questions...")
                st.image("sansnoeyes.png", caption="you can't understand how this feels. knowing that one day, without warning, it's all going to be reset.")

            if st.session_state.submission_processed:
                st.session_state.submission_processed = False
            
                counts = score_answers(current_answers)
                house, tied = determine_house(counts)
                house = random.choice(tied) if len(tied) > 1 else tied[0]
                
                result = {"name": name, "house": house, "timestamp": datetime.now()}
                df_result = pd.DataFrame([result])
            
                current_results_df = pd.read_csv("results.csv")
                new_results_df = pd.concat([current_results_df, df_result], ignore_index=True)
                new_results_df.to_csv("results.csv", index=False)

            with st.spinner('The Sorting Hat is deciding...'):
                time.sleep(2)

            if not st.session_state.balloons_shown:
                st.balloons()
                st.session_state.balloons_shown = True

            counts = score_answers(current_answers)
            house, tied = determine_house(counts)
            
            house_colors = {
                "Gryffindor": "#7F0909",
                "Slytherin": "#1A472A",
                "Ravenclaw": "#0E1A40",
                "Hufflepuff": "#B8860B",
                "Neutral": "#CD5C5C"
            }

            bg_color = house_colors.get(house, "#CD5C5C")
            st.markdown(
                f"""
                <style>
                .stApp {{
                    background-color: {bg_color};
                    transition: background-color 1s;
                }}
                </style>
                """,
                unsafe_allow_html=True
            )
            
            st.markdown(
                f"""
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
                """,
                unsafe_allow_html=True
            )
            
            # Display certificate image and download button
            if house in CERTIFICATE_IMAGES:
                certificate_file = CERTIFICATE_IMAGES[house]
                try:
                    st.markdown(
                        """
                        <div style="
                            background: linear-gradient(135deg, #f8f4e5, #e8e0c4);
                            border: 3px solid #5a4633;
                            border-radius: 20px;
                            padding: 20px;
                            margin-top: 20px;
                            box-shadow: 6px 6px 12px rgba(0,0,0,0.25);
                            text-align: center;
                        ">
                            <h2 style="color:#3e2723; font-family: 'Georgia';">Your Official House Certificate</h2>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    col_left_spacer, col_image, col_right_spacer = st.columns([1, 3, 1])
                    with col_image:
                        st.image(certificate_file, caption=f"Official {house} Certificate", use_container_width=True)
                    
                    # Move the download button to a new block below the columns
                    st.markdown("---") # Add a separator for better layout
                    
                    pdf_buffer = create_certificate_pdf(name, house, certificate_file)
                    st.download_button(
                        label="Download Certificate (With your name in it!)",
                        data=pdf_buffer,
                        file_name=f"{name}_{house}_Certificate.pdf",
                        mime="application/pdf",
                        help="Download your official Hogwarts House Certificate with your name in it as a PDF!"
                    )
                except FileNotFoundError:
                    st.warning(f"Certificate image '{certificate_file}' not found. Please make sure the image file is in the correct directory.")
                except Exception as e:
                    st.error(f"Error loading certificate: {str(e)}")
            
            if len(tied) > 1:
                tied_houses_str = ", ".join(tied[:-1])
                if len(tied) > 2:
                    tied_houses_str += ","
                tied_houses_str += f" and {tied[-1]}"
                st.info(f"The sorting hat found a tie between {tied_houses_str} before making a final decision.")

            df_scores_chart = pd.DataFrame({
                "House": counts.keys(),
                "Points": counts.values()
            })
            
            st.markdown(
                """
                <div style="
                    background: linear-gradient(135deg, #f8f4e5, #e8e0c4);
                    border: 3px solid #5a4633;
                    border-radius: 20px;
                    padding: 20px;
                    margin-top: 30px;
                    box-shadow: 6px 6px 12px rgba(0,0,0,0.25);
                    text-align: center;
                ">
                    <h2 style="color:#3e2723; font-family: 'Georgia';">Your Point Distribution</h2>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            house_color_map = {
                "Gryffindor": "#7F0909",
                "Slytherin": "#1A472A",
                "Ravenclaw": "#0E1A40",
                "Hufflepuff": "#FFD700"
            }
            
            total_points = df_scores_chart['Points'].sum()
            df_scores_chart['Percentage'] = (df_scores_chart['Points'] / total_points) * 100
            
            base_chart = alt.Chart(df_scores_chart).encode(
                theta=alt.Theta("Points:Q", stack=True),
                color=alt.Color(
                    "House:N",
                    scale=alt.Scale(
                        domain=list(house_color_map.keys()),
                        range=list(house_color_map.values())
                    ),
                    legend=None
                ),
                tooltip=["House", "Points"]
            )
            
            pie = base_chart.mark_arc(outerRadius=120).encode(
                tooltip=["House", "Points", alt.Tooltip("Percentage", format=".1f", title="Percentage")]
            )
            
            text = base_chart.mark_text(radius=140).encode(
                text=alt.Text("Percentage", format=".1f"),
                order=alt.Order("Points", sort="descending"),
                color=alt.value("black")
            )
            
            combined_chart = (pie + text).properties(
                title="Your Personal House Points Distribution"
            ).interactive()
            
            st.altair_chart(combined_chart, use_container_width=True)

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
                <p class="credit-role">Certificate Design</p>
                <p class="credit-name">Sara</p>
            </div>
            <div class="credit-line">
                <p class="credit-role">Mischief Managed. See you on Monday =)</p>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
