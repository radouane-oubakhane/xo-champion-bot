import discord
from discord.ext import commands
from discord import app_commands
import random
import os
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Game state and scoring
games = {}
scores = {}

# Minimax algorithm for AI
def minimax(board, depth, is_maximizing, ai_mark, player_mark):
    winner, _ = check_winner(board)
    if winner == player_mark:
        return -1
    elif winner == ai_mark:
        return 1
    elif is_board_full(board):
        return 0

    if is_maximizing:
        best_score = -float('inf')
        for i in range(9):
            if board[i] == " ":
                board[i] = ai_mark
                score = minimax(board, depth + 1, False, ai_mark, player_mark)
                board[i] = " "
                best_score = max(score, best_score)
        return best_score
    else:
        best_score = float('inf')
        for i in range(9):
            if board[i] == " ":
                board[i] = player_mark
                score = minimax(board, depth + 1, True, ai_mark, player_mark)
                board[i] = " "
                best_score = min(score, best_score)
        return best_score

def best_move(board, ai_mark, player_mark):
    best_score = -float('inf')
    move = 0
    for i in range(9):
        if board[i] == " ":
            board[i] = ai_mark
            score = minimax(board, 0, False, ai_mark, player_mark)
            board[i] = " "
            if score > best_score:
                best_score = score
                move = i
    return move

def check_winner(board):
    win_conditions = [(0, 1, 2), (3, 4, 5), (6, 7, 8),
                      (0, 3, 6), (1, 4, 7), (2, 5, 8),
                      (0, 4, 8), (2, 4, 6)]
    for condition in win_conditions:
        if board[condition[0]] == board[condition[1]] == board[condition[2]] != " ":
            return board[condition[0]], condition
    return None, None

def is_board_full(board):
    return " " not in board

def display_board(board):
    return f"{board[0]} | {board[1]} | {board[2]}\n---------\n{board[3]} | {board[4]} | {board[5]}\n---------\n{board[6]} | {board[7]} | {board[8]}"

def generate_board_image(board, winning_condition=None, winner=None):
    # Create a blank image with white background
    img = Image.new('RGB', (300, 300), color='white')
    draw = ImageDraw.Draw(img)
    
    # Load a larger font
    font = ImageFont.truetype("arial.ttf", 40)  # Ensure you have the Arial font available

    # Draw the grid
    for i in range(1, 3):
        draw.line((100 * i, 0, 100 * i, 300), fill='black', width=3)
        draw.line((0, 100 * i, 300, 100 * i), fill='black', width=3)

    # Draw the X and O marks and numbers
    for i in range(9):
        x = (i % 3) * 100 + 50
        y = (i // 3) * 100 + 50
        if board[i] == 'X':
            draw.text((x, y), 'X', fill='blue', anchor='mm', font=font)
        elif board[i] == 'O':
            draw.text((x, y), 'O', fill='red', anchor='mm', font=font)
        else:
            draw.text((x, y), str(i + 1), fill='gray', anchor='mm', font=font)

    # Draw the winning line if there is a winner
    if winning_condition and winner:
        color = 'blue' if winner == 'X' else 'red'
        start = ((winning_condition[0] % 3) * 100 + 50, (winning_condition[0] // 3) * 100 + 50)
        end = ((winning_condition[2] % 3) * 100 + 50, (winning_condition[2] // 3) * 100 + 50)
        draw.line([start, end], fill=color, width=5)

    # Save the image to a file
    img.save('board.png')

def generate_result_image(winner):
    # Create a blank square image with white background
    img = Image.new('RGB', (300, 300), color='white')
    draw = ImageDraw.Draw(img)
    
    # Load a larger font
    font = ImageFont.truetype("arial.ttf", 60)  # Ensure you have the Arial font available

    # Draw the result text
    text = f"{winner} Wins!"
    color = 'blue' if winner == 'X' else 'red'
    draw.text((150, 150), text, fill=color, anchor='mm', font=font)

    # Save the image to a file
    img.save('result.png')

def generate_draw_image():
    # Create a blank square image with white background
    img = Image.new('RGB', (300, 300), color='white')
    draw = ImageDraw.Draw(img)
    
    # Load a larger font
    font = ImageFont.truetype("arial.ttf", 60)  # Ensure you have the Arial font available

    # Draw the draw text
    text = "It's a Draw!"
    draw.text((150, 150), text, fill='gray', anchor='mm', font=font)

    # Save the image to a file
    img.save('draw.png')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await bot.tree.sync()

@bot.tree.command(name="start", description="Start a new Tic-Tac-Toe game")
async def start(interaction: discord.Interaction):
    user = interaction.user
    if user.id in games:
        await interaction.response.send_message("You already have a game in progress!", ephemeral=True)
        return

    board = [" "] * 9
    games[user.id] = board

    # Randomly choose who plays as X and who plays as O
    player_mark = random.choice(['X', 'O'])
    ai_mark = 'O' if player_mark == 'X' else 'X'
    games[user.id] = {'board': board, 'player_mark': player_mark, 'ai_mark': ai_mark}

    # Randomly decide who starts
    if random.choice([True, False]):
        ai_move = best_move(board, ai_mark, player_mark)
        board[ai_move] = ai_mark

    generate_board_image(board)
    await interaction.response.send_message(file=discord.File('board.png'), content=f"New game started! You are {player_mark}. Your move! Use /move <position> to make a move (1-9).")

@bot.tree.command(name="move", description="Make a move in your Tic-Tac-Toe game")
@app_commands.describe(position="Position to place your mark (1-9)")
async def move(interaction: discord.Interaction, position: int):
    user = interaction.user
    if user.id not in games:
        await interaction.response.send_message("You don't have a game in progress! Use /start to begin a new game.", ephemeral=True)
        return

    game = games[user.id]
    board = game['board']
    player_mark = game['player_mark']
    ai_mark = game['ai_mark']
    pos = position - 1
    if board[pos] != " ":
        await interaction.response.send_message("Invalid move! That spot is already taken.", ephemeral=True)
        return

    board[pos] = player_mark
    winner, winning_condition = check_winner(board)
    if winner:
        generate_board_image(board, winning_condition, winner)
        await interaction.response.send_message(file=discord.File('board.png'), content="You win!")
        generate_result_image(winner)
        await interaction.followup.send(file=discord.File('result.png'))
        del games[user.id]
        scores[user.id] = scores.get(user.id, 0) + 1
        return
    elif is_board_full(board):
        generate_board_image(board)
        await interaction.response.send_message(file=discord.File('board.png'), content="It's a draw!")
        generate_draw_image()
        await interaction.followup.send(file=discord.File('draw.png'))
        del games[user.id]
        return

    ai_move = best_move(board, ai_mark, player_mark)
    board[ai_move] = ai_mark
    winner, winning_condition = check_winner(board)
    if winner:
        generate_board_image(board, winning_condition, winner)
        await interaction.response.send_message(file=discord.File('board.png'), content="You lose!")
        generate_result_image(winner)
        await interaction.followup.send(file=discord.File('result.png'))
        del games[user.id]
        return
    elif is_board_full(board):
        generate_board_image(board)
        await interaction.response.send_message(file=discord.File('board.png'), content="It's a draw!")
        generate_draw_image()
        await interaction.followup.send(file=discord.File('draw.png'))
        del games[user.id]
        return

    generate_board_image(board)
    await interaction.response.send_message(file=discord.File('board.png'), content="Your move!")

@bot.tree.command(name="leaderboard", description="View the Tic-Tac-Toe leaderboard")
async def leaderboard(interaction: discord.Interaction):
    leaderboard = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    message = "Leaderboard:\n"
    for user_id, score in leaderboard:
        user = await bot.fetch_user(user_id)
        message += f"{user.name}: {score}\n"
    await interaction.response.send_message(message)

@bot.tree.command(name="reset", description="Reset your Tic-Tac-Toe game")
async def reset(interaction: discord.Interaction):
    user = interaction.user
    if user.id in games:
        del games[user.id]
        await interaction.response.send_message("Your game has been reset.", ephemeral=True)
    else:
        await interaction.response.send_message("You don't have a game in progress!", ephemeral=True)

bot.run(TOKEN)