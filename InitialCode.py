import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import sys

# --- 1. DATA LOADING (Same Logic) ---
def load_data():
    filename = 'atp_tennis_.csv'
    try:
        print("📂 Loading dataset...")
        df = pd.read_csv(filename)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Year'] = df['Date'].dt.year
        print("✅ Data loaded successfully!")
        return df
    except FileNotFoundError:
        print("❌ Error: 'atp_tennis_.csv' not found.")
        return None

# --- 2. INTERACTIVE TERMINAL APP ---
def main():
    df = load_data()
    if df is None:
        return

    while True:
        print("\n" + "="*40)
        print("   🎾 ATP TENNIS ANALYZER (CLI MODE)")
        print("="*40)
        
        # --- STEP 1: SELECT ERA ---
        print("\n[Step 1] Select an Era to analyze:")
        print("  1. All Time (2000-2025)")
        print("  2. The 2000s (2000-2009)")
        print("  3. The 2010s (2010-2019)")
        print("  4. The 2020s (2020-Present)")
        print("  Q. Quit")
        
        choice = input("\n👉 Enter your choice (1-4): ").strip().lower()
        
        if choice == 'q':
            print("Goodbye! 👋")
            break
            
        era_df = df.copy()
        era_name = "All Time"
        
        if choice == '2':
            era_df = df[(df['Year'] >= 2000) & (df['Year'] <= 2009)]
            era_name = "The 2000s"
        elif choice == '3':
            era_df = df[(df['Year'] >= 2010) & (df['Year'] <= 2019)]
            era_name = "The 2010s"
        elif choice == '4':
            era_df = df[df['Year'] >= 2020]
            era_name = "The 2020s"
        elif choice != '1':
            print("⚠️ Invalid choice, defaulting to All Time.")

        # --- STEP 2: SELECT TOP N ---
        try:
            top_n_input = input("\n[Step 2] How many top players do you want to list? (e.g., 5, 10): ")
            top_n = int(top_n_input)
        except ValueError:
            print("⚠️ Invalid number. showing Top 5 by default.")
            top_n = 5

        # Calculate Top Winners
        top_winners = era_df['Winner'].value_counts().head(top_n)
        top_players_list = top_winners.index.tolist()

        # --- STEP 3: SELECT PLAYER FROM LIST ---
        print(f"\n[Step 3] Top {top_n} Players of {era_name}:")
        for idx, player in enumerate(top_players_list):
            print(f"  {idx + 1}. {player} ({top_winners[player]} wins)")
        
        try:
            p_choice = input(f"\n👉 Select a player by number (1-{top_n}): ")
            p_index = int(p_choice) - 1
            if 0 <= p_index < len(top_players_list):
                selected_player = top_players_list[p_index]
            else:
                print("⚠️ Invalid number selected.")
                continue
        except ValueError:
            print("⚠️ Invalid input.")
            continue

        # --- STEP 4: SHOW STATS ---
        print("\n" + "-"*30)
        print(f"📊 REPORT FOR: {selected_player.upper()}")
        print("-"*30)
        
        # Calculate Stats (using full history for context)
        # Matches where they played
        p_matches = df[(df['Player_1'] == selected_player) | (df['Player_2'] == selected_player)]
        p_wins = len(df[df['Winner'] == selected_player])
        total_played = len(p_matches)
        win_rate = (p_wins / total_played * 100) if total_played > 0 else 0
        
        print(f"  • Total Career Matches: {total_played}")
        print(f"  • Total Career Wins:    {p_wins}")
        print(f"  • Career Win Rate:      {win_rate:.1f}%")
        
        # Best Surface
        if not p_matches.empty:
            wins_by_surface = df[df['Winner'] == selected_player]['Surface'].value_counts()
            if not wins_by_surface.empty:
                best_surface = wins_by_surface.idxmax()
                print(f"  • Best Surface:         {best_surface} ({wins_by_surface.max()} wins)")

        # --- STEP 5: VISUALIZATIONS ---
        print("\n[Step 5] Visualization Options:")
        vis_choice = input("👉 Show charts? (y/n): ").lower()
        
        if vis_choice == 'y':
            print("Generating charts... (Check the popup window)")
            
            # Setup a matplotlib figure with 2 subplots
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
            
            # Chart 1: Wins by Surface
            surface_data = df[df['Winner'] == selected_player]['Surface'].value_counts()
            sns.barplot(x=surface_data.index, y=surface_data.values, ax=ax1, palette="viridis")
            ax1.set_title(f"{selected_player} - Wins by Surface")
            ax1.set_ylabel("Wins")
            
            # Chart 2: Wins Over Time
            yearly_wins = df[df['Winner'] == selected_player].groupby('Year').size()
            sns.lineplot(x=yearly_wins.index, y=yearly_wins.values, marker='o', ax=ax2, color='b')
            ax2.set_title(f"{selected_player} - Wins per Year")
            ax2.set_ylabel("Wins")
            
            plt.tight_layout()
            plt.show()
            
            # Bonus: Heatmap check
            heat_choice = input("👉 Show Global Era Heatmap? (y/n): ").lower()
            if heat_choice == 'y':
                print("Generating heatmap...")
                plt.figure(figsize=(14, 10))
                wins_per_year = df.groupby(['Year', 'Winner']).size().reset_index(name='Wins')
                top3 = wins_per_year.sort_values(['Year', 'Wins'], ascending=[True, False]).groupby('Year').head(3)
                pivot_df = top3.pivot(index='Year', columns='Winner', values='Wins')
                sns.heatmap(pivot_df, cmap='YlOrRd', annot=True, fmt='g')
                plt.title("Top 3 Players by Wins (Yearly)")
                plt.show()

if __name__ == "__main__":
    main()
        
