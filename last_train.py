#!/usr/bin/env python3
"""
The Last Train - A Narrative Survival/Resource Management Game
Finished & polished — copy into last_train.py and run.
Dependencies: rich (pip install rich)
Optional: pygame for sound (pip install pygame) - but sound is optional and won't break the game if missing.
"""

import random
import json
import os
import time
import sys
from datetime import datetime
from typing import Dict, List, Optional

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, BarColumn, TextColumn
    from rich.text import Text
    from rich.layout import Layout
    from rich import box
except ImportError:
    print("Installing required package 'rich'...")
    os.system(f"{sys.executable} -m pip install --quiet rich")
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, BarColumn, TextColumn
    from rich.text import Text
    from rich.layout import Layout
    from rich import box

# Try to import pygame for optional sound. If unavailable, game still runs.
try:
    import pygame
    PYGAME_AVAILABLE = True
except Exception:
    PYGAME_AVAILABLE = False

class SoundManager:
    """Optional sound manager using pygame. Keeps things safe if pygame isn't available."""
    def __init__(self):
        self.enabled = False
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init()
                self.enabled = True
                self.sounds = {}
                # No embedded synthetic tones; optionally load files if present
                # You can drop .wav files named whistle.wav, engine.wav, alert.wav, success.wav next to script
                for name in ("whistle", "engine", "alert", "success"):
                    fname = f"{name}.wav"
                    if os.path.exists(fname):
                        try:
                            self.sounds[name] = pygame.mixer.Sound(fname)
                        except Exception:
                            self.sounds[name] = None
                    else:
                        self.sounds[name] = None
            except Exception:
                self.enabled = False

    def play(self, sound_name: str):
        if not self.enabled:
            return
        snd = self.sounds.get(sound_name)
        if snd:
            try:
                snd.play()
            except Exception:
                pass

class GameState:
    """Current state of the game."""
    def __init__(self):
        self.fuel = 100
        self.morale = 75
        self.condition = 90
        self.distance_remaining = 1000
        self.passengers = 15
        self.day = 1
        self.station_number = 0
        self.score = 0
        self.events_history = []
        self.game_over = False
        self.victory = False

    def to_dict(self) -> Dict:
        return {
            'fuel': self.fuel,
            'morale': self.morale,
            'condition': self.condition,
            'distance_remaining': self.distance_remaining,
            'passengers': self.passengers,
            'day': self.day,
            'station_number': self.station_number,
            'score': self.score,
            'events_history': self.events_history,
            'game_over': self.game_over,
            'victory': self.victory
        }

    def from_dict(self, data: Dict):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

class Event:
    """Random event with choices that affect state."""
    def __init__(self, name: str, description: str, choices: List[Dict], weight: int = 1, ascii_art: Optional[str] = None):
        self.name = name
        self.description = description
        self.choices = choices
        self.weight = weight
        self.ascii_art = ascii_art

class TheLastTrain:
    def __init__(self):
        self.console = Console()
        self.state = GameState()
        self.sound_manager = SoundManager()
        self.save_file = "last_train_save.json"
        self.leaderboard_file = "leaderboard.json"
        self.events = self._create_events()
        self.running = True

    def _create_events(self) -> List[Event]:
        return [
            Event(
                "Bandit Raid",
                "Armed bandits emerge from the wasteland, demanding supplies!",
                [
                    {"text": "Fight them off", "effects": {"passengers": -5, "morale": -10, "condition": -15}, "sound": "alert"},
                    {"text": "Give them fuel", "effects": {"fuel": -20, "morale": -5}, "sound": "engine"},
                    {"text": "Negotiate peacefully", "effects": {"passengers": -2, "morale": 5}, "sound": "success"}
                ],
                weight=3,
                ascii_art="""
╔════════════════════════╗
║   ⚔️  BANDITS AHEAD!   ║
║    🚂───█───🚃🚃        ║
╚════════════════════════╝
"""),
            Event(
                "Broken Track",
                "The tracks ahead are damaged by the apocalypse!",
                [
                    {"text": "Repair quickly (risky)", "effects": {"fuel": -10, "condition": -20, "distance_remaining": -30}, "sound": "alert"},
                    {"text": "Careful repair", "effects": {"fuel": -15, "condition": -5, "distance_remaining": -20}, "sound": "engine"},
                    {"text": "Find alternate route", "effects": {"fuel": -25, "distance_remaining": -10}, "sound": "whistle"}
                ],
                weight=4,
                ascii_art="""
╔══════════════════╗
║  🔧 TRACK DAMAGE  ║
║   XXX   ═══╫╫╫══ ║
╚══════════════════╝
"""),
            Event(
                "Passenger Dispute",
                "Tensions rise among your passengers as resources dwindle.",
                [
                    {"text": "Mediate the conflict", "effects": {"morale": 10, "fuel": -5}, "sound": "success"},
                    {"text": "Ignore and keep moving", "effects": {"morale": -15, "passengers": -3}, "sound": "alert"},
                    {"text": "Share extra rations", "effects": {"morale": 15, "fuel": -10, "passengers": 2}, "sound": "success"}
                ],
                weight=3),
            Event(
                "Supply Cache Found",
                "Your scouts discover hidden supplies in an abandoned building!",
                [
                    {"text": "Take everything", "effects": {"fuel": 25, "morale": 5, "condition": 10}, "sound": "success"},
                    {"text": "Take only what's needed", "effects": {"fuel": 15, "morale": 10}, "sound": "success"},
                    {"text": "Leave supplies for others", "effects": {"morale": 20, "score": 50}, "sound": "success"}
                ],
                weight=2,
                ascii_art="""
╔════════════╗
║ SUPPLY CACHE ║
║  ⛽ 📦 🍖 💊  ║
╚════════════╝
"""),
            Event(
                "Severe Weather",
                "A massive storm approaches from the wasteland!",
                [
                    {"text": "Push through the storm", "effects": {"condition": -25, "morale": -10, "distance_remaining": -40}, "sound": "alert"},
                    {"text": "Take shelter and wait", "effects": {"fuel": -15, "morale": -5, "distance_remaining": -10}, "sound": "engine"},
                    {"text": "Use storm as cover", "effects": {"fuel": -20, "morale": 5, "distance_remaining": -50}, "sound": "whistle"}
                ],
                weight=3,
                ascii_art="""
╔══════════╗
║  ⛈️ STORM ║
║ ⚡ 🌧️ ⚡  ║
╚══════════╝
"""),
            Event(
                "Refugee Group",
                "A group of survivors waves you down, begging for passage.",
                [
                    {"text": "Take them all aboard", "effects": {"passengers": 8, "morale": 15, "fuel": -10}, "sound": "success"},
                    {"text": "Take only a few", "effects": {"passengers": 3, "morale": -5}, "sound": "whistle"},
                    {"text": "Keep moving", "effects": {"morale": -20, "score": -25}, "sound": "alert"}
                ],
                weight=3)
        ]

    def get_train_ascii(self) -> str:
        if self.state.condition > 70:
            return "🚂───█───🚃🚃🚃\n  💨💨💨"
        elif self.state.condition > 30:
            return "🚂───█───🚃🚃🚃\n  💨💨"
        else:
            return "🚂───█───🚃🚃\n  💨"

    def create_dashboard(self) -> Panel:
        # Build small progress bars and stats table
        fuel_bar = Progress(TextColumn("[bold]Fuel"), BarColumn(), TextColumn("[bold]{task.percentage:>3.0f}%"), expand=True)
        fuel_task = fuel_bar.add_task("", total=100, completed=max(0, min(100, self.state.fuel)))

        morale_bar = Progress(TextColumn("[bold]Morale"), BarColumn(), TextColumn("[bold]{task.percentage:>3.0f}%"), expand=True)
        morale_task = morale_bar.add_task("", total=100, completed=max(0, min(100, self.state.morale)))

        condition_bar = Progress(TextColumn("[bold]Condition"), BarColumn(), TextColumn("[bold]{task.percentage:>3.0f}%"), expand=True)
        condition_task = condition_bar.add_task("", total=100, completed=max(0, min(100, self.state.condition)))

        distance_progress = max(0, min(1000, self.state.distance_remaining))
        distance_bar = Progress(TextColumn("[bold]Distance"), BarColumn(), TextColumn("[bold]{task.completed}/{task.total}"), expand=True)
        distance_task = distance_bar.add_task("", total=1000, completed=1000 - distance_progress)

        stats_table = Table(show_header=False, box=box.SIMPLE)
        stats_table.add_column("Stat", style="bold")
        stats_table.add_column("Value")
        stats_table.add_row("🚂 Train", self.get_train_ascii())
        stats_table.add_row("👥 Passengers", f"[bold cyan]{self.state.passengers}[/]")
        stats_table.add_row("📅 Day", f"[bold yellow]{self.state.day}[/]")
        stats_table.add_row("🚉 Station", f"[bold magenta]{self.state.station_number}[/]")
        stats_table.add_row("🏆 Score", f"[bold green]{self.state.score}[/]")

        # Layout: left stats, right bars
        layout = Layout()
        layout.split_row(
            Layout(name="left", ratio=2),
            Layout(name="right", ratio=3)
        )
        layout["left"].update(Panel(stats_table, title="[bold cyan]Status[/]"))
        # Combine progress bars vertically in a single Panel
        bars_panel = Panel(
            Group(
                Text("Progress:", style="bold"),
                fuel_bar,
                morale_bar,
                condition_bar,
                distance_bar
            ),
            title="[bold magenta]Resources[/]"
        )
        layout["right"].update(bars_panel)
        return Panel(layout, title="[bold red]Dashboard[/]", border_style="blue")

    def show_intro(self):
        self.console.clear()
        intro_art = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    🚂───█───🚃🚃🚃   THE LAST TRAIN   🚃🚃🚃───█───🚂         ║
║                                                              ║
║         A Narrative Survival Adventure                       ║
║                                                              ║
║    You are the conductor of humanity's final hope—            ║
║    the last train escaping the ruined world.                  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
        self.console.print(Panel(intro_art, border_style="red"))
        self.console.print("\n[bold yellow]Press ENTER to begin your journey...[/]", justify="center")
        input()
        self.sound_manager.play("whistle")

    def show_station_menu(self) -> str:
        self.console.print("\n" + "="*60)
        self.console.print(f"[bold cyan]🚉 STATION {self.state.station_number + 1}[/]", justify="center")
        self.console.print("="*60)
        station_table = Table(show_header=False, box=box.ROUNDED)
        station_table.add_column("Option", style="bold")
        station_table.add_column("Action")
        station_table.add_column("Effect", style="dim")
        station_table.add_row("1", "🧑‍🤝‍🧑 Pick up passengers", "Find survivors (+passengers, -fuel)")
        station_table.add_row("2", "⛽ Refuel the train", "Get more fuel (+fuel, -time/distance)")
        station_table.add_row("3", "🔧 Repair the train", "Fix damage (+condition, -fuel)")
        station_table.add_row("4", "💾 Save game", "Save your progress")
        station_table.add_row("Q", "🚪 Quit game", "Exit to menu")
        self.console.print(station_table)
        while True:
            choice = input("\n[Station Action] Your choice (1-4, Q): ").strip().upper()
            if choice in ['1', '2', '3', '4', 'Q']:
                return choice
            self.console.print("[red]Invalid choice. Please select 1-4 or Q.[/]")

    def handle_station_action(self, choice: str):
        if choice == '1':
            found_passengers = random.randint(3, 8)
            fuel_cost = random.randint(5, 10)
            self.state.passengers += found_passengers
            self.state.fuel -= fuel_cost
            self.state.morale = min(100, self.state.morale + 5)
            self.state.score += found_passengers * 10
            self.console.print(f"[green]✅ Found {found_passengers} survivors![/]")
            self.console.print(f"[yellow]⛽ Used {fuel_cost} fuel in the search[/]")
            self.sound_manager.play("success")
        elif choice == '2':
            fuel_gained = random.randint(20, 35)
            self.state.fuel = min(100, self.state.fuel + fuel_gained)
            self.console.print(f"[green]✅ Refueled! Gained {fuel_gained} fuel[/]")
            self.console.print(f"[yellow]⏰ Time cost: some extra travel required[/]")
            self.sound_manager.play("engine")
        elif choice == '3':
            repair_amount = random.randint(15, 25)
            fuel_cost = random.randint(8, 15)
            self.state.condition = min(100, self.state.condition + repair_amount)
            self.state.fuel -= fuel_cost
            self.console.print(f"[green]✅ Repairs completed! +{repair_amount} condition[/]")
            self.console.print(f"[yellow]⛽ Used {fuel_cost} fuel for repairs[/]")
            self.sound_manager.play("success")
        elif choice == '4':
            self.save_game()
            return
        elif choice == 'Q':
            self.running = False
            return

    def trigger_random_event(self):
        if random.random() < 0.7:
            weights = [e.weight for e in self.events]
            event = random.choices(self.events, weights=weights, k=1)[0]
            self.handle_event(event)

    def handle_event(self, event: Event):
        self.console.print("\n" + "🚨" * 20)
        self.console.print(f"\n[bold red]⚠️  {event.name.upper()}  ⚠️[/]", justify="center")
        if event.ascii_art:
            self.console.print(event.ascii_art, style="yellow")
        self.console.print(f"\n[bold white]{event.description}[/]", justify="center")
        self.console.print("\n" + "🚨" * 20)
        choice_table = Table(show_header=False, box=box.ROUNDED)
        choice_table.add_column("Option", style="bold")
        choice_table.add_column("Action")
        for i, choice in enumerate(event.choices):
            choice_table.add_row(str(i + 1), choice["text"])
        self.console.print(choice_table)
        while True:
            try:
                choice_idx = int(input(f"\nYour choice (1-{len(event.choices)}): ")) - 1
                if 0 <= choice_idx < len(event.choices):
                    break
                else:
                    self.console.print("[red]Invalid choice![/]")
            except ValueError:
                self.console.print("[red]Please enter a number![/]")
        chosen_action = event.choices[choice_idx]
        effects = chosen_action.get("effects", {})
        self.console.print(f"\n[cyan]You chose: {chosen_action['text']}[/]")
        for stat, change in effects.items():
            # allow stat names that map to GameState attributes
            if hasattr(self.state, stat):
                old = getattr(self.state, stat)
                setattr(self.state, stat, max(0, old + change))
                new = getattr(self.state, stat)
                if change > 0:
                    self.console.print(f"[green]📈 {stat.title()}: {old} → {new} (+{change})[/]")
                elif change < 0:
                    self.console.print(f"[red]📉 {stat.title()}: {old} → {new} ({change})[/]")
            else:
                # If it's a stat not on GameState (like 'score'), apply directly if present in dict
                if stat == "score":
                    old = self.state.score
                    self.state.score = max(0, old + change)
                    self.console.print(f"[green]🏆 Score: {old} → {self.state.score} ({'+' if change>=0 else ''}{change})[/]")
        if "sound" in chosen_action:
            self.sound_manager.play(chosen_action["sound"])
        self.state.events_history.append({"day": self.state.day, "event": event.name, "choice": chosen_action["text"]})
        input("\n[dim]Press ENTER to continue...[/]")

    def advance_turn(self):
        travel_fuel = random.randint(8, 15)
        travel_distance = random.randint(40, 80)
        self.state.fuel -= travel_fuel
        self.state.distance_remaining -= travel_distance
        self.state.day += 1
        self.state.station_number += 1
        self.state.condition -= random.randint(1, 5)
        morale_change = random.randint(-3, 3)
        self.state.morale += morale_change
        # Clamp important stats
        self.state.fuel = max(0, min(100, self.state.fuel))
        self.state.morale = max(0, min(100, self.state.morale))
        self.state.condition = max(0, min(100, self.state.condition))
        self.state.distance_remaining = max(0, self.state.distance_remaining)
        self.console.print(f"\n[blue]🚂 Traveled {travel_distance} km (fuel: -{travel_fuel})[/]")

    def check_game_over(self) -> bool:
        if self.state.distance_remaining <= 0:
            if self.state.passengers > 0:
                self.state.victory = True
                self.state.score += self.state.passengers * 50
                self.state.score += max(0, self.state.fuel) * 2
            else:
                self.state.victory = False
            self.state.game_over = True
            return True
        if (self.state.fuel <= 0 or self.state.morale <= 0 or
            self.state.condition <= 0 or self.state.passengers <= 0):
            self.state.victory = False
            self.state.game_over = True
            return True
        return False

    def show_game_over(self):
        self.console.clear()
        if self.state.victory:
            victory_art = f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    🎉🎊🎉  VICTORY! YOU MADE IT!  🎉🎊🎉                    ║
║                                                              ║
║    🚂───█───🚃🚃🚃    🏁 SAFE ZONE REACHED! 🏁            ║
║                                                              ║
║    👥 Survivors Saved: {self.state.passengers:<3}                            ║
║    🏆 Final Score: {self.state.score:<6}                           ║
║    📅 Journey Days: {self.state.day:<3}                           ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
            self.console.print(Panel(victory_art, border_style="green"))
            self.sound_manager.play("success")
        else:
            failure_reason = "Unknown"
            if self.state.fuel <= 0:
                failure_reason = "The train ran out of fuel..."
            elif self.state.morale <= 0:
                failure_reason = "Passenger morale collapsed..."
            elif self.state.condition <= 0:
                failure_reason = "The train broke down beyond repair..."
            elif self.state.passengers <= 0:
                failure_reason = "All passengers were lost..."
            failure_art = f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    💀💀💀  GAME OVER  💀💀💀                                ║
║                                                              ║
║    🚂───X───🚃🚃🚃      The Last Train Falls Silent...      ║
║                                                              ║
║         {failure_reason:<50} ║
║                                                              ║
║    📅 Survived: {self.state.day} days                                         ║
║    🏆 Final Score: {self.state.score}                                        ║
║    📍 Distance Left: {self.state.distance_remaining} km                               ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
            self.console.print(Panel(failure_art, border_style="red"))
            self.sound_manager.play("alert")
        self.update_leaderboard()
        input("\nPress ENTER to continue...")

    def save_game(self):
        try:
            save_data = {'state': self.state.to_dict(), 'timestamp': datetime.now().isoformat()}
            with open(self.save_file, 'w') as f:
                json.dump(save_data, f, indent=2)
            self.console.print("[green]✅ Game saved successfully![/]")
        except Exception as e:
            self.console.print(f"[red]❌ Failed to save game: {e}[/]")
        input("Press ENTER to continue...")

    def load_game(self) -> bool:
        try:
            if not os.path.exists(self.save_file):
                self.console.print("[yellow]No save file found.[/]")
                input("Press ENTER to continue...")
                return False
            with open(self.save_file, 'r') as f:
                save_data = json.load(f)
            self.state.from_dict(save_data['state'])
            self.console.print("[green]✅ Game loaded successfully![/]")
            input("Press ENTER to continue...")
            return True
        except Exception as e:
            self.console.print(f"[red]❌ Failed to load game: {e}[/]")
            input("Press ENTER to continue...")
            return False

    def update_leaderboard(self):
        try:
            leaderboard = []
            if os.path.exists(self.leaderboard_file):
                with open(self.leaderboard_file, 'r') as f:
                    leaderboard = json.load(f)
            leaderboard.append({
                'score': self.state.score,
                'passengers_saved': self.state.passengers,
                'days_survived': self.state.day,
                'victory': self.state.victory,
                'date': datetime.now().isoformat()
            })
            leaderboard.sort(key=lambda x: x['score'], reverse=True)
            leaderboard = leaderboard[:10]
            with open(self.leaderboard_file, 'w') as f:
                json.dump(leaderboard, f, indent=2)
        except Exception as e:
            # silently ignore leaderboard errors
            pass

    def show_leaderboard(self):
        self.console.clear()
        if not os.path.exists(self.leaderboard_file):
            self.console.print("[yellow]No scores recorded yet![/]")
            input("Press ENTER to continue...")
            return
        with open(self.leaderboard_file, 'r') as f:
            leaderboard = json.load(f)
        if not leaderboard:
            self.console.print("[yellow]No scores recorded yet![/]")
            input("Press ENTER to continue...")
            return
        table = Table(title="🏆 HIGH SCORES - THE LAST TRAIN 🏆", box=box.ROUNDED)
        table.add_column("Rank", justify="center", style="bold")
        table.add_column("Score", justify="right", style="bold yellow")
        table.add_column("Survivors", justify="center", style="cyan")
        table.add_column("Days", justify="center", style="magenta")
        table.add_column("Status", justify="center")
        table.add_column("Date", style="dim")
        for i, entry in enumerate(leaderboard, 1):
            status = "🎉 VICTORY" if entry.get('victory') else "💀 LOST"
            date_str = entry.get('date', '')[:10]
            table.add_row(str(i), str(entry.get('score', 0)), str(entry.get('passengers_saved', 0)),
                          str(entry.get('days_survived', 0)), status, date_str)
        self.console.print(table)
        input("\nPress ENTER to continue...")

    def main_menu(self):
        while True:
            self.console.clear()
            menu_art = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    🚂───█───🚃🚃🚃   THE LAST TRAIN   🚃🚃🚃───█───🚂         ║
║                                                              ║
║                   Main Menu                                  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
            self.console.print(Panel(menu_art, border_style="blue"))
            menu_table = Table(show_header=False, box=box.ROUNDED)
            menu_table.add_column("Option", style="bold")
            menu_table.add_column("Action")
            menu_table.add_row("1", "🚀 New Game")
            menu_table.add_row("2", "📁 Load Game")
            menu_table.add_row("3", "🏆 Leaderboard")
            menu_table.add_row("4", "❓ How to Play")
            menu_table.add_row("Q", "🚪 Quit")
            self.console.print(menu_table)
            choice = input("\nYour choice: ").strip().upper()
            if choice == '1':
                self.start_new_game()
            elif choice == '2':
                if self.load_game():
                    self.game_loop()
            elif choice == '3':
                self.show_leaderboard()
            elif choice == '4':
                self.show_instructions()
            elif choice == 'Q':
                self.console.print("[yellow]Thanks for playing The Last Train![/]")
                break
            else:
                self.console.print("[red]Invalid choice![/]")
                time.sleep(0.8)

    def show_instructions(self):
        self.console.clear()
        instructions = """
╔══════════════════════════════════════════════════════════════╗
║                     HOW TO PLAY                              ║
╠══════════════════════════════════════════════════════════════╣
║  🎯 OBJECTIVE:                                               ║
║     • Guide your train 1000km to the Safe Zone               ║
║     • Keep at least 1 passenger alive                        ║
║     • Manage Fuel, Morale, and Train Condition               ║
║                                                              ║
║  🚉 AT EACH STATION:                                         ║
║     • Pick up passengers (gain survivors, use fuel)          ║
║     • Refuel (gain fuel, lose travel efficiency)             ║
║     • Repair train (improve condition, use fuel)             ║
║                                                              ║
║  ⚠️  RANDOM EVENTS:                                           ║
║     • Bandit raids, broken tracks, storms                    ║
║     • Your choices determine the outcome                     ║
║                                                              ║
║  💀 GAME OVER IF:                                            ║
║     • Fuel = 0, Morale = 0, Condition = 0, or Passengers = 0 ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
        self.console.print(Panel(instructions, border_style="cyan"))
        input("\nPress ENTER to return to menu...")

    def start_new_game(self):
        self.state = GameState()
        self.show_intro()
        self.game_loop()

    def game_loop(self):
        self.running = True
        while self.running and not self.state.game_over:
            self.console.clear()
            dashboard = self.create_dashboard()
            self.console.print(dashboard)
            if self.check_game_over():
                break
            choice = self.show_station_menu()
            if not self.running:
                break
            self.handle_station_action(choice)
            if not self.running or choice in ['4', 'Q']:
                break
            self.advance_turn()
            self.trigger_random_event()
            if self.check_game_over():
                break
            # small pause so player sees updates (can remove for faster runs)
            time.sleep(0.25)
        if self.state.game_over:
            self.show_game_over()

def main():
    try:
        game = TheLastTrain()
        game.main_menu()
    except KeyboardInterrupt:
        print("\n\nThanks for playing The Last Train!")
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Please check your Python environment and try again.")

if __name__ == "__main__":
    # Group import used for progress grouping if available
    try:
        from rich.console import Group
    except Exception:
        # fallback
        class Group:
            def __init__(self, *args):
                self._args = args
            def __rich_console__(self, console, options):
                for a in self._args:
                    yield a
    main()
