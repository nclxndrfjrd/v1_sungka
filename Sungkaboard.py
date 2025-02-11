import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as patches
import time
import random
from PIL import Image


# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'home'
    st.session_state.players = []
    st.session_state.avatars = {}
    st.session_state.difficulty = None
if 'houses' not in st.session_state:
    st.session_state.houses = [0, 7, 7, 7, 7, 7,  # P1 Head (index 0) + P1 Houses (1-5)
                            0,                 # P2 Head (index 6)
                            7, 7, 7, 7, 7,     # P2 Houses (7-11)
                            0]                 # P1 Head (index 12)
    st.session_state.current_player = 1
    st.session_state.round = 1

def navigate_to(page):
    st.session_state.page = page
# Load background image
bg_image = Image.open('BG.jpg')
# Set background color and adjust the general look using Python
st.markdown("""
    <style>
        body {
            background-color: #F8E7F6;
        }
        .big-font {
            font-size: 40px !important;
            font-family: 'Courier', monospace;
            color: #4B164C;
            text-align: center;
        }
        .button-style {
            background-color: #DD88CF;
            color: white;
            font-size: 18px;
            padding: 15px 50px;
            border-radius: 10px;
            font-family: 'Courier', monospace;
        }
        /* Sidebar background color */
        .sidebar .sidebar-content {
            background-color: #DD88CF;
        }
    </style>
""", unsafe_allow_html=True)

# Home Page
def home_page():
    col1, col2, col3 = st.columns([1, 2, 1])  # Middle column is wider
    with col2:
        st.title("Sungka Game")

    # Add a Start Game button with custom style
    if st.button("Start Game", key="start_game", help="Click to start the game", use_container_width=True):
        st.session_state.page = 'player_setup'

# Sidebar Navigation (appears after clicking Start)
if st.session_state.page != 'home':
    with st.sidebar:
        st.button("Home", on_click=lambda: navigate_to('home'))
        st.button("Game Options", on_click=lambda: navigate_to('player_setup'))
        st.button("Game Mechanics", on_click=lambda: navigate_to('game_mechanics'))
        st.button("Game", on_click=lambda: navigate_to('game'))
        st.button("Leaderboard", on_click=lambda: navigate_to('leaderboard'))

# Function to reset the board for a new game
def reset_board():
    st.session_state.houses = [0, 7, 7, 7, 7, 7,  # P1 Head (index 0) + P1 Houses (1-5)
                            0,                 # P2 Head (index 6)
                            7, 7, 7, 7, 7,     # P2 Houses (7-11)
                            0]                 # P1 Head (index 12)
    st.session_state.round = 1
    st.session_state.scores = {"Player 1": 0, "Player 2": 0}

def player_setup_page():
    st.title("Player Setup")

    # Select number of players
    num_players = st.radio("How many players?", [1, 2])

    # Assign player names
    player1_name = st.text_input("Player 1 Name:", "")

    if num_players == 1:
        st.session_state.players = [player1_name if player1_name else "Player 1", "Bot"]
        # Set the game mode to "1 Player"
        st.session_state.game_mode = "1 Player"
    else:
        player2_name = st.text_input("Player 2 Name:", "")
        st.session_state.players = [
            player1_name if player1_name else "Player 1", 
            player2_name if player2_name else "Player 2"
        ]
        # Set the game mode to "2 Player"
        st.session_state.game_mode = "2 Player"

    # Ensure avatars exist in session state
    if "avatars" not in st.session_state:
        st.session_state.avatars = {}

    avatar_choices = [f"AV{i+1}.gif" for i in range(9)]  # 9 avatars available

    # Avatar Selection
    for player in st.session_state.players:
        if player == "Bot":
            st.session_state.avatars[player] = "AV2.gif"  # Default bot avatar
            continue  # Skip selection for bot

        st.write(f"Choose an avatar for {player}")
        cols = st.columns(len(avatar_choices))

        for i, avatar in enumerate(avatar_choices):
            with cols[i]:
                if st.button(
                    "✔" if st.session_state.avatars.get(player) == avatar else " ",
                    key=f"{player}_avatar_{i}"
                ):
                    st.session_state.avatars[player] = avatar
                st.image(avatar, width=100)

    if st.button("Next"):
        st.session_state.page = 'difficulty_selection'

# Difficulty Selection Page
def difficulty_selection_page():
    st.title("Select Difficulty")
    difficulty = st.radio("Choose Difficulty", ["Easy", "Medium", "Hard"])
    if st.button("Start Math Challenge"):
        st.session_state.difficulty = difficulty
        st.session_state.page = 'math_challenge'

# Math Challenge Page
def math_challenge_page():
    st.title("Math Challenge")
    st.write("Solve the function to determine who goes first!")

    # Ensure the question is generated only once
    if 'question_generated' not in st.session_state:
        # Get difficulty level
        difficulty = st.session_state.difficulty
        x_value = np.random.randint(1, 6)  # Ensure x is always between 1-5

        # Generate function & correct answer
        if difficulty == "Easy":
            constant = np.random.randint(-4, 5)  # Keep within reasonable range
            problem = rf"f(x) = x + {constant}"
            correct_answer = x_value + constant

        elif difficulty == "Medium":
            b = np.random.randint(-5, 6)
            problem = rf"f(x) = x^2 + {b}x"
            correct_answer = (x_value**2) + (b * x_value)

        else:  # Hard (Quadratic with roots in 1-5)
            root1, root2 = np.random.choice(range(1, 6), 2, replace=False)
            a = np.random.randint(1, 3)  # Keep coefficient small
            problem = rf"f(x) = {a}(x - {root1})(x - {root2})"
            correct_answer = a * (x_value - root1) * (x_value - root2)

        # Store the generated question and correct answer in session state
        st.session_state.problem = problem
        st.session_state.correct_answer = correct_answer
        st.session_state.x_value = x_value
        st.session_state.question_generated = True

    # Display the function and x_value
    st.latex(st.session_state.problem)
    st.latex(f"\\text{{Solve for }} f({st.session_state.x_value})")

    # Player answers
    player_answers = {}
    for player in st.session_state.players:
        if player == "Bot":
            player_answers[player] = None  # Bot doesn't answer
        else:
            # Use text input to allow any number and convert it to a float
            answer_input = st.text_input(f"{player}'s Answer", key=f"{player}_answer")
            try:
                player_answers[player] = float(answer_input)  # Convert input to a float
            except ValueError:
                player_answers[player] = None  # If input is not a valid number, set it to None

    # Check answers
    if st.button("Submit Answers"):
        correct_players = [p for p in st.session_state.players if player_answers.get(p) == st.session_state.correct_answer]

        # Show correct answer
        st.write(f"✅ The correct answer is **{st.session_state.correct_answer}**!")

        # Display results
        for player, answer in player_answers.items():
            if player == "Bot":
                st.write(f"🤖 {player} is a bot and does not answer.")
            elif answer == st.session_state.correct_answer:
                st.write(f"✅ {player} answered **correctly!**")
            else:
                st.write(f"❌ {player} answered **incorrectly!** (Their answer: {answer})")

        # Determine who goes first
        if correct_players:
            first_turn = random.choice(correct_players)
            st.write(f"🎉 **{first_turn} goes first!**")
            st.session_state.first_turn = first_turn
        else:
            st.write("⚠️ No one got the correct answer. Choosing randomly...")
            first_turn = random.choice(st.session_state.players)
            st.session_state.first_turn = first_turn
            st.write(f"🎲 **{first_turn} goes first!**")

        st.session_state.page = 'game'  # Proceed to the game phase

# Game Mechanics
if st.session_state.page == 'game_mechanics':
    st.header("Game Mechanics")
    st.write(""" 
    - The Sungka board has 10 holes: 5 for Player 1 and 5 for Player 2.
    - Each player has a house at the end of the board for collecting marbles.
    - Players start with 7 marbles in each pit.
    - Players take turns selecting a pit and distributing marbles.
    - The player with the most marbles in their head wins after 5 rounds.
    """)
    
    if st.button("Next", key="mechanics_next"):
        navigate_to('game')



    # Initialize game state
    if 'round' not in st.session_state:
        st.session_state.round = 1
    if 'players' not in st.session_state:
        st.session_state.players = ['Player 1', 'Player 2']
    if 'avatars' not in st.session_state:
        st.session_state.avatars = {'Player 1': 'AV1.gif', 'Player 2': 'AV2.gif'}
    if 'game_mode' not in st.session_state:  # Add game mode (1 player or 2 player)
        st.session_state.game_mode = "2 Player"  # Default is 2 Player

# Function to draw the Sungka board
def draw_sungka_board():
    fig, ax = plt.subplots(figsize=(10, 5))
    
    board_color = "#8B4513"
    ulo_color = "#00008B"
    house_color = "#87CEEB"
    pebble_color = "black"

    # Define house and ulo indexes for easier handling
    P1_HOUSES = [5, 4, 3, 2, 1]  # Player 1 Houses (Top row, left to right)
    P2_HOUSES = [7, 8, 9, 10, 11]  # Player 2 Houses (Bottom row, left to right)
    P1_ULO = 6  # Player 1's ulo (left head)
    P2_ULO = 12  # Player 2's ulo (right head)

    ax.add_patch(patches.FancyBboxPatch((-6.5, -2), 13, 4, boxstyle="round,pad=0.2", color=board_color, ec="black", lw=2))

    # Player 1 ULO (left side)
    ax.add_patch(patches.Ellipse((-5.5, 0), 1.5, 2.5, color=ulo_color, ec="black", lw=2, zorder=1))
    ax.text(-5.5, 0, str(st.session_state.houses[P1_ULO]), fontsize=14, ha='center', va='center', 
            color='white', bbox=dict(facecolor='red', edgecolor='black', boxstyle='round,pad=0.3'))

    # Player 2 ULO (right side)
    ax.add_patch(patches.Ellipse((5.5, 0), 1.5, 2.5, color=ulo_color, ec="black", lw=2, zorder=1))
    ax.text(5.5, 0, str(st.session_state.houses[P2_ULO]), fontsize=14, ha='center', va='center', 
            color='white', bbox=dict(facecolor='red', edgecolor='black', boxstyle='round,pad=0.3'))

    # Player 1 Houses (Top Row)
    positions_top = [-4, -2, 0, 2, 4]
    for i, x in zip(P1_HOUSES, positions_top):
        ax.add_patch(patches.Circle((x, 1), 0.8, color=house_color, ec="black", lw=2, zorder=2))
        ax.text(x, 2.2, str(st.session_state.houses[i]), fontsize=12, ha='center', va='center',
                color='white', bbox=dict(facecolor='red', edgecolor='black', boxstyle='round,pad=0.3'))

    # Player 2 Houses (Bottom Row)
    positions_bottom = [-4, -2, 0, 2, 4]
    for i, x in zip(P2_HOUSES, positions_bottom):
        ax.add_patch(patches.Circle((x, -1), 0.8, color=house_color, ec="black", lw=2, zorder=2))
        ax.text(x, -2.2, str(st.session_state.houses[i]), fontsize=12, ha='center', va='center',
                color='white', bbox=dict(facecolor='red', edgecolor='black', boxstyle='round,pad=0.3'))

    # Function to add pebbles
    def add_pebbles(x, y, count):
        for j in range(count):
            px = x + (j % 3 - 1) * 0.25
            py = y + (j // 3 - 0.5) * 0.25
            ax.add_patch(patches.Ellipse((px, py), 0.15, 0.2, color=pebble_color, zorder=3))

    # Add pebbles to each house
    for i, x in zip(P1_HOUSES, positions_top):
        add_pebbles(x, 1, st.session_state.houses[i])  # Player 1 houses
    for i, x in zip(P2_HOUSES, positions_bottom):
        add_pebbles(x, -1, st.session_state.houses[i])  # Player 2 houses


    ax.set_xlim(-8, 8)
    ax.set_ylim(-5, 5)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_frame_on(False)
    return fig


# Define House Indexes for Each Player
P1_HOUSES = [5, 4, 3, 2, 1]  # Player 1's Houses (left to right)
P2_HOUSES = [7, 8, 9, 10, 11]  # Player 2's Houses (right to left)

P1_ULO = 6  # Player 1's ulo (head)
P2_ULO = 12  # Player 2's ulo (head)

def move_pebbles(index):
    stones = st.session_state.houses[index]
    if stones == 0:
        return  # Ignore empty houses

    st.session_state.houses[index] = 0  # Remove stones from selected house
    pos = index  # Start placing pebbles from the next position

    while stones > 0:
        pos = (pos + 1) % 13  # Wrap around correctly (0-12)

        # Skip opponent's ulo
        if (st.session_state.current_player == 1 and pos == P2_ULO) or \
           (st.session_state.current_player == 2 and pos == P1_ULO):
            pos = (pos + 1) % 13  # Move past the ulo
            continue  

        st.session_state.houses[pos] += 1
        stones -= 1

    # **Extra Turn Rule**: If last stone lands in player's own ulo
    if (st.session_state.current_player == 1 and pos == P1_ULO) or \
       (st.session_state.current_player == 2 and pos == P2_ULO):
        return  # Player keeps turn

    # **Switch Turn**
    st.session_state.current_player = 3 - st.session_state.current_player
    st.session_state.round += 1
    
    # **Call bot_move() if it's a bot's turn**
    if st.session_state.current_player == 2 and st.session_state.players[1] == "Bot":
        bot_move()
    st.rerun()


def game_page():
    col1, col2, col3 = st.columns([1, 2, 1])  # Middle column is wider
    with col2:
        st.title("Sungka Game")

    # Display Round Announcement
    st.markdown(f"<h1 style='text-align: center; color: red;'>Round {st.session_state.round}</h1>", unsafe_allow_html=True)
    time.sleep(2)

    # Center Player 1 Above the Board
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(st.session_state.avatars.get(st.session_state.players[0], ""), width=250)
        st.subheader(st.session_state.players[0])

    # Display game board with dynamic input for houses
    st.write("Game Board:") 
    st.pyplot(draw_sungka_board())

  # **Render Buttons for Player Moves**
    cols = st.columns(5)

    for i in range(5):
        if st.session_state.current_player == 1:
            if cols[i].button(f"Move {i+1}", key=f"p1_{i}"):
                move_pebbles(P1_HOUSES[i])  # Uses the predefined house indexes
        else:
            if cols[i].button(f"Move {i+1}", key=f"p2_{i}"):
                move_pebbles(P2_HOUSES[i])  # Uses the predefined house indexes
    # Center Player 2 Below the Board
    col4, col5, col6 = st.columns([1, 2, 1])
    with col5:
        st.image(st.session_state.avatars.get(st.session_state.players[1], ""), width=250)
        st.subheader(st.session_state.players[1])

  

   # End game after 5 rounds
       # Fetch ulo (head) scores correctly
    p1_score = st.session_state.houses[P1_ULO]
    p2_score = st.session_state.houses[P2_ULO]

    if st.session_state.round > 5:
        st.session_state.page = 'game_over'
        st.write("Game Over! Final Scores:")
        st.write(f"Player 1: {p1_score} marbles")
        st.write(f"Player 2: {p2_score} marbles")
        if p1_score > p2_score:
            st.write("Player 1 wins!")
        elif p2_score> p1_score:
            st.write("Player 2 wins!")
        else:
            st.write("It's a tie!")

    # Bot move handling (for 1 Player mode)
def bot_move():
        st.write("Bot's turn...")

        # Select a non-empty house randomly from P2_HOUSES
        available_moves = [i for i in P2_HOUSES if st.session_state.houses[i] > 0]
        if available_moves:  # If there are valid moves
            house_choice_bot = random.choice(available_moves)  # Select randomly
            st.write(f"Bot selects House {house_choice_bot} and moves the marbles...")
            move_pebbles(house_choice_bot)
        else:
            st.write("Bot has no valid moves, skipping turn.")
        move_pebbles(house_choice_bot) 

        # After updating the Bot's move, display the updated board
        st.write(f"Updated P2 Houses: {st.session_state.P2_HOUSES}")
        st.write(f"Updated P2 Head: {st.session_state.P2_ULO}")

        # Proceed to the next round
        st.session_state.round += 1
        # Game Over Page


def game_over_page():
    st.title("Game Over")

    # Fetch ulo (head) scores correctly
    p1_score = st.session_state.houses[P1_ULO]
    p2_score = st.session_state.houses[P2_ULO]

    # Determine the winner based on ulo score
    if p1_score > p2_score:
        winner = st.session_state.players[0]  # Player 1
    elif p2_score > p1_score:
        winner = st.session_state.players[1]  # Player 2 / Bot
    else:
        winner = "It's a tie!"

    # Display game results
    st.markdown(f"<h1 style='text-align: center; color: green;'>Game Over</h1>", unsafe_allow_html=True)
    time.sleep(2)
    
    st.markdown(f"<h2 style='text-align: center;'>Winner: {winner}</h2>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center;'>Player 1: {p1_score} marbles</h3>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center;'>Player 2: {p2_score} marbles</h3>", unsafe_allow_html=True)

    # Play Again button
    if st.button("Play Again"):
        st.session_state.page = 'home'
        st.rerun()



# Page Navigation
if st.session_state.page == 'home':
    home_page()
elif st.session_state.page == 'player_setup':
    player_setup_page()
elif st.session_state.page == 'difficulty_selection':
    difficulty_selection_page()
elif st.session_state.page == 'math_challenge':
    math_challenge_page()
elif st.session_state.page == 'game':
    game_page()
elif st.session_state.page == 'game_over':
    game_over_page()
# Leaderboard
if st.session_state.page == 'leaderboard':
    st.header("Leaderboard")
    # Retrieve actual player names and scores from session state
    player1_name = st.session_state.players[0]
    player2_name = st.session_state.players[1]
    p1_score = st.session_state.houses[P1_ULO]  # Get Player 1's ulo (head)
    p2_score = st.session_state.houses[P2_ULO]  # Get Player 2's ulo (head)

    # Display Corrected Scores
    st.write(f"**{player1_name}:** {p1_score} points")
    st.write(f"**{player2_name}:** {p2_score} points")

    # Restart Game Button
    if st.button("Restart Game"):
        reset_board()
        navigate_to('home')