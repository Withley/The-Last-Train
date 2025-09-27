# 🚂 The Last Train
*A Narrative Survival/Resource Management Game*

![Game Preview](https://img.shields.io/badge/Platform-Terminal-blue)
![Python](https://img.shields.io/badge/Python-3.7+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🎮 About The Game

You are the conductor of humanity's final hope—the last train escaping a ruined world. Navigate through a post-apocalyptic wasteland, manage scarce resources, and make crucial decisions that will determine the fate of your passengers.

**Can you reach the Safe Zone with survivors intact?**

## ✨ Features

### 🎯 Core Gameplay
- **Resource Management**: Balance Fuel, Morale, Train Condition, and Passenger Count
- **Strategic Decisions**: Every choice matters in this survival experience  
- **Random Events**: Dynamic storytelling with bandit raids, broken tracks, severe weather, and more
- **Multiple Endings**: Victory or defeat based on your decisions and resource management

### 🎨 Immersive Experience
- **Rich Terminal UI**: Colorful progress bars, ASCII art, and formatted tables using the `rich` library
- **Sound Effects**: Atmospheric audio cues using `pygame` (optional)
- **Dynamic ASCII Art**: Train condition changes based on damage level
- **Narrative Elements**: Dramatic intro/outro sequences with engaging storylines

### 💾 Game Features
- **Save/Load System**: Continue your journey anytime with JSON-based save files
- **Leaderboard**: Track high scores and compare your survival skills
- **Event History**: Review past decisions and their consequences
- **Tutorial**: Built-in instructions for new players

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Quick Start
1. **Clone or Download** this repository
2. **Navigate** to the game directory:
   ```bash
   cd the-last-train
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the Game**:
   ```bash
   python last_train.py
   ```

### Manual Installation (if pip install fails)
```bash
pip install rich pygame keyboard
python last_train.py
```

## 🎲 How to Play

### 🎯 Objective
- Guide your train **1000km** to the Safe Zone
- Keep **at least 1 passenger** alive
- Manage **4 critical resources**: Fuel, Morale, Train Condition, Distance

### 🚉 Station Actions
At each station, choose one action:

1. **🧑‍🤝‍🧑 Pick up Passengers**: Find survivors (+passengers, -fuel)
2. **⛽ Refuel the Train**: Get more fuel (+fuel, -time) 
3. **🔧 Repair the Train**: Fix damage (+condition, -fuel)
4. **💾 Save Game**: Save your progress
5. **🚪 Quit**: Exit to main menu

### ⚠️ Random Events
After each station, face unpredictable challenges:
- **Bandit Raids**: Fight, negotiate, or pay tribute
- **Broken Tracks**: Repair quickly or find alternate routes  
- **Severe Weather**: Push through storms or take shelter
- **Refugee Groups**: Help survivors or conserve resources
- **Supply Caches**: Discover valuable resources

### 💀 Game Over Conditions
The journey ends if any resource reaches zero:
- **Fuel = 0**: Train stops in the wasteland
- **Morale = 0**: Passengers lose hope and abandon the train
- **Condition = 0**: Train breaks down beyond repair  
- **Passengers = 0**: No one left to save

### 🏆 Scoring System
- **+10 points** per passenger rescued
- **+50 points** per passenger saved at journey's end
- **+2 points** per unit of fuel remaining
- **Bonus/Penalty** for moral choices during events

## 🎨 Game Features Deep Dive

### 📊 Dashboard HUD
The game displays a comprehensive dashboard showing:
- **Progress Bars**: Visual representation of Fuel, Morale, Condition, and Distance
- **Train ASCII Art**: Dynamic visualization that changes based on train condition
- **Statistics Table**: Current passengers, day, station number, and score
- **Status Updates**: Real-time feedback on your actions and their consequences

### 🎭 Event System
The game features a sophisticated event system with:
- **Weighted Probability**: Different events have different chances of occurring
- **Meaningful Choices**: Each decision has realistic consequences
- **ASCII Art**: Visual representations for major events
- **Sound Effects**: Audio cues that enhance immersion
- **Branching Outcomes**: Multiple solutions to each challenge

### 💾 Persistence Features
- **Save System**: JSON-based save files that preserve complete game state
- **Leaderboard**: Local high score tracking with detailed statistics
- **Event History**: Track of all major decisions and their outcomes
- **Progress Indicators**: Visual feedback on journey completion

## 🔧 Technical Details

### Dependencies
- **rich**: Advanced terminal formatting, progress bars, and colored text
- **pygame**: Sound effects and audio management (optional)
- **keyboard**: Enhanced input handling (optional)

### File Structure
```
the-last-train/
├── last_train.py           # Main game file
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── last_train_save.json   # Save file (created when you save)
└── leaderboard.json       # High scores (created after first game)
```

### Save Files
- **last_train_save.json**: Contains complete game state including resources, progress, and event history
- **leaderboard.json**: Stores top 10 high scores with detailed statistics

## 🎵 Sound Effects

The game includes optional sound effects using pygame:
- **Train Whistle**: Journey start and certain events
- **Engine Chugging**: Refueling and mechanical actions
- **Alert Sounds**: Dangerous events and warnings
- **Success Tones**: Positive outcomes and victories

*Note: Sound effects will automatically disable if pygame is not available*

## 🐛 Troubleshooting

### Common Issues

**"ModuleNotFoundError: No module named 'rich'"**
```bash
pip install rich
```

**Sound not working**
- Install pygame: `pip install pygame`
- The game will work without sound if pygame is unavailable

**Keyboard input issues**
- The game uses standard input() and will work without the keyboard library
- For enhanced input, install: `pip install keyboard`

**Permission errors on save files**
- Ensure you have write permissions in the game directory
- The game creates save files in the same directory as the script

## 🎮 Tips for Success

1. **Balance is Key**: Don't focus on just one resource—you need all four to survive
2. **Moral Choices Matter**: Helping others often provides long-term benefits
3. **Plan Ahead**: Consider the long-term consequences of each decision
4. **Save Often**: Use the save feature to preserve your progress
5. **Learn from Events**: Each playthrough teaches you about different event outcomes
6. **Resource Management**: Sometimes it's worth taking risks to gain valuable resources

## 🏆 Achievement Ideas

Try to achieve these unofficial goals:
- **Perfect Run**: Reach the Safe Zone with all original passengers
- **Efficient Journey**: Complete the game in minimum days
- **Resource Master**: Finish with high levels in all resources
- **Moral Compass**: Make consistently altruistic choices
- **Survivor**: Complete the game on your first attempt

## 📜 Credits

- **Game Design**: AI Assistant
- **Rich Terminal Library**: [Textualize](https://github.com/Textualize/rich)
- **Sound Effects**: pygame library
- **Inspiration**: Post-apocalyptic survival games and interactive fiction

## 📝 License

This project is released under the MIT License. Feel free to modify, distribute, and use for educational purposes.

---

**🚂 All aboard The Last Train! The wasteland awaits, and humanity's future depends on you. 🚂**

*Good luck, Conductor. The journey begins now...*
