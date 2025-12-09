import streamlit as st

from CluesGenerator.clues_generator import RandomPuzzleGenerator
from Controller.puzzle_manager import PuzzleManager

class Board:
    def __init__(self):
        self.n = st.number_input(
            "Grid size (n × n)",
            min_value=4,
            max_value=9,
            value=4,
            step=1,
            key="board_size",
        )

        st.session_state.setdefault("solution", {})
        st.session_state.setdefault("metrics", {})

    @staticmethod
    def __hard_reload():
        st.session_state["reload_trigger"] = st.session_state.get("reload_trigger", 0) + 1
        st.rerun()

    @staticmethod
    def __inject_solution():
        sol = st.session_state.get("solution", {})
        for (r, c), v in sol.items():
            st.session_state[f"cell_{r}_{c}"] = str(v)

    def interface(self):
        if st.session_state.get("force_reload"):
            del st.session_state["force_reload"]

            clues = st.session_state.get("generated_clues")
            if clues:
                n = self.n
                for i in range(n):
                    st.session_state[f"top_{i}"] = str(clues["top"][i])
                    st.session_state[f"bottom_{i}"] = str(clues["bottom"][i])
                    st.session_state[f"left_{i}"] = str(clues["left"][i])
                    st.session_state[f"right_{i}"] = str(clues["right"][i])

        Board.__inject_solution()

        self.__render_table()
        self.__render_buttons()
        Board.__render_metrics()

    def __render_table(self):
        n = self.n
        top = st.columns([0.7] + [1]*n + [0.7])
        for c in range(n):
            with top[c+1]:
                st.text_input("", key=f"top_{c}", max_chars=1)

        for r in range(n):
            row = st.columns([0.7] + [1]*n + [0.7])
            with row[0]:
                st.text_input("", key=f"left_{r}", max_chars=1)
            for c in range(n):
                with row[c+1]:
                    st.text_input("", key=f"cell_{r}_{c}", disabled=True)
            with row[-1]:
                st.text_input("", key=f"right_{r}", max_chars=1)

        bottom = st.columns([0.7] + [1]*n + [0.7])
        for c in range(n):
            with bottom[c+1]:
                st.text_input("", key=f"bottom_{c}", max_chars=1)

    def __render_buttons(self):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("CSP + AC3"):
                self.__run_solver("CSP", "Puzzle solved with CSP + AC3!")
        with col2:
            if st.button("A* / Weighted A*"):
                self.__run_solver("A*", "Puzzle solved with A*!")
        with col3:
            if st.button("Hill Climbing / SA"):
                self.__run_solver("HillClimb", "Puzzle solved with Hill Climbing / SA!")
        with col4:
            if st.button("Generate Random Puzzle"):
                generator = RandomPuzzleGenerator(self.n)
                clues = generator.generate()

                st.session_state["generated_clues"] = clues
                st.session_state["force_reload"] = True
                st.rerun()

    def __run_solver(self, solver_name, success_message):
        data = self.__collect_data()
        result, metrics = PuzzleManager(data, solver_name).run()

        if result is None:
            st.error(metrics or "Solver failed.")
            return

        st.session_state["solution"] = result
        st.session_state["metrics"] = metrics

        keys = list(st.session_state.keys())
        for k in keys:
            if k not in ["solution", "board_size", "reload_trigger", "metrics"]:
                del st.session_state[k]

        st.success(success_message)

        Board.__hard_reload()

    def __collect_data(self):
        n = self.n
        data = {"n": n, "clues": {"top": [], "bottom": [], "left": [], "right": []}, "grid": []}

        for c in range(n):
            data["clues"]["top"].append(st.session_state.get(f"top_{c}", ""))
        for r in range(n):
            data["clues"]["left"].append(st.session_state.get(f"left_{r}", ""))
            row = []
            for c in range(n):
                row.append(st.session_state.get(f"cell_{r}_{c}", ""))
            data["grid"].append(row)
            data["clues"]["right"].append(st.session_state.get(f"right_{r}", ""))
        for c in range(n):
            data["clues"]["bottom"].append(st.session_state.get(f"bottom_{c}", ""))
        return data

    @staticmethod
    def __render_metrics():
        metrics = st.session_state.get("metrics")
        if metrics:
            st.subheader("Performance Metrics")
            for key, value in metrics.items():
                st.write(f"{key.replace('_', ' ').capitalize()}: {value}")