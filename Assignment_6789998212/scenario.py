#
# scenario.py - builds a Competition from a scenario file or from
#               prompted input
#
# Student Name : ajwang-kajwang
# Student ID   : 6789998212
#
# Everything that decides WHAT is simulated - how many competitors, which
# clubs, which belts exist, which events run on which mats - lives in a
# scenario, not in the code.  A scenario comes from a JSON file, an
# optional CSV roster of competitors, or from answering a few validated
# prompts.
#
# Sources / self-citation
# -----------------------
# * ask_int() is the input validation pattern from Practical Test 1
#   (dojo.py Activity 3): read, then re-prompt WHILE the answer is out
#   of range.  It needs no while True and no break, unlike the
#   try/except version I used in PracTest2 wandering4.py.
# * name_defs from the given training.py is kept as the first few
#   names, so the small scenario still reads like the practical.
#
import csv
import json
import os
import random

import events as ev
import pykwondo as pk

# The given name list from training.py, extended so that larger
# scenarios do not run out of names.
NAME_DEFS = ["Panda", "Tigress", "Crane", "Viper", "Mantis", "Monkey"]
EXTRA_NAMES = [
    "Ayla", "Bao", "Cleo", "Dara", "Eshe", "Fen", "Gita", "Hana", "Ines",
    "Jae", "Kofi", "Lian", "Mira", "Noor", "Omar", "Pia", "Quon", "Rafa",
    "Sami", "Tomas", "Uma", "Vik", "Wren", "Xiu", "Yara", "Zane", "Arin",
    "Bela", "Ciro", "Dita", "Enzo", "Faye", "Goro", "Hugo", "Iris", "Juno",
]
SURNAME_INITIALS = list("ABCDEFGHIJKLMNOPRSTVWZ")

DEFAULT_SKILL_CHANCE = {
    "pattern": 1.0,
    "team_pattern": 0.85,
    "sparring": 0.7,
    "breaking": 0.5,
}

REQUIRED_KEYS = ("name", "clubs", "events")


# --- validated input (PracTest1 dojo.py pattern) -----------------------
def parse_int(text):
    """returns text as an int, or None if it is not a whole number"""
    cleaned = text.strip()
    digits = cleaned[1:] if cleaned[:1] in "+-" else cleaned
    return int(cleaned) if digits.isdigit() else None


def ask_int(prompt, low, high, reader=input, writer=print):
    """asks for a whole number and re-asks until it is in range

    The PracTest1 validation loop: read once, then loop WHILE the
    answer is unusable.  No while True, no break, and a non-numeric
    answer is treated as out of range rather than crashing.

    Parameters
    ----------
    prompt : str
        what to ask for, without the range
    low, high : int
        inclusive acceptable range
    reader : callable
        input function - replaced in tests
    writer : callable
        print function - replaced in tests

    Returns
    -------
    int
        a value between low and high
    """
    question = f"{prompt} ({low}-{high}): "
    value = parse_int(reader(question))
    while value is None or value < low or value > high:
        writer("Out of range, please re-enter...")
        value = parse_int(reader(question))
    return value


def ask_yes_no(prompt, default=True, reader=input):
    """asks a yes/no question, empty answer taking the default"""
    suffix = "[Y/n]" if default else "[y/N]"
    answer = reader(f"{prompt} {suffix}: ").strip().lower()
    return default if answer == "" else answer.startswith("y")


# --- competitor generation ---------------------------------------------
def name_pool(count, rng):
    """returns count distinct competitor names"""
    names = list(NAME_DEFS) + list(EXTRA_NAMES)
    rng.shuffle(names)
    chosen = []
    for number in range(count):
        base = names[number % len(names)]
        initial = SURNAME_INITIALS[(number // len(names))
                                  % len(SURNAME_INITIALS)]
        chosen.append(base if number < len(names) else f"{base} {initial}")
    return chosen


def weighted_rank(ranks, weights, rng):
    """picks a rank name, honouring per-rank weights from the scenario"""
    names = ranks.names()
    if not weights:
        return rng.choice(names)
    chances = [max(0.0, float(weights.get(name, 0))) for name in names]
    if sum(chances) <= 0:
        return rng.choice(names)
    return rng.choices(names, weights=chances, k=1)[0]


def build_generated_roster(settings, clubs, ranks, rng):
    """creates a randomised, varied set of competitors

    Parameters
    ----------
    settings : dict
        the scenario's 'competitors' block
    clubs : list
        club names
    ranks : RankSystem
    rng : random.Random

    Returns
    -------
    list
        list of dicts, one per competitor, ready for build_competitors()
    """
    count = int(settings.get("count", 20))
    low_age, high_age = settings.get("age_range", [10, 55])
    weights = settings.get("rank_weights", {})
    chances = dict(DEFAULT_SKILL_CHANCE)
    chances.update(settings.get("skill_chance", {}))
    names = name_pool(count, rng)
    roster = []
    for number in range(count):
        rank = weighted_rank(ranks, weights, rng)
        skills = [skill for skill, chance in chances.items()
                  if rng.random() < chance]
        roster.append({
            "id": number + 1,
            "name": names[number],
            "age": rng.randint(int(low_age), int(high_age)),
            "club": clubs[number % len(clubs)],
            "rank": rank,
            "skills": skills if skills else ["pattern"],
            "form": round(rng.uniform(0.85, 1.15), 3),
        })
    return roster


def load_roster(path):
    """reads a competitor roster from a CSV input file

    Columns: id, name, age, club, rank, skills, form.  `skills` is a
    semicolon separated list, `id` and `form` are optional.

    Returns
    -------
    list
        list of competitor dicts
    """
    if not os.path.exists(path):
        raise ValueError(f"roster file not found: {path}")
    roster = []
    with open(path, newline="", encoding="utf-8") as handle:
        for line_no, row in enumerate(csv.DictReader(handle), start=2):
            missing = [key for key in ("name", "age", "club", "rank")
                       if not row.get(key)]
            if missing:
                raise ValueError(f"{path} line {line_no}: missing {missing}")
            listed = row.get("skills", "").split(";")
            skills = [item.strip() for item in listed if item.strip()]
            roster.append({
                "id": int(row["id"]) if row.get("id") else len(roster) + 1,
                "name": row["name"].strip(),
                "age": int(row["age"]),
                "club": row["club"].strip(),
                "rank": row["rank"].strip(),
                "skills": skills if skills else ["pattern"],
                "form": float(row["form"]) if row.get("form") else 1.0,
            })
    if not roster:
        raise ValueError(f"{path} has no competitors in it")
    return roster


def build_competitors(roster, venue, clubs, ranks):
    """turns roster dicts into Competitors standing in their club areas

    Each club's members are spread over that club's area of the venue,
    and that spot becomes the competitor's home - where they wait, and
    where they walk back to after an event.
    """
    by_club = {}
    for entry in roster:
        by_club.setdefault(entry["club"], []).append(entry)
    competitors = []
    for club_name, entries in by_club.items():
        if club_name not in clubs:
            raise ValueError(f"competitor in unknown club {club_name!r}, "
                             f"clubs are {sorted(clubs)}")
        area = venue.area(clubs[club_name].area_name)
        places = pk.standing_places(area, len(entries))
        for entry, place in zip(entries, places):
            if entry["rank"] not in ranks.names():
                raise ValueError(
                    f"competitor {entry['name']!r} has unknown rank "
                    f"{entry['rank']!r}, ranks are {ranks.names()}")
            competitor = pk.Competitor(
                entry["id"], entry["name"], entry["age"], club_name,
                entry["rank"], place, skills=entry["skills"],
                form=entry.get("form", 1.0))
            clubs[club_name].add(competitor)
            competitors.append(competitor)
    competitors.sort(key=lambda c: c.comp_id)
    return competitors


# --- the scenario itself ------------------------------------------------
def default_config(competitors=24, clubs=3, event_count=4, steps=300,
                   seed=None):
    """returns a ready-to-run scenario dictionary

    Used both as the answer to the prompts and as the starting point
    for the scenario files, so the two paths cannot drift apart.
    """
    club_names = ["Jade Palace", "Iron Fist", "Crane Hill",
                  "Thunder Valley", "Silver Lotus", "Bamboo Grove"][:clubs]
    schedule = [
        {"type": "pattern", "name": "Junior Patterns", "mat": "Mat A",
         "max_rank": "Green", "max_age": 17, "difficulty": 1.0},
        {"type": "sparring", "name": "Senior Sparring", "mat": "Mat B",
         "min_rank": "Blue", "min_age": 18, "difficulty": 1.05},
        {"type": "team_pattern", "name": "Club Team Patterns", "mat": "Mat A",
         "team_size": 3, "difficulty": 1.1},
        {"type": "breaking", "name": "Power Breaking", "mat": "Mat B",
         "min_rank": "Blue", "max_boards": 6, "difficulty": 1.15},
    ][:event_count]
    return {
        "name": "Py Kwon Do Open",
        "seed": seed,
        "steps": steps,
        "max_parallel": 2,
        "clubs": club_names,
        "competitors": {"count": competitors, "age_range": [10, 52]},
        "events": schedule,
    }


def validate_config(config):
    """checks a scenario dictionary and explains what is wrong

    Raises
    ------
    ValueError
        with a message naming the key at fault
    """
    if not isinstance(config, dict):
        raise ValueError("a scenario must be a JSON object")
    missing = [key for key in REQUIRED_KEYS if key not in config]
    if missing:
        raise ValueError(f"scenario is missing {missing}")
    if not isinstance(config["clubs"], list) or len(config["clubs"]) < 1:
        raise ValueError("'clubs' must be a list with at least one club")
    if not isinstance(config["events"], list) or len(config["events"]) < 2:
        raise ValueError("'events' must be a list of at least two events "
                         "(the specification asks for two types minimum)")
    ranks = pk.RankSystem(config.get("ranks"))
    for number, event in enumerate(config["events"], start=1):
        if not isinstance(event, dict):
            raise ValueError(f"event {number} must be a JSON object")
        if event.get("type") not in ev.EVENT_TYPES:
            raise ValueError(f"event {number} ({event.get('name', '?')}) has "
                             f"unknown type {event.get('type')!r}, "
                             f"expected one "
                             f"of {sorted(ev.EVENT_TYPES)}")
        for key in ("min_rank", "max_rank"):
            if event.get(key) and event[key] not in ranks.names():
                raise ValueError(f"event {event.get('name', number)}: {key} "
                                 f"{event[key]!r} is not a rank in "
                                 f"{ranks.names()}")
    people = config.get("competitors", {})
    if not isinstance(people, dict):
        raise ValueError("'competitors' must be an object with "
                         "'count' or 'file'")
    if "file" not in people and int(people.get("count", 0)) < 2:
        raise ValueError("'competitors.count' must be at least 2")
    return True


class Scenario:
    """
    One set of simulation parameters, and the factory that turns it
    into a Competition.

    Attributes
    ----------
    config : dict
        the validated scenario dictionary
    source : str
        where it came from, for the report header
    """

    def __init__(self, config, source="built-in"):
        """stores and validates a scenario dictionary"""
        validate_config(config)
        self.config = config
        self.source = source

    def __str__(self):
        """returns the scenario name and where it came from"""
        return f"{self.config['name']} (from {self.source})"

    @classmethod
    def load(cls, path):
        """reads a scenario from a JSON file"""
        if not os.path.exists(path):
            raise ValueError(f"scenario file not found: {path}")
        with open(path, encoding="utf-8") as handle:
            config = json.load(handle)
        return cls(config, source=path)

    @classmethod
    def from_prompt(cls, reader=input, writer=print):
        """builds a scenario by asking the user, with validation"""
        writer("No scenario file given - let's set one up.")
        clubs = ask_int("How many clubs", 2, 6, reader, writer)
        competitors = ask_int("How many competitors", 6, 60, reader, writer)
        event_count = ask_int("How many events", 2, 4, reader, writer)
        steps = ask_int("How many timesteps at most", 20, 500, reader, writer)
        config = default_config(competitors=competitors, clubs=clubs,
                                event_count=event_count, steps=steps)
        return cls(config, source="prompted input")

    # --- accessors used by the driver ---------------------------------
    def name(self):
        """returns the scenario's name"""
        return self.config["name"]

    def steps(self, override=None):
        """returns the timestep budget, CLI override winning"""
        return int(override if override else self.config.get("steps", 300))

    def seed(self, override=None):
        """returns the random seed, CLI override winning"""
        chosen = override if override is not None else self.config.get("seed")
        return None if chosen is None else int(chosen)

    def mat_names(self):
        """returns the mats the schedule needs, in order of first use"""
        mats = list(self.config.get("mats", []))
        for event in self.config["events"]:
            if event["mat"] not in mats:
                mats.append(event["mat"])
        return mats

    def build(self, seed=None, steps=None):
        """creates the Competition described by this scenario

        Parameters
        ----------
        seed : int, optional
            overrides the scenario's own seed
        steps : int, optional
            overrides the scenario's own timestep budget

        Returns
        -------
        competition : Competition
        budget : int
            the timestep budget to run it for
        """
        from competition import Competition   # imported here to avoid a cycle

        config = self.config
        chosen_seed = self.seed(seed)
        rng = random.Random(chosen_seed)
        ranks = pk.RankSystem(config.get("ranks"))
        club_names = list(config["clubs"])
        size = config.get("venue", {})
        venue = pk.Venue.build_default(club_names, self.mat_names(),
                                       width=size.get("width"),
                                       height=size.get("height"))
        clubs = {name: pk.Club(name) for name in club_names}
        people = config.get("competitors", {})
        if "file" in people:
            roster_path = people["file"]
            if not os.path.isabs(roster_path) and self.source != "built-in":
                here = os.path.dirname(os.path.abspath(self.source))
                candidate = os.path.join(here, roster_path)
                if os.path.exists(candidate):
                    roster_path = candidate
            roster = load_roster(roster_path)
            for entry in roster:
                if entry["club"] not in clubs:
                    clubs[entry["club"]] = pk.Club(entry["club"])
        else:
            roster = build_generated_roster(people, club_names, ranks, rng)
        competitors = build_competitors(roster, venue, clubs, ranks)
        schedule = [ev.make_event(event) for event in config["events"]]
        competition = Competition(config["name"], venue, ranks, clubs,
                                  competitors, schedule, rng=rng,
                                  max_parallel=int(
                                      config.get("max_parallel", 2)))
        return competition, self.steps(steps)
