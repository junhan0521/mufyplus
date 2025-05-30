import streamlit as st
import random
import numpy as np
import time

class MinesweeperGame:
    def __init__(self, rows=10, cols=10, mines=15):
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.board = np.zeros((rows, cols), dtype=int)
        self.revealed = np.zeros((rows, cols), dtype=bool)
        self.flagged = np.zeros((rows, cols), dtype=bool)
        self.game_over = False
        self.won = False
        self.first_click = True
        self.hit_mine_pos = None
        self.start_time = time.time()
        
    def place_mines(self, safe_row, safe_col):
        """Place mines randomly, avoiding the first clicked cell"""
        mine_positions = set()
        while len(mine_positions) < self.mines:
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)
            if (row, col) != (safe_row, safe_col) and (row, col) not in mine_positions:
                mine_positions.add((row, col))
                self.board[row, col] = -1  # -1 represents a mine
        
        # Calculate numbers for non-mine cells
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board[row, col] != -1:
                    count = 0
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            if dr == 0 and dc == 0:
                                continue
                            nr, nc = row + dr, col + dc
                            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                                if self.board[nr, nc] == -1:
                                    count += 1
                    self.board[row, col] = count
    
    def reveal_cell(self, row, col):
        """Reveal a cell and handle game logic"""
        if self.game_over or self.revealed[row, col] or self.flagged[row, col]:
            return
        
        # Place mines after first click to ensure safe start
        if self.first_click:
            self.place_mines(row, col)
            self.first_click = False
        
        self.revealed[row, col] = True
        
        # Hit a mine - reveal entire board and end game
        if self.board[row, col] == -1:
            self.game_over = True
            self.hit_mine_pos = (row, col)
            self.reveal_all_mines()
            return
        
        # Auto-reveal adjacent cells if this cell has no adjacent mines
        if self.board[row, col] == 0:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        if not self.revealed[nr, nc] and not self.flagged[nr, nc]:
                            self.reveal_cell(nr, nc)
        
        # Check win condition after each reveal
        self.check_win()
    
    def reveal_all_mines(self):
        """Reveal all mines when player hits one"""
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board[row, col] == -1:
                    self.revealed[row, col] = True
    
    def toggle_flag(self, row, col):
        """Toggle flag on unrevealed cells"""
        if not self.revealed[row, col] and not self.game_over:
            self.flagged[row, col] = not self.flagged[row, col]
    
    def check_win(self):
        """Check if player has won by revealing all non-mine cells"""
        non_mine_cells = 0
        revealed_non_mine_cells = 0
        
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board[row, col] != -1:
                    non_mine_cells += 1
                    if self.revealed[row, col]:
                        revealed_non_mine_cells += 1
        
        if non_mine_cells == revealed_non_mine_cells:
            self.won = True
            self.game_over = True
            return True
        return False
    
    def get_cell_content(self, row, col):
        """Get the display content and style for a cell"""
        if self.flagged[row, col] and not self.revealed[row, col]:
            return "🚩", "flagged"
        elif not self.revealed[row, col]:
            return "", "hidden"
        elif self.board[row, col] == -1:
            if self.hit_mine_pos == (row, col):
                return "💥", "exploded_mine"
            else:
                return "💣", "mine"
        elif self.board[row, col] == 0:
            return "", "empty"
        else:
            return str(self.board[row, col]), f"number_{self.board[row, col]}"
    
    def get_elapsed_time(self):
        """Get elapsed time in seconds"""
        if self.game_over:
            return getattr(self, 'end_time', time.time()) - self.start_time
        return time.time() - self.start_time

def apply_custom_css():
    """Apply custom CSS styling"""
    st.markdown("""
    <style>
    /* Main app styling */
    .main-title {
        text-align: center;
        font-size: 3.5rem;
        font-weight: bold;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradient 3s ease infinite;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Game controls styling */
    .game-controls {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    /* Game board container */
    .game-board-container {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 12px 40px rgba(0,0,0,0.15);
        margin: 2rem 0;
    }
    
    /* Cell button styling */
    .stButton > button {
        width: 40px !important;
        height: 40px !important;
        padding: 0 !important;
        margin: 1px !important;
        border-radius: 6px !important;
        font-size: 18px !important;
        font-weight: bold !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.2s ease !important;
    }
    
    /* Hidden cell styling */
    .cell-hidden {
        background: linear-gradient(145deg, #e0e0e0, #c0c0c0) !important;
        border: 2px outset #d0d0d0 !important;
        color: transparent !important;
    }
    
    .cell-hidden:hover {
        background: linear-gradient(145deg, #f0f0f0, #d0d0d0) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
    }
    
    /* Revealed empty cell */
    .cell-empty {
        background: linear-gradient(145deg, #f5f5f5, #e8e8e8) !important;
        border: 2px inset #e0e0e0 !important;
        color: transparent !important;
    }
    
    /* Mine styling */
    .cell-mine {
        background: linear-gradient(145deg, #ff6b6b, #ee5a52) !important;
        border: 2px inset #ff5722 !important;
        color: #000 !important;
    }
    
    /* Exploded mine with animation */
    .cell-exploded {
        background: linear-gradient(145deg, #ff3838, #d32f2f) !important;
        border: 2px inset #c62828 !important;
        color: #000 !important;
        animation: explosion 0.8s ease-in-out !important;
    }
    
    @keyframes explosion {
        0% { transform: scale(1); }
        50% { transform: scale(1.3); background: #ffff00; }
        100% { transform: scale(1); }
    }
    
    /* Flagged cell */
    .cell-flagged {
        background: linear-gradient(145deg, #ffd93d, #ffcd02) !important;
        border: 2px outset #ffc107 !important;
        color: #000 !important;
    }
    
    /* Number styling */
    .cell-number-1 { background: linear-gradient(145deg, #f5f5f5, #e8e8e8) !important; border: 2px inset #e0e0e0 !important; color: #1976d2 !important; }
    .cell-number-2 { background: linear-gradient(145deg, #f5f5f5, #e8e8e8) !important; border: 2px inset #e0e0e0 !important; color: #388e3c !important; }
    .cell-number-3 { background: linear-gradient(145deg, #f5f5f5, #e8e8e8) !important; border: 2px inset #e0e0e0 !important; color: #d32f2f !important; }
    .cell-number-4 { background: linear-gradient(145deg, #f5f5f5, #e8e8e8) !important; border: 2px inset #e0e0e0 !important; color: #7b1fa2 !important; }
    .cell-number-5 { background: linear-gradient(145deg, #f5f5f5, #e8e8e8) !important; border: 2px inset #e0e0e0 !important; color: #689f38 !important; }
    .cell-number-6 { background: linear-gradient(145deg, #f5f5f5, #e8e8e8) !important; border: 2px inset #e0e0e0 !important; color: #0288d1 !important; }
    .cell-number-7 { background: linear-gradient(145deg, #f5f5f5, #e8e8e8) !important; border: 2px inset #e0e0e0 !important; color: #5d4037 !important; }
    .cell-number-8 { background: linear-gradient(145deg, #f5f5f5, #e8e8e8) !important; border: 2px inset #e0e0e0 !important; color: #424242 !important; }
    
    /* Flag button styling */
    .flag-button {
        width: 25px !important;
        height: 40px !important;
        font-size: 14px !important;
        background: linear-gradient(145deg, #ffd93d, #ffcd02) !important;
        border: 1px solid #ffc107 !important;
        border-radius: 6px !important;
    }
    
    /* Statistics styling */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
    
    div[data-testid="metric-container"] label {
        color: rgba(255, 255, 255, 0.8) !important;
        font-weight: bold !important;
    }
    
    div[data-testid="metric-container"] div {
        color: white !important;
        font-size: 1.5rem !important;
        font-weight: bold !important;
    }
    
    /* Game status styling */
    .status-won {
        background: linear-gradient(135deg, #4caf50, #8bc34a);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.2rem;
        font-weight: bold;
        animation: celebration 1s ease-in-out;
    }
    
    .status-lost {
        background: linear-gradient(135deg, #f44336, #e57373);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.2rem;
        font-weight: bold;
    }
    
    .status-playing {
        background: linear-gradient(135deg, #2196f3, #64b5f6);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.2rem;
        font-weight: bold;
    }
    
    @keyframes celebration {
        0%, 100% { transform: scale(1); }
        25% { transform: scale(1.05); }
        50% { transform: scale(1.1); }
        75% { transform: scale(1.05); }
    }
    
    /* Instructions styling */
    .stExpander {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    # Page configuration
    st.set_page_config(
        page_title="💣 Minesweeper Game",
        page_icon="💣",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Apply custom styling
    apply_custom_css()
    
    # Main title with animation
    st.markdown('<h1 class="main-title">💣 MINESWEEPER 💣</h1>', unsafe_allow_html=True)
    
    # Initialize game state
    if 'game' not in st.session_state:
        st.session_state.game = MinesweeperGame()
    
    game = st.session_state.game
    
    # Game controls section
    st.markdown('<div class="game-controls">', unsafe_allow_html=True)
    
    # Top row controls
    control_cols = st.columns([1, 2, 1, 1, 1, 1])
    
    with control_cols[0]:
        if st.button("🔄 New Game", use_container_width=True, type="primary"):
            st.session_state.game = MinesweeperGame(game.rows, game.cols, game.mines)
            st.rerun()
    
    with control_cols[1]:
        difficulty_options = [
            "🟢 Beginner (9×9, 10 mines)",
            "🟡 Intermediate (16×16, 40 mines)", 
            "🔴 Expert (30×16, 99 mines)",
            "🟣 Custom (10×10, 15 mines)"
        ]
        
        selected_difficulty = st.selectbox(
            "Select Difficulty",
            difficulty_options,
            label_visibility="collapsed"
        )
        
        # Set difficulty parameters
        if "Beginner" in selected_difficulty:
            rows, cols, mines = 9, 9, 10
        elif "Intermediate" in selected_difficulty:
            rows, cols, mines = 16, 16, 40
        elif "Expert" in selected_difficulty:
            rows, cols, mines = 30, 16, 99
        else:  # Custom
            rows, cols, mines = 10, 10, 15
        
        # Reset game if difficulty changed
        if (rows, cols, mines) != (game.rows, game.cols, game.mines):
            st.session_state.game = MinesweeperGame(rows, cols, mines)
            st.rerun()
    
    with control_cols[2]:
        mines_remaining = max(0, game.mines - np.sum(game.flagged))
        st.metric("💣 Mines Left", mines_remaining)
    
    with control_cols[3]:
        cells_revealed = np.sum(game.revealed & (game.board != -1))
        total_safe_cells = game.rows * game.cols - game.mines
        st.metric("🔍 Progress", f"{cells_revealed}/{total_safe_cells}")
    
    with control_cols[4]:
        elapsed_time = int(game.get_elapsed_time())
        st.metric("⏱️ Time", f"{elapsed_time}s")
    
    with control_cols[5]:
        # Game status
        if game.won:
            st.markdown('<div class="status-won">🎉 VICTORY! 🎉</div>', unsafe_allow_html=True)
        elif game.game_over:
            st.markdown('<div class="status-lost">💥 GAME OVER 💥</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-playing">🎮 PLAYING</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Instructions expandable section
    with st.expander("📖 How to Play Minesweeper", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 🎯 **Objective**
            - Clear all cells without hitting any mines
            - Use number clues to deduce mine locations
            
            ### 🎮 **Controls**
            - **Left Click**: Reveal a cell
            - **Flag Button (🚩)**: Mark suspected mines
            - **Numbers**: Show adjacent mine count
            """)
        
        with col2:
            st.markdown("""
            ### 🧠 **Strategy Tips**
            - Start with corners and edges
            - Use logical deduction from numbers
            - Flag suspected mines to avoid accidents
            - Empty cells auto-reveal adjacent areas
            
            ### 🏆 **Winning**
            - Reveal all safe cells to win
            - Flagging all mines is optional
            """)
    
    # Game board section
    st.markdown('<div class="game-board-container">', unsafe_allow_html=True)
    
    # Create grid layout - calculate total columns needed (cells + flags)
    total_cols_per_row = game.cols * 2  # Each cell needs 2 columns (cell + flag)
    
    # Create the game grid
    for row in range(game.rows):
        # Create columns for this row
        row_cols = st.columns(total_cols_per_row)
        
        for col in range(game.cols):
            # Get cell content and style
            cell_content, cell_type = game.get_cell_content(row, col)
            
            # Calculate column indices (cell at even index, flag at odd index)
            cell_col_idx = col * 2
            flag_col_idx = col * 2 + 1
            
            # Main cell button
            with row_cols[cell_col_idx]:
                cell_key = f"cell_{row}_{col}"
                display_text = cell_content if cell_content else " "
                
                if st.button(
                    display_text,
                    key=cell_key,
                    help=f"Row {row+1}, Col {col+1}",
                    use_container_width=True
                ):
                    if not game.flagged[row, col] and not game.game_over:
                        game.reveal_cell(row, col)
                        if game.game_over and not game.won:
                            # Store end time when game ends
                            game.end_time = time.time()
                        st.rerun()
            
            # Flag toggle button (only for unrevealed cells)
            with row_cols[flag_col_idx]:
                if not game.revealed[row, col] and not game.game_over:
                    flag_key = f"flag_{row}_{col}"
                    flag_symbol = "🚩" if game.flagged[row, col] else "⚐"
                    
                    if st.button(
                        flag_symbol,
                        key=flag_key,
                        help="Toggle flag",
                        use_container_width=True
                    ):
                        game.toggle_flag(row, col)
                        st.rerun()
                else:
                    # Empty space for revealed cells
                    st.write("")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Game over statistics and options
    if game.game_over:
        st.markdown("---")
        st.markdown("### 📊 **Final Statistics**")
        
        stats_cols = st.columns(5)
        
        with stats_cols[0]:
            final_time = int(game.get_elapsed_time())
            st.metric("⏱️ Total Time", f"{final_time}s")
        
        with stats_cols[1]:
            revealed_safe = np.sum(game.revealed & (game.board != -1))
            st.metric("✅ Safe Cells Found", f"{revealed_safe}/{total_safe_cells}")
        
        with stats_cols[2]:
            completion = (revealed_safe / total_safe_cells * 100) if total_safe_cells > 0 else 0
            st.metric("📈 Completion", f"{completion:.1f}%")
        
        with stats_cols[3]:
            flags_used = np.sum(game.flagged)
            st.metric("🚩 Flags Used", f"{flags_used}")
        
        with stats_cols[4]:
            if game.won:
                st.metric("🏆 Result", "WINNER! 🎉")
            else:
                st.metric("💀 Result", "Try Again!")
        
        # Play again section
        st.markdown("---")
        restart_cols = st.columns([1, 2, 1])
        
        with restart_cols[1]:
            if st.button(
                "🎮 Start New Game" if game.won else "🔄 Try Again",
                type="primary",
                use_container_width=True
            ):
                st.session_state.game = MinesweeperGame(game.rows, game.cols, game.mines)
                st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; padding: 1rem;'>"
        "💣 Classic Minesweeper • Built with Streamlit • Good Luck! 🍀"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
