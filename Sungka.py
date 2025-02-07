import streamlit as st
import numpy as np
import time
import random
from PIL import Image

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'home'
    st.session_state.players = []
    st.session_state.avatars = {}
    st.session_state.difficulty = None
    st.session_state.board, st.session_state.ulo_p1, st.session_state.ulo_p2 = [7] * 10, 0, 0
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
    st.markdown('<p class="big-font">SUNGKA GAME V1.0</p>', unsafe_allow_html=True)

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
    st.session_state.board = [7] * 5 + [0] + [7] * 5 + [0]
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
if 'ulo_p1' not in st.session_state:
    st.session_state.ulo_p1 = 0
if 'ulo_p2' not in st.session_state:
    st.session_state.ulo_p2 = 0
if 'houses_p1' not in st.session_state:
    st.session_state.houses_p1 = [7, 7, 7, 7, 7]  # Player 1's houses
if 'houses_p2' not in st.session_state:
    st.session_state.houses_p2 = [7, 7, 7, 7, 7]  # Player 2's houses
if 'game_mode' not in st.session_state:  # Add game mode (1 player or 2 player)
    st.session_state.game_mode = "2 Player"  # Default is 2 Player

# Function to distribute marbles with animation
def distribute_marbles(player, house_choice):
    if player == 'Player 1':
        houses = st.session_state.houses_p1
        opponent_houses = st.session_state.houses_p2
        player_head = st.session_state.ulo_p1
        opponent_head = st.session_state.ulo_p2
    else:
        houses = st.session_state.houses_p2
        opponent_houses = st.session_state.houses_p1
        player_head = st.session_state.ulo_p2
        opponent_head = st.session_state.ulo_p1
    
    marbles_to_move = houses[house_choice - 1]
    houses[house_choice - 1] = 0
    current_index = house_choice - 1

    while marbles_to_move > 0:
        current_index = (current_index + 1) % 10
        if player == 'Player 1' and current_index == 9:
            continue
        elif player == 'Player 2' and current_index == 4:
            continue
        
        # Highlight the house while distributing
        if current_index < 5:
            houses[current_index] += 1
            st.session_state.houses_p1 = houses  # Update Player 1's houses
        elif current_index == 5:
            player_head += 1
        else:
            opponent_houses[current_index - 6] += 1

        # Animate the shell move with a short pause
        time.sleep(0.5)  # Adjust the sleep time for animation speed
        
        # Highlight the house (temporarily turn red and then back to black)
        st.write(f"<div style='color: red;'>House {current_index + 1}</div>", unsafe_allow_html=True)

        marbles_to_move -= 1
    
    if player == 'Player 1':
        st.session_state.ulo_p1 = player_head
    else:
        st.session_state.ulo_p2 = player_head

# Function for bot's automatic move (Player 2)
def bot_move():
    house_choice = random.randint(1, 5)  # Bot chooses a random house
    st.write(f"Bot selects House {house_choice} and moves the marbles...")
    distribute_marbles('Player 2', house_choice)  # Bot's marbles move logic
    st.write(f"Updated P2 Houses: {st.session_state.houses_p2}")
    st.write(f"Updated P2 Head: {st.session_state.ulo_p2}")

# Player's turn handling
def game_page():
    st.title("Sungka Game")

    # Display Round Announcement
    st.markdown(f"<h1 style='text-align: center; color: red;'>Round {st.session_state.round}</h1>", unsafe_allow_html=True)
    time.sleep(2)

    # Show avatars and names in two columns
    cols = st.columns(2)
    for i, player in enumerate(st.session_state.players):
        with cols[i]:
            st.image(st.session_state.avatars.get(player, ""), width=200)
            st.write(player)

    # Display game board with dynamic input for houses
    st.write("Game Board:") 
    
    # P1 House Display
    board_cols = st.columns(5)
    for i in range(5):
        with board_cols[i]:
            st.text_input(f"P1 House {i+1}", value=st.session_state.houses_p1[i], key=f"p1_house_{i}", disabled=True)
    st.text_input("P1 Head", value=st.session_state.ulo_p1, key="p1_head", help="Accumulated Marbles", disabled=True)
    
    # P2 House Display
    board_cols2 = st.columns(5)
    for i in range(5):
        with board_cols2[i]:
            st.text_input(f"P2 House {i+1}", value=st.session_state.houses_p2[i], key=f"p2_house_{i}", disabled=True)
    st.text_input("P2 Head", value=st.session_state.ulo_p2, key="p2_head", help="Accumulated Marbles", disabled=True)

    # Avatar image for hand animation
    st.image("Hand.gif", width=100)

    # Player's turn handling
    if st.session_state.round <= 5:
        # Player 1's turn
        if st.session_state.round % 2 != 0:
            house_choice = st.selectbox("Choose a house to pick from (Player 1)", [1, 2, 3, 4, 5])
            if st.button("Make Move (Player 1)"):
                st.write(f"Player 1 selects House {house_choice} and moves the marbles...")

                # Distribute marbles for Player 1
                distribute_marbles('Player 1', house_choice)

                # After updating Player 1's move, display the updated board
                st.write(f"Updated P1 Houses: {st.session_state.houses_p1}")
                st.write(f"Updated P1 Head: {st.session_state.ulo_p1}")

                # Proceed to the next round
                st.session_state.round += 1

                # If game is in 1 Player mode, automatically make the bot's move
                if st.session_state.game_mode == "1 Player":
                    bot_move()

        # Player 2's turn (Bot's turn in 1 Player Mode)
        elif st.session_state.round % 2 == 0:
            if st.session_state.game_mode == "1 Player":
                # Automatically move the bot
                bot_move()
            else:
                house_choice_p2 = st.selectbox("Choose a house to pick from (Player 2)", [1, 2, 3, 4, 5])
                if st.button("Make Move (Player 2)"):
                    st.write(f"Player 2 selects House {house_choice_p2} and moves the marbles...")

                    # Distribute marbles for Player 2
                    distribute_marbles('Player 2', house_choice_p2)

                    # After updating Player 2's move, display the updated board
                    st.write(f"Updated P2 Houses: {st.session_state.houses_p2}")
                    st.write(f"Updated P2 Head: {st.session_state.ulo_p2}")

                    # Proceed to the next round
                    st.session_state.round += 1

    # End game after 5 rounds
    if st.session_state.round > 5:
        st.session_state.page = 'game_over'
        st.write("Game Over! Final Scores:")
        st.write(f"Player 1: {st.session_state.ulo_p1} marbles")
        st.write(f"Player 2: {st.session_state.ulo_p2} marbles")
        if st.session_state.ulo_p1 > st.session_state.ulo_p2:
            st.write("Player 1 wins!")
        elif st.session_state.ulo_p2 > st.session_state.ulo_p1:
            st.write("Player 2 wins!")
        else:
            st.write("It's a tie!")

# Bot move handling (for 1 Player mode)
def bot_move():
    st.write("Bot's turn...")
    
    # Simulate the bot's move: randomly select a house
    house_choice_bot = random.choice([1, 2, 3, 4, 5])
    st.write(f"Bot selects House {house_choice_bot} and moves the marbles...")

    # Distribute marbles for the Bot (Player 2)
    distribute_marbles('Player 2', house_choice_bot)

    # After updating the Bot's move, display the updated board
    st.write(f"Updated P2 Houses: {st.session_state.houses_p2}")
    st.write(f"Updated P2 Head: {st.session_state.ulo_p2}")

    # Proceed to the next round
    st.session_state.round += 1
# Game Over Page
def game_over_page():
    st.title("Game Over")
    winner = max(st.session_state.players, key=lambda p: st.session_state.ulo_p1 if p == st.session_state.players[0] else st.session_state.ulo_p2)
    st.markdown(f"<h1 style='text-align: center; color: green;'>Game Over</h1>", unsafe_allow_html=True)
    time.sleep(2)
    st.markdown(f"<h2 style='text-align: center;'>Winner: {winner}</h2>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center;'>Points: {st.session_state.ulo_p1 if winner == st.session_state.players[0] else st.session_state.ulo_p2}</h3>", unsafe_allow_html=True)
    if st.button("Play Again"):
        st.session_state.page = 'home'

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
    st.write(f"{st.session_state.names['Player 1']}: {st.session_state.scores['Player 1']} points")
    st.write(f"{st.session_state.names['Player 2']}: {st.session_state.scores['Player 2']} points")
    
    if st.button("Restart Game"):
        reset_board()
        navigate_to('home')
