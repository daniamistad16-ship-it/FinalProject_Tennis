import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import random

# --- DATA ACQUISITION & REAL DATA LOADING TEMPLATE ---

def load_real_data():
    """
    TEMPLATE: Load and process real tennis data from a CSV file.

    IMPORTANT: You must adjust the file path and column names to match
    your specific dataset (e.g., atp_tennis_matches.csv).
    """
    
    # 1. Define the path to your primary data file (e.g., match results)
    # REPLACE 'atp_tennis_matches.csv' with the actual filename you downloaded.
    file_path = 'atp_tennis_matches.csv'
    
    try:
        # Load the raw data
        df_raw = pd.read_csv(file_path, low_memory=False)
        print(f"Successfully loaded data from {file_path}. Shape: {df_raw.shape}")
        
        # 2. Rename columns to match the EXPECTED names used in calculate_career_stats().
        # This is the most important step for the real data to work with the existing logic.
        
        # You need to identify the corresponding column names in your CSV:
        df = df_raw.rename(columns={
            # Example mapping for a standard dataset:
            'winner_name': 'Player',          # The column containing the winning player's name
            'tourney_id': 'Trophy_ID',        # Used to identify unique tournaments/trophies
            'tourney_surface': 'Surface',     # Surface type (Hard, Clay, Grass)
            'tourney_year': 'Year',           # The year the match was played
            'winner_prize': 'Match_Prize_Money' # Prize money (if available per winner)
        }, inplace=False)

        # 3. Create 'Result' and 'Trophy' columns (required by analysis functions)
        df['Result'] = 'Win'
        # Simplify Trophy calculation: a win means they were a final winner in a tournament
        # In a real scenario, you'd filter for the 'F' (Final) round, but for this template, 
        # we'll assume any win is an arbitrary "match prize" for simplicity.
        # You should improve this by checking the 'round' column in your final data.
        df['Trophy'] = (df['Trophy_ID'].duplicated(keep='first')) # Mock logic for unique trophy count

        # Select only the columns needed for the analysis (plus any necessary IDs)
        required_columns = ['Player', 'Year', 'Surface', 'Result', 'Trophy', 'Match_Prize_Money']
        
        # Filter the DataFrame to only include these columns
        return df[df['Player'].notna() & df['Surface'].notna()][required_columns]

    except FileNotFoundError:
        print(f"ERROR: File not found at '{file_path}'. Please ensure the CSV is in the same directory.")
        return None
    except KeyError as e:
        print(f"ERROR: Missing expected column after renaming: {e}. Check your column mapping in load_real_data().")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while loading data: {e}")
        return None


def create_mock_data():
    """
    Creates a mock DataFrame structured like real ATP/WTA data.
    
    NOTE: This is now a fallback. The final project should use load_real_data()
    once the user has placed the CSV file in the project folder.
    """
    print("--- Using MOCK DATA as a FALLBACK ---")
    
    # Define three sample players for demonstration
    players = [
        ("Rafael Nadal", 2005, 2024, 'Clay', 92, 14, 134_000_000),
        ("Roger Federer", 1998, 2022, 'Grass', 82, 10, 130_000_000),
        ("Novak Djokovic", 2003, 2024, 'Hard', 100, 15, 185_000_000),
    ]

    # Surfaces and results for simulation
    surfaces = ['Hard', 'Clay', 'Grass', 'Carpet']
    results = ['Win', 'Loss']
    
    data = []
    
    # Generate 500 records for each player to simulate a career
    for name, start_year, end_year, favorite_surface, base_wins, base_trophies, base_prize in players:
        # Simulate Win/Loss Records across surfaces
        for _ in range(500):
            surface = random.choice(surfaces)
            
            # Simulate a higher win rate on the player's favorite surface
            win_rate = 0.85 if surface == favorite_surface else 0.70
            result = 'Win' if random.random() < win_rate else 'Loss'
            
            year = random.randint(start_year, end_year)
            
            # Simulate prize money for match (simplified)
            prize_money = random.randint(1000, 5000) if result == 'Win' else 500
            
            # Simulate trophies (rare event)
            is_trophy = True if result == 'Win' and random.random() < 0.05 else False

            data.append({
                'Player': name,
                'Year': year,
                'Surface': surface,
                'Result': result,
                'Trophy': is_trophy,
                'Match_Prize_Money': prize_money,
            })
            
    df = pd.DataFrame(data)
    
    # Convert 'Year' to integer
    df['Year'] = df['Year'].astype(int)
    
    return df

# --- CORE ANALYSIS FUNCTIONS ---

def calculate_career_stats(df, player_name):
    """Calculates key career statistics for a given player."""
    
    player_data = df[df['Player'] == player_name].copy()
    
    if player_data.empty:
        return None, "Player not found or data missing."

    # 1. Overall Win Rate
    total_matches = len(player_data)
    total_wins = player_data[player_data['Result'] == 'Win'].shape[0]
    win_rate = (total_wins / total_matches) * 100 if total_matches > 0 else 0

    # 2. Total Trophies & Prize Money
    total_trophies = player_data['Trophy'].sum()
    total_prize_money = player_data['Match_Prize_Money'].sum()
    
    # 3. Surface Win Rates (for Pie Chart)
    surface_stats = player_data.groupby('Surface').agg(
        Total_Matches=('Result', 'count'),
        Wins=('Result', lambda x: (x == 'Win').sum())
    )
    surface_stats['Win_Rate'] = (surface_stats['Wins'] / surface_stats['Total_Matches']) * 100
    surface_stats = surface_stats.sort_values(by='Win_Rate', ascending=False)
    
    # Handle case where there are no surface stats (shouldn't happen with real data)
    favorite_surface = surface_stats.index[0] if not surface_stats.empty else "N/A"
    
    # 4. Trophies by Year (for Bar Chart)
    trophies_by_year = player_data[player_data['Trophy'] == True].groupby('Year').size().reset_index(name='Trophies')
    
    stats = {
        'Overall_Win_Rate': win_rate,
        'Total_Matches': total_matches,
        'Total_Wins': total_wins,
        'Total_Trophies': total_trophies,
        'Total_Prize_Money': total_prize_money,
        'Favorite_Surface': favorite_surface,
        'Surface_Win_Stats': surface_stats,
        'Trophies_By_Year': trophies_by_year
    }
    
    return stats, None

# --- VISUALIZATION FUNCTIONS ---

def create_summary_visuals(stats, player_name):
    """Generates and saves the required plots."""
    
    # Set a professional plot style
    plt.style.use('seaborn-v0_8-whitegrid')
    
    # Create a figure with two subplots
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    plt.suptitle(f"Career Summary & Key Statistics for {player_name}", fontsize=20, fontweight='bold', y=1.02)

    # --- Plot 1: Trophies by Year (Bar Chart) ---
    trophy_data = stats['Trophies_By_Year']
    
    if not trophy_data.empty:
        axes[0].bar(trophy_data['Year'], trophy_data['Trophies'], color='#3498db', edgecolor='black')
        axes[0].set_title('Trophies Won Per Year', fontsize=14)
        axes[0].set_xlabel('Year')
        axes[0].set_ylabel('Number of Trophies')
        # Ensure year labels are readable
        if len(trophy_data['Year']) > 15:
            axes[0].set_xticks(trophy_data['Year'][::2]) # Show every other year
        else:
            axes[0].set_xticks(trophy_data['Year'])
            
        axes[0].tick_params(axis='x', rotation=45)
        axes[0].grid(axis='y', linestyle='--', alpha=0.7)
    else:
        axes[0].text(0.5, 0.5, 'No Trophy Data Available', ha='center', va='center', fontsize=14)
        axes[0].set_title('Trophies Won Per Year', fontsize=14)
    
    # --- Plot 2: Win Rate by Surface (Pie Chart) ---
    surface_stats = stats['Surface_Win_Stats']
    
    if not surface_stats.empty:
        # Prepare data for the pie chart
        pie_data = surface_stats['Win_Rate']
        labels = [f"{surf} ({rate:.1f}%)" for surf, rate in zip(surface_stats.index, surface_stats['Win_Rate'])]
        
        # Colors for surfaces
        colors = {
            'Clay': '#e74c3c',  # Reddish
            'Hard': '#34495e',  # Dark Blue/Grey
            'Grass': '#2ecc71', # Green
            'Carpet': '#f39c12' # Orange/Yellow
        }
        
        pie_colors = [colors.get(surf, '#bdc3c7') for surf in surface_stats.index]
        
        axes[1].pie(
            pie_data, 
            labels=labels, 
            autopct='%1.1f%%', 
            startangle=90, 
            colors=pie_colors, 
            wedgeprops={'edgecolor': 'black', 'linewidth': 1}
        )
        axes[1].set_title('Win Rate Distribution by Surface', fontsize=14)
        axes[1].axis('equal') # Equal aspect ratio ensures that pie is drawn as a circle.
    else:
        axes[1].text(0.5, 0.5, 'No Surface Data Available', ha='center', va='center', fontsize=14)
        axes[1].set_title('Win Rate Distribution by Surface', fontsize=14)

    # Adjust layout to prevent overlap
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    # Save the plot to a file
    output_filename = f"{player_name.replace(' ', '_')}_Career_Summary.png"
    plt.savefig(output_filename)
    plt.close(fig) # Close the figure to free up memory
    
    return output_filename

# --- MAIN EXECUTION LOGIC ---

def run_tennis_analyst():
    """Main function to run the tennis career analyst tool."""
    
    print("--- Python Tennis Career Analyst ---")
    print("Attempting to load real data...")
    
    full_data = load_real_data()

    if full_data is None:
        print("\nCould not load real data (FileNotFound or KeyError). Falling back to mock data.")
        full_data = create_mock_data()
        
    if full_data is None or full_data.empty:
        print("FATAL: Data could not be loaded or generated. Exiting.")
        return

    # Get list of players available in the data
    available_players = sorted(full_data['Player'].unique().tolist())
    print(f"\nData loaded successfully. {len(available_players):,} players available.")
    
    # Show only a few sample players if the list is huge
    if len(available_players) > 5:
        sample_players = available_players[:3] + ['...'] + available_players[-3:]
        print(f"Sample players: {', '.join(sample_players)}")
    else:
        print(f"Available players: {', '.join(available_players)}")


    while True:
        try:
            player_input = input("\nEnter the full name of a tennis player (or 'exit'): ").strip()
            
            if player_input.lower() == 'exit':
                print("Exiting application. Goodbye!")
                break
            
            if not player_input:
                continue

            # Check if the input player exists in the data
            if player_input not in available_players:
                print(f"'{player_input}' not found. Please try again. Names are case sensitive.")
                continue

            # 1. Calculate Statistics
            print(f"\nAnalyzing career statistics for {player_input}...")
            stats, error = calculate_career_stats(full_data, player_input)

            if error:
                print(f"ERROR: {error}")
                continue

            # 2. Display Text Summary
            print("\n" + "="*50)
            print(f"🏆 Career Overview: {player_input.upper()}")
            print("="*50)
            print(f"• Total Trophies: {int(stats['Total_Trophies']):,}")
            print(f"• Overall Win Rate: {stats['Overall_Win_Rate']:.2f}% ({stats['Total_Wins']:,} Wins)")
            print(f"• Total Matches Played: {stats['Total_Matches']:,}")
            
            # Format prize money as currency (simplified)
            prize_money_usd = f"${stats['Total_Prize_Money']:,}"
            print(f"• Estimated Prize Money Won: {prize_money_usd}")
            print(f"• Favorite Surface: {stats['Favorite_Surface']} (Highest Win Rate)")
            print("="*50)

            # 3. Generate Visualizations
            print("Generating career graphics...")
            output_file = create_summary_visuals(stats, player_input)
            print(f"✅ Success! Career summary charts saved to: {output_file}")
            print("Check your project folder for the PNG file!")
            
        except Exception as e:
            print(f"\nAn unexpected error occurred during analysis: {e}")
            break

# Execute the main function
if __name__ == "__main__":
    # Ensure the required packages are installed
    try:
        run_tennis_analyst()
    except ImportError as e:
        print("\n--- CRITICAL ERROR ---")
        print(f"Missing required library: {e}. Please install it.")
        print("You can install all necessary libraries using:")
        print("pip install pandas matplotlib numpy")