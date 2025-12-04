import streamlit as st
from GUI.board import Board

st.set_page_config(page_title="Skyscrapers Puzzle", layout="centered")

st.title("Skyscrapers Puzzle Input Grid")
st.subheader("Choose board size")

board = Board()
board.interface()