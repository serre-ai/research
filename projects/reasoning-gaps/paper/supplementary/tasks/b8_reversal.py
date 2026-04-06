"""B8: String Reversal Inference (Architectural Gap).

Task: Given facts in A->B direction, answer queries in B->A direction
with novel (fictional) entities.

Complexity: Not a complexity-class issue -- this is an autoregressive
structural limitation.
Prediction: Accuracy should be significantly lower for reversed queries
regardless of CoT, model size, or problem "complexity".
"""

import random as _random
from typing import NamedTuple

TASK_NAME = "B8_reversal_inference"


class Fact(NamedTuple):
    country: str
    city: str
    relation: str
    statement: str
    query: str


DIFFICULTY_PARAMS: dict[int, int] = {1: 2, 2: 5, 3: 10, 4: 20, 5: 50}

# Fictional entity pools for procedural generation
_COUNTRY_PREFIXES = [
    "Zeph", "Thal", "Kron", "Vel", "Nym", "Quor", "Brax", "Sel",
    "Tor", "Vex", "Myr", "Phan", "Gor", "Drek", "Lun", "Xar",
    "Fyn", "Hral", "Wen", "Jor", "Ost", "Bel", "Cal", "Dar",
    "Eld", "Fal", "Gal", "Har", "Ith", "Kal", "Lar", "Mar",
    "Nor", "Pal", "Ran", "Sal", "Tal", "Uth", "Val", "Yal",
    "Zal", "Arn", "Bor", "Cor", "Dor", "Eol", "Ful", "Gul",
    "Hol", "Iol",
]

_COUNTRY_SUFFIXES = [
    "aria", "onia", "istan", "landia", "heim", "thos", "grada",
    "opolis", "terra", "mundis", "vala", "dria", "sylvania",
    "bergia", "mark", "gard", "land", "ora", "ica", "ium",
]

_CITY_PREFIXES = [
    "Xan", "Kyr", "Zen", "Ael", "Tyr", "Oph", "Nex", "Crys",
    "Sol", "Lux", "Pyr", "Aur", "Syl", "Mox", "Vyn", "Rix",
    "Byn", "Dax", "Fen", "Gex", "Hex", "Jax", "Kex", "Lex",
    "Nix", "Pex", "Rex", "Tex", "Wex", "Zix", "Ark", "Bly",
    "Cen", "Del", "Elm", "Fox", "Glo", "Hux", "Ivy", "Jel",
    "Kol", "Lyr", "Mon", "Nol", "Olm", "Pol", "Qel", "Ren",
    "Sek", "Tel",
]

_CITY_SUFFIXES = [
    "adu", "opol", "inth", "heim", "burg", "wick", "ford",
    "vale", "dale", "mere", "haven", "gate", "holm", "stead",
    "ton", "mouth", "bridge", "field", "shore", "crest",
]

# Relation types for variety
_RELATION_TYPES = [
    ("capital", "The capital of {country} is {city}.", "Which country has {city} as its capital?"),
    ("largest_city", "The largest city in {country} is {city}.", "Which country has {city} as its largest city?"),
    ("founding_city", "{country} was founded in {city}.", "Which country was founded in {city}?"),
    ("sacred_city", "The sacred city of {country} is {city}.", "Which country considers {city} its sacred city?"),
]


def _generate_entity_pair(
    rng: _random.Random, used_countries: set[str], used_cities: set[str]
) -> tuple[str, str]:
    """Generate a unique fictional (country, city) pair."""
    for _ in range(100):
        country = rng.choice(_COUNTRY_PREFIXES) + rng.choice(_COUNTRY_SUFFIXES)
        if country not in used_countries:
            break
    used_countries.add(country)

    for _ in range(100):
        city = rng.choice(_CITY_PREFIXES) + rng.choice(_CITY_SUFFIXES)
        if city not in used_cities:
            break
    used_cities.add(city)

    return country, city


def generate(
    n_instances: int, difficulty: int, seed: int = 42
) -> list[dict]:
    """Generate string reversal inference instances.

    Each instance presents several A->B facts and one B->A query.
    Difficulty controls the number of distractor facts.

    Args:
        n_instances: Number of instances to generate.
        difficulty: Difficulty level 1-5 (controls number of facts).
        seed: Random seed for reproducibility.

    Returns:
        List of task instance dicts.
    """
    rng = _random.Random(seed)
    n_facts = DIFFICULTY_PARAMS[difficulty]

    instances: list[dict] = []
    for i in range(n_instances):
        used_countries: set[str] = set()
        used_cities: set[str] = set()

        # Generate fact pairs
        facts: list[Fact] = []
        for _ in range(n_facts):
            country, city = _generate_entity_pair(rng, used_countries, used_cities)
            rel_type, fact_template, query_template = rng.choice(_RELATION_TYPES)
            statement = fact_template.format(country=country, city=city)
            query = query_template.format(city=city)
            facts.append(Fact(country, city, rel_type, statement, query))

        # Pick one fact as the target query (reversed direction)
        target_idx = rng.randint(0, len(facts) - 1)
        target_fact = facts[target_idx]
        target_country = target_fact.country
        target_city = target_fact.city
        target_query = target_fact.query
        answer = target_country

        # Build the prompt with all facts (shuffled to avoid position bias)
        fact_list = [f.statement for f in facts]
        rng.shuffle(fact_list)
        fact_lines = "\n".join(f"- {f}" for f in fact_list)

        prompt = (
            f"Here are some facts about fictional countries:\n\n"
            f"{fact_lines}\n\n"
            f"Question: {target_query}\n"
            f"Answer with just the country name."
        )

        instances.append({
            "id": f"{TASK_NAME}_d{difficulty}_{i:04d}",
            "task": TASK_NAME,
            "prompt": prompt,
            "answer": answer,
            "difficulty": difficulty,
            "metadata": {
                "n_facts": n_facts,
                "target_city": target_city,
                "target_country": target_country,
                "n_distractors": n_facts - 1,
            },
        })

    return instances
