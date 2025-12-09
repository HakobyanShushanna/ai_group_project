import streamlit as st

from CluesGenerator.clues_generator import RandomPuzzleGenerator
from Controller.puzzle_manager import PuzzleManager
from Evaluations.evaluator import Evaluator
from GUI.board import Board

st.set_page_config(page_title="Skyscrapers Puzzle", layout="centered")

st.title("Skyscrapers Puzzle Input Grid")
st.subheader("Choose board size")

if __name__ == "__main__":
    # board = Board()
    # board.interface()
    #
    for i in range(4, 8):
        evaluator = Evaluator(i, 0.5)
        csp_mean, csp_sd, a_star_mean, a_star_sd, hill_mean, hill_sd = evaluator.evaluate_algorithms()

        print(f"==================== {i} x {i} GRID ====================")
        print("CSP mean: ", csp_mean, " | CSP sd: ", csp_sd)
        print("A* mean: ", a_star_mean, " | A* sd: ", a_star_sd)
        print("Hill Climbing mean: ", hill_mean, " | Hill Climbing sd: ", hill_sd)