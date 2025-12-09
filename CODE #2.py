import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import sys

# -----------------------------------------
# COLOR THEMES FOR PLAYERS
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


# -----------------------------------------
# DATA LOADING
# -----------------------------------------
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


# -----------------------------------------
# MAIN PROGRAM
# -----------------------------------------
def main():
    df = load_data()
    if df is None:
        return

    while True:
        print("\n" + "="*40)
        print(" 🎾 ATP TENNIS ANALYZER (CLI MODE)")
        print("="*40)

        # -------------------------
        # STEP 1: ERA SELECTION
        # -------------------------
        print("\n[Step 1] Select an Era:")
        print(" 1. All Time (2000–2025)")
        print(" 2. The 2000s (2000–2009)")
        print(" 3. The 2010s (2010–2019)")
        print(" 4. The 2020s (2020–Present)")
        print(" Q. Quit")

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

        # -------------------------
        # STEP 2: TOP N
        # -------------------------
        try:
            top_n = int(input("\n[Step 2] How many top players? "))
        except ValueError:
            print("⚠️ Invalid input → Using Top 5.")
            top_n = 5

        if era_df.empty:
            print("⚠️ Selected era has no data. Using full dataset instead.")
            era_df = df.copy()
            era_name = "All Time (fallback)"

        top_winners = era_df['Winner'].value_counts().head(top_n)
        top_players_list = top_winners.index.tolist()

        if not top_players_list:
            print("⚠️ No winners found in the selected era. Exiting.")
            return

        # -------------------------
        # STEP 3: SELECT PLAYER
        # -------------------------
        print(f"\nTop {top_n} players of {era_name}:")
        for idx, p in enumerate(top_players_list):
            print(f" {idx+1}. {p} ({top_winners[p]} wins)")

        try:
            p_choice = int(input(f"\n👉 Select a player (1–{top_n}): ")) - 1
            selected_player = top_players_list[p_choice]
        except:
            print("⚠️ Invalid selection.")
            continue

        # Color theme for this player
        p_color = PLAYER_COLORS.get(selected_player, DEFAULT_COLOR)

        # -------------------------
        # STEP 4: STATS
        # -------------------------
        print("\n" + "-"*30)
        print(f"📊 REPORT FOR: {selected_player.upper()}")
        print("-"*30)

        matches = df[(df['Player_1'] == selected_player) |
                     (df['Player_2'] == selected_player)]
        wins = df[df['Winner'] == selected_player]

        total = len(matches)
        win_rate = (len(wins) / total * 100) if total > 0 else 0

        print(f" • Total Career Matches: {total}")
        print(f" • Total Career Wins: {len(wins)}")
        print(f" • Career Win Rate: {win_rate:.1f}%")

        # Best surface
        surf = wins['Surface'].value_counts()
        if not surf.empty:
            print(f" • Best Surface: {surf.idxmax()} ({surf.max()} wins)")

        # -------------------------
        # STEP 5: VISUALS
        # -------------------------
        print("\n[Step 5] Visualization Options:")
        print(" 1. View charts for selected player")
        print(" 2. Compare two players")
        print(" q. Skip charts")

        vis_choice = input("\n👉 Enter choice: ").lower()

        # -------------------------
        # OPTION 1 — SINGLE PLAYER
        # -------------------------
        if vis_choice == "1":
            print("Generating charts...")

            # 1. BAR CHART — Wins by surface
            plt.close('all')
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

            if surf.empty:
                ax1.text(0.5, 0.5, "No surface win data", ha='center', va='center')
                ax1.set_title(f"{selected_player} - Wins by Surface")
                ax1.set_ylabel("Wins")
            else:
                sns.barplot(
                    x=surf.index,
                    y=surf.values,
                    ax=ax1,
                    color=p_color
                )
                ax1.set_title(f"{selected_player} - Wins by Surface")
                ax1.set_ylabel("Wins")

            # 2. LINE CHART — Wins per year
            yearly = wins.groupby("Year").size()
            if yearly.empty:
                ax2.text(0.5, 0.5, "No yearly win data", ha='center', va='center')
                ax2.set_title(f"{selected_player} - Wins per Year")
                ax2.set_ylabel("Wins")
            else:
                sns.lineplot(
                    x=yearly.index,
                    y=yearly.values,
                    ax=ax2,
                    marker="o",
                    color=p_color
                )
                ax2.set_title(f"{selected_player} - Wins per Year")
                ax2.set_ylabel("Wins")

            plt.tight_layout()
            plt.show()

            # -------------------------------------
            # NEW GRAPH: PLAYER HEATMAP
            # -------------------------------------
            print("🔥 Generating Player Heatmap...")

            if not wins.empty and {'Surface', 'Round'}.issubset(wins.columns):
                heat = wins.groupby(["Surface", "Round"]).size().reset_index(name="Wins")
                pivot = heat.pivot(index="Surface", columns="Round", values="Wins").fillna(0)
                plt.figure(figsize=(10, 6))
                sns.heatmap(pivot, cmap="YlOrRd", annot=True, fmt="g")
                plt.title(f"{selected_player} – Heatmap (Surface × Round Wins)")
                plt.show()
            else:
                print("⚠️ Not enough data to build the player heatmap (missing columns or no wins).")

            # -------------------------------------
            # GLOBAL ERA HEATMAP (original)
            # -------------------------------------
            if input("\n👉 Show Global Era Heatmap? (y/n): ").lower() == "y":
                print("Generating heatmap...")
                wins_per_year = df.groupby(['Year', 'Winner']).size().reset_index(name='Wins')
                if wins_per_year.empty:
                    print("⚠️ Not enough global data for heatmap.")
                else:
                    top3 = wins_per_year.sort_values(
                        ['Year', 'Wins'], ascending=[True, False]
                    ).groupby('Year').head(3)
                    pivot_df = top3.pivot(index='Year', columns='Winner', values='Wins').fillna(0)
                    plt.figure(figsize=(14, 10))
                    sns.heatmap(pivot_df, cmap='YlOrRd', annot=True, fmt='g')
                    plt.title("Top 3 Players by Wins (Yearly)")
                    plt.show()

        # -------------------------
        # OPTION 2 — COMPARE TWO PLAYERS
        # -------------------------
        elif vis_choice == "2":
            print("\n🎾 Enter name of second player to compare:")

            # Input second player
            player2 = input("👉 Player 2 name (must appear in dataset): ").strip()

            # Check if valid
            winners_unique = df['Winner'].unique()
            if player2 not in winners_unique:
                print("❌ Player not found in dataset.")
                continue

            print(f"\n📊 Comparing {selected_player} VS {player2}...")

            # Colors
            p1_color = PLAYER_COLORS.get(selected_player, DEFAULT_COLOR)
            p2_color = PLAYER_COLORS.get(player2, "#e15759")

            # Data
            p1_wins = df[df['Winner'] == selected_player]
            p2_wins = df[df['Winner'] == player2]

            # --- Comparison Graphs ---
            plt.close('all')
            fig, axes = plt.subplots(1, 2, figsize=(14, 6))

            # Wins by Surface (grouped bars)
            s1 = p1_wins['Surface'].value_counts()
            s2 = p2_wins['Surface'].value_counts()
            surfaces = sorted(set(s1.index) | set(s2.index))

            if not surfaces:
                axes[0].text(0.5, 0.5, "No surface data", ha='center', va='center')
                axes[0].set_title("Wins by Surface (Comparison)")
                axes[0].set_ylabel("Wins")
            else:
                # create positions
                x = range(len(surfaces))
                width = 0.35
                axes[0].bar([i - width/2 for i in x], [s1.get(s, 0) for s in surfaces],
                            width=width, color=p1_color, label=selected_player)
                axes[0].bar([i + width/2 for i in x], [s2.get(s, 0) for s in surfaces],
                            width=width, color=p2_color, label=player2)
                axes[0].set_xticks(x)
                axes[0].set_xticklabels(surfaces, rotation=45)
                axes[0].set_title("Wins by Surface (Comparison)")
                axes[0].set_ylabel("Wins")
                axes[0].legend()

            # Wins per Year
            y1 = p1_wins.groupby("Year").size()
            y2 = p2_wins.groupby("Year").size()
            if y1.empty and y2.empty:
                axes[1].text(0.5, 0.5, "No yearly data", ha='center', va='center')
                axes[1].set_title("Wins per Year (Comparison)")
                axes[1].set_ylabel("Wins")
            else:
                if not y1.empty:
                    sns.lineplot(x=y1.index, y=y1.values, marker="o", ax=axes[1], color=p1_color, label=selected_player)
                if not y2.empty:
                    sns.lineplot(x=y2.index, y=y2.values, marker="o", ax=axes[1], color=p2_color, label=player2)
                axes[1].set_title("Wins per Year (Comparison)")
                axes[1].set_ylabel("Wins")
                axes[1].legend()

            plt.tight_layout()
            plt.show()

            # Comparison Heatmap
            print("🔥 Generating Comparison Heatmap...")

            if {'Surface', 'Round'}.issubset(df.columns):
                heat1 = p1_wins.groupby(["Surface", "Round"]).size().reset_index(name="P1")
                heat2 = p2_wins.groupby(["Surface", "Round"]).size().reset_index(name="P2")
                merged = pd.merge(heat1, heat2, on=["Surface", "Round"], how="outer").fillna(0)

                # pivot P1 and P2
                pivot_p1 = merged.pivot(index="Surface", columns="Round", values="P1").fillna(0)
                pivot_p2 = merged.pivot(index="Surface", columns="Round", values="P2").fillna(0)

                # align indexes/columns
                all_surfaces = sorted(set(pivot_p1.index) | set(pivot_p2.index))
                all_rounds = sorted(set(pivot_p1.columns) | set(pivot_p2.columns))

                pivot_p1 = pivot_p1.reindex(index=all_surfaces, columns=all_rounds, fill_value=0)
                pivot_p2 = pivot_p2.reindex(index=all_surfaces, columns=all_rounds, fill_value=0)

                diff = pivot_p1 - pivot_p2

                plt.figure(figsize=(10, 6))
                sns.heatmap(diff, cmap="coolwarm", center=0, annot=True, fmt=".0f")
                plt.title(f"{selected_player} vs {player2} – Heatmap (Difference in Wins)")
                plt.show()
            else:
                print("⚠️ Not enough data to build comparison heatmap (missing 'Surface'/'Round' columns).")

        # -------------------------
        # SKIP VISUALS
        # -------------------------
        else:
            print("Skipping charts...")


# Run the program
if __name__ == "__main__":
    main()
