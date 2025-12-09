import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import sys

# Set Streamlit page configuration early
st.set_page_config(layout="wide", page_title="ATP Tennis Analyzer")

# -----------------------------------------
# COLOR THEMES FOR PLAYERS (from original file)
# -----------------------------------------
PLAYER_COLORS = {
    # Big names (add more if needed)
    "Roger Federer": "#1f77b4",
    "Rafael Nadal": "#d62728",
    "Novak Djokovic": "#2ca02c",
    "Andy Murray": "#9467bd",
    "Stan Wawrinka": "#ff7f0e",
}

DEFAULT_COLOR = "#4e79a7"   # used when player not in dict

def get_player_color(player_name):
    """Retrieves the color for a specific player."""
    return PLAYER_COLORS.get(player_name, DEFAULT_COLOR)


# -----------------------------------------
# DATA LOADING (Adapted for Streamlit caching)
# -----------------------------------------
@st.cache_data
def load_data():
    """Loads and preprocesses the ATP tennis dataset."""
    filename = 'atp_tennis_.csv'
    try:
        df = pd.read_csv(filename)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        # Drop rows where date conversion failed or are incomplete
        df.dropna(subset=['Date', 'Winner', 'Player_1', 'Player_2', 'Surface', 'Round'], inplace=True)
        df['Year'] = df['Date'].dt.year
        return df
    except FileNotFoundError:
        st.error(f"❌ Error: '{filename}' not found. Please ensure the file is correctly uploaded.")
        return None
    except Exception as e:
        st.error(f"An error occurred during data loading: {e}")
        return None

# -----------------------------------------
# HELPER FUNCTION FOR STATS
# -----------------------------------------
def get_player_stats(df, player_name):
    """Helper function to calculate key career stats for one player."""
    player_matches = df[(df['Player_1'] == player_name) | (df['Player_2'] == player_name)].copy()
    wins = (player_matches['Winner'] == player_name).sum()
    total_matches = len(player_matches)
    win_rate = (wins / total_matches) * 100 if total_matches > 0 else 0
    
    # Calculate wins by surface
    surface_wins = player_matches[player_matches['Winner'] == player_name].groupby('Surface').size().reset_index(name='Wins')
    surface_wins['Player'] = player_name
    
    return total_matches, win_rate, surface_wins


# -----------------------------------------
# PLOTTING FUNCTIONS
# -----------------------------------------

def plot_annual_win_rate(df, player_name):
    """Generates and displays a line chart of the player's annual win rate."""
    st.subheader(f"{player_name}'s Annual Win Rate Trend")
    
    player_matches = df[(df['Player_1'] == player_name) | (df['Player_2'] == player_name)].copy()

    if player_matches.empty:
        st.info(f"No match data available for {player_name} in the selected period.")
        return

    # Calculate wins and total matches per year
    yearly_stats = player_matches.groupby('Year').agg(
        Total_Matches=('Date', 'count'),
        Wins=('Winner', lambda x: (x == player_name).sum())
    ).reset_index()

    # Calculate win rate
    yearly_stats['Win_Rate'] = (yearly_stats['Wins'] / yearly_stats['Total_Matches']) * 100

    if not yearly_stats.empty:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        player_color = get_player_color(player_name)
        
        ax.plot(yearly_stats['Year'], yearly_stats['Win_Rate'], 
                marker='o', linestyle='-', color=player_color, linewidth=2, markersize=6)
        
        ax.set_title(f"{player_name} Winning Percentage by Year", fontsize=14)
        ax.set_xlabel("Year", fontsize=12)
        ax.set_ylabel("Win Rate (%)", fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.set_ylim(0, 100) # Win rate is between 0 and 100

        # Adjust x-axis ticks to show only integer years
        years = yearly_stats['Year'].unique()
        # Show a maximum of 10 ticks for readability
        step = max(1, len(years) // 10)
        ax.set_xticks(years[::step]) 
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.info("No yearly data found to plot the trend.")


def plot_career_stats(df, player_name):
    """Generates and displays career statistics for a selected player (Original and calls new trend)."""
    
    total_matches, win_rate, surface_wins_df = get_player_stats(df, player_name)

    if total_matches == 0:
        st.info(f"No matches found for {player_name} in the selected time frame ({df['Year'].min()} - {df['Year'].max()}).")
        return
    
    wins = (total_matches * win_rate / 100) # Calculate wins from total and rate
    
    st.subheader(f"Summary Statistics for {player_name}")
    
    col_a, col_b = st.columns(2)
    col_a.metric(label="Total Matches Played", value=total_matches)
    col_b.metric(label="Overall Win Rate", value=f"{win_rate:.1f}%", help=f"Total Wins: {wins:.0f}")
    
    st.markdown("---")
    
    # NEW CHART 1: Annual Win Rate Trend
    plot_annual_win_rate(df, player_name)

    st.markdown("---")
    st.subheader("Wins by Surface")
    
    # Count wins by surface from helper function
    surface_wins = surface_wins_df.set_index('Surface')['Wins']

    if not surface_wins.empty:
        fig, ax = plt.subplots(figsize=(8, 5))
        surface_wins.plot(kind='bar', ax=ax, color=get_player_color(player_name))
        ax.set_title(f"{player_name} Wins by Surface")
        ax.set_ylabel("Number of Wins")
        ax.set_xlabel("Surface")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.info("No wins recorded in this range.")

# -----------------------------------------
# NEW COMPARISON FUNCTION
# -----------------------------------------

def plot_player_comparison(df, player1, player2):
    """Generates and displays comparison statistics for two selected players."""
    st.header(f"⚖️ Lifetime Career Comparison: {player1} vs {player2}")

    # 1. Get stats for both players
    total1, rate1, surface_wins1 = get_player_stats(df, player1)
    total2, rate2, surface_wins2 = get_player_stats(df, player2)

    # 2. Display summary metrics side-by-side
    st.subheader("Overall Performance")
    col_a, col_b = st.columns(2)
    
    # Player 1 Metrics
    with col_a:
        st.metric(
            label=f"{player1} Total Matches Played", 
            value=total1
        )
        st.metric(
            label=f"{player1} Overall Win Rate", 
            value=f"{rate1:.1f}%", 
            delta=f"{rate1 - rate2:.1f}% Win Rate Difference" if total1 > 0 and total2 > 0 else None,
            delta_color="normal" if rate1 > rate2 else ("inverse" if rate2 > rate1 else "off")
        )
    
    # Player 2 Metrics
    with col_b:
        st.metric(
            label=f"{player2} Total Matches Played", 
            value=total2
        )
        st.metric(
            label=f"{player2} Overall Win Rate", 
            value=f"{rate2:.1f}%", 
            delta=f"{rate2 - rate1:.1f}% Win Rate Difference" if total1 > 0 and total2 > 0 else None,
            delta_color="normal" if rate2 > rate1 else ("inverse" if rate1 > rate2 else "off")
        )
        
    st.markdown("---")

    # 3. Surface Wins Comparison (Grouped Bar Chart)
    st.subheader("Wins by Surface Comparison")
    
    # Combine dataframes
    combined_surface_wins = pd.concat([surface_wins1, surface_wins2])
    
    if combined_surface_wins.empty:
        st.info("No wins recorded for these players in the selected range.")
        return

    # Create the grouped bar chart using Matplotlib/Seaborn
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        x='Surface', 
        y='Wins', 
        hue='Player', 
        data=combined_surface_wins,
        palette={player1: get_player_color(player1), player2: get_player_color(player2)},
        ax=ax
    )
    
    ax.set_title(f"Wins by Surface: {player1} vs {player2}", fontsize=14)
    ax.set_ylabel("Number of Wins", fontsize=12)
    ax.set_xlabel("Surface", fontsize=12)
    ax.legend(title="Player")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)


def plot_h2h_trend(df, player1, player2):
    """Plots the cumulative head-to-head score over time."""
    st.subheader(f"Historical Head-to-Head Trend ({player1} vs {player2})")

    h2h_matches = df[((df['Player_1'] == player1) & (df['Player_2'] == player2)) | 
                     ((df['Player_1'] == player2) & (df['Player_2'] == player1))].sort_values(by='Date').copy()

    if h2h_matches.empty:
        return # Handled in summary function
    
    # Calculate who won each match (1 if Player 1 won, 0 otherwise)
    h2h_matches['P1_Win'] = (h2h_matches['Winner'] == player1).astype(int)
    h2h_matches['P2_Win'] = (h2h_matches['Winner'] == player2).astype(int)

    # Calculate cumulative score
    h2h_matches['P1_Cumulative_Wins'] = h2h_matches['P1_Win'].cumsum()
    h2h_matches['P2_Cumulative_Wins'] = h2h_matches['P2_Win'].cumsum()
    h2h_matches['Match_Number'] = range(1, len(h2h_matches) + 1)

    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plotting Player 1's cumulative wins
    ax.plot(h2h_matches['Match_Number'], h2h_matches['P1_Cumulative_Wins'], 
            label=player1, marker='o', linestyle='-', color=get_player_color(player1), linewidth=2)
    
    # Plotting Player 2's cumulative wins
    ax.plot(h2h_matches['Match_Number'], h2h_matches['P2_Cumulative_Wins'], 
            label=player2, marker='s', linestyle='--', color=get_player_color(player2), linewidth=2)

    ax.set_title(f"{player1} vs {player2}: Head-to-Head History", fontsize=14)
    ax.set_xlabel("Match Number (Chronological)", fontsize=12)
    ax.set_ylabel("Cumulative Wins", fontsize=12)
    ax.legend(loc='upper left')
    ax.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    st.pyplot(fig)


def plot_h2h_summary(df, player1, player2):
    """Calculates and displays a summary and pie chart for Head-to-Head record."""
    h2h_matches = df[((df['Player_1'] == player1) & (df['Player_2'] == player2)) | 
                     ((df['Player_1'] == player2) & (df['Player_2'] == player1))].copy()

    if h2h_matches.empty:
        st.info(f"No Head-to-Head matches found between {player1} and {player2} in this range.")
        return

    p1_wins = (h2h_matches['Winner'] == player1).sum()
    p2_wins = (h2h_matches['Winner'] == player2).sum()
    total = len(h2h_matches)
    
    st.subheader("Overall Head-to-Head Record")
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Total Matches", total)
    col_b.metric(f"{player1} Wins", p1_wins, delta=f"{p1_wins - p2_wins} net wins" if p1_wins > p2_wins else None)
    col_c.metric(f"{player2} Wins", p2_wins, delta=f"{p2_wins - p1_wins} net wins" if p2_wins > p1_wins else None)

    if total > 0:
        # Pie Chart for H2H Wins
        labels = [player1, player2]
        sizes = [p1_wins, p2_wins]
        colors = [get_player_color(player1), get_player_color(player2)]

        fig, ax = plt.subplots(figsize=(6, 6))
        # Filter out 0 size slices for cleaner look
        filtered_labels = [labels[i] for i, size in enumerate(sizes) if size > 0]
        filtered_sizes = [size for size in sizes if size > 0]
        filtered_colors = [colors[i] for i, size in enumerate(sizes) if size > 0]
        
        ax.pie(filtered_sizes, labels=filtered_labels, autopct='%1.1f%%', startangle=90, colors=filtered_colors, wedgeprops={'edgecolor': 'black', 'linewidth': 1})
        ax.axis('equal') 
        st.pyplot(fig)

def plot_h2h_heatmap(df, player1, player2):
    """Generates the win difference heatmap by Surface and Round."""
    st.subheader("Win Difference by Surface and Round (Heatmap)")
    
    h2h_matches = df[((df['Player_1'] == player1) & (df['Player_2'] == player2)) | 
                     ((df['Player_1'] == player2) & (df['Player_2'] == player1))].copy()
    
    if h2h_matches.empty:
        return # Handled in summary function

    # Check for critical columns
    if h2h_matches[['Surface', 'Round']].isnull().any().any():
        st.warning("⚠️ Heatmap requires 'Surface' and 'Round' data, which is missing for some matches in this head-to-head.")
        return

    # Logic adapted from the user's original snippet
    p1_wins = h2h_matches[h2h_matches['Winner'] == player1]
    p2_wins = h2h_matches[h2h_matches['Winner'] == player2]
    
    # Aggregate wins by Surface and Round
    heat1 = p1_wins.groupby(["Surface", "Round"]).size().reset_index(name="P1")
    heat2 = p2_wins.groupby(["Surface", "Round"]).size().reset_index(name="P2")
    
    # Merge, fill NaN with 0
    merged = pd.merge(heat1, heat2, on=["Surface", "Round"], how="outer").fillna(0)

    # Pivot P1 and P2
    pivot_p1 = merged.pivot(index="Surface", columns="Round", values="P1").fillna(0)
    pivot_p2 = merged.pivot(index="Surface", columns="Round", values="P2").fillna(0)

    # Align indexes/columns
    all_surfaces = sorted(set(pivot_p1.index) | set(pivot_p2.index))
    all_rounds = sorted(set(pivot_p1.columns) | set(pivot_p2.columns))

    pivot_p1 = pivot_p1.reindex(index=all_surfaces, columns=all_rounds, fill_value=0)
    pivot_p2 = pivot_p2.reindex(index=all_surfaces, columns=all_rounds, fill_value=0)

    # Calculate difference (Player 1 Wins - Player 2 Wins)
    diff = pivot_p1 - pivot_p2

    # Plotting the heatmap
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.heatmap(diff, 
                cmap="coolwarm", 
                center=0, 
                annot=True, 
                fmt=".0f", 
                linewidths=.5, 
                linecolor='lightgray',
                cbar_kws={'label': f'Wins ({player1} - {player2})'})
    
    ax.set_title(f"{player1} vs {player2} – Win Difference by Surface/Round")
    ax.set_xlabel("Round")
    ax.set_ylabel("Surface")
    plt.yticks(rotation=0)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)


# -----------------------------------------
# MAIN STREAMLIT APPLICATION
# -----------------------------------------
def main_app():
    """Main function to run the Streamlit app."""
    
    st.title("🎾 ATP Tennis Match Analyzer")
    st.caption("Analyze career statistics and head-to-head records using the provided match data.")
    
    df = load_data()
    if df is None:
        return

    # Extract all unique player names
    all_players = sorted(pd.concat([df['Player_1'], df['Player_2']]).unique())

    # --- SIDEBAR (SELECTIONS) ---
    st.sidebar.header("⚙️ Analysis Settings")
    
    # Analysis Mode Selector (UPDATED)
    analysis_mode = st.sidebar.radio(
        "Choose Analysis Type:",
        ("Career Stats", "Head-to-Head Comparison", "Two-Player Lifetime Comparison")
    )
    
    # Year Range Slider
    min_year = int(df['Year'].min())
    max_year = int(df['Year'].max())
    year_range = st.sidebar.slider(
        "Select Year Range:",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
        step=1
    )
    
    # Filter data by year range
    df_filtered = df[(df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1])].copy()
    
    # --- ANALYSIS LOGIC ---
    
    if analysis_mode == "Career Stats":
        st.header("📊 Player Career Statistics")
        
        # Determine the default player for career stats
        default_index = all_players.index("Roger Federer") if "Roger Federer" in all_players else 0
        
        selected_player = st.selectbox(
            "Select a Player for Career Analysis:",
            all_players,
            index=default_index
        )
        
        if selected_player:
            plot_career_stats(df_filtered, selected_player)

    elif analysis_mode == "Head-to-Head Comparison":
        st.header("⚔️ Head-to-Head Matchup Comparison")
        
        col1, col2 = st.columns(2)
        
        # Determine default players for Head-to-Head
        default_p1_idx = all_players.index("Roger Federer") if "Roger Federer" in all_players else 0
        default_p2_idx = all_players.index("Rafael Nadal") if "Rafael Nadal" in all_players else (1 if len(all_players) > 1 else 0)

        with col1:
            player1 = st.selectbox("Player 1:", all_players, index=default_p1_idx)
        
        with col2:
            player2 = st.selectbox("Player 2:", all_players, index=default_p2_idx)

        st.markdown("---")

        if player1 and player2 and player1 != player2:
            plot_h2h_summary(df_filtered, player1, player2)
            st.markdown("---")
            plot_h2h_trend(df_filtered, player1, player2)
            st.markdown("---")
            plot_h2h_heatmap(df_filtered, player1, player2)
        elif player1 == player2:
            st.warning("Please select two different players for Head-to-Head comparison.")
        else:
            st.info("Select two players to begin the comparison.")

    # NEW MODE: Two-Player Lifetime Comparison
    elif analysis_mode == "Two-Player Lifetime Comparison":
        st.header("⚖️ Compare Career Statistics")
        
        col1, col2 = st.columns(2)
        
        # Determine default players for comparison
        default_p1_idx = all_players.index("Roger Federer") if "Roger Federer" in all_players else 0
        default_p2_idx = all_players.index("Novak Djokovic") if "Novak Djokovic" in all_players else (1 if len(all_players) > 1 else 0)

        with col1:
            player1 = st.selectbox("Player 1 (Left Side):", all_players, key='comp1', index=default_p1_idx)
        
        with col2:
            player2 = st.selectbox("Player 2 (Right Side):", all_players, key='comp2', index=default_p2_idx)

        st.markdown("---")

        if player1 and player2 and player1 != player2:
            plot_player_comparison(df_filtered, player1, player2)
        elif player1 == player2:
            st.warning("Please select two different players for career comparison.")
        else:
            st.info("Select two players to compare their overall career stats.")


if __name__ == "__main__":
    main_app()