# Introduction
An AI agent that uses a minimax alpha-beta pruning algorithm to play checkers. Uses a bitboard representation for the pieces to quickly and efficiently generate moves. The board is assumed to be 8x8, and a player must make a jump (or consecutive jumps) if one is available. The "callibrate.py" program outputs a text file "callibrate.txt", which the main program uses to determine how many moves forward the agent should look given the amount of time available.

# Technologies
Python 3.7.4

# Launch
Import the files into a directory that contains a text file "input.txt" that contains information about the board. The text file should be formatted like so:  
The first line should be "SINGLE" or "GAME".  
The next should be "BLACK" or "WHITE", depending on who's turn it is to make a move.  
The next line contains the float value representing the number of seconds the agent has to submit an action.  
The next 8 lines should each be 8 characters long. This represents the board. The "." symbol represents an empty space and the "w" and "b" characters represent a white and black piece, respectively. If the character is capitalized, then it is a king piece.  
  
Run the "callibrate.py" program with no input parameters. Then run the "main.py" file with no input parameters.
