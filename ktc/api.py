import sqlite3
import contextlib
from typing import Dict, List
from fractions import Fraction

import os


path_to_database = os.path.join(os.path.dirname("../data"), "monsters.db")
db_location = path_to_database


def sort_sizes(size_list: List[str]) -> List[str]:
    to_return = []

    size_list = [size.lower() for size in size_list]

    if "tiny" in size_list:
        to_return.append("tiny")
    if "small" in size_list:
        to_return.append("small")
    if "medium" in size_list:
        to_return.append("medium")
    if "large" in size_list:
        to_return.append("large")
    if "huge" in size_list:
        to_return.append("huge")
    if "gargantuan" in size_list:
        to_return.append("gargantuan")

    to_return = [size.title() for size in to_return]
    return to_return


def get_list_of_environments() -> List[str]:
    with contextlib.closing(sqlite3.connect(db_location)) as conn:
        c = conn.cursor()

        c.execute('''SELECT DISTINCT environment FROM monsters''')
        unique_environments = [item[0] for item in c.fetchall()]

    set_of_environments = set()
    for environment in unique_environments:
        if not environment:
            continue
        for env in environment.split(','):
            set_of_environments.add(env.strip())

    environments = list(set_of_environments)
    environments.sort()
    return environments


def get_list_of_sizes() -> List[str]:
    with contextlib.closing(sqlite3.connect(db_location)) as conn:
        c = conn.cursor()

        c.execute('''SELECT DISTINCT size FROM monsters''')
        unique_types = [item[0] for item in c.fetchall()]

    size_list = sort_sizes(unique_types)
    return size_list


def get_list_of_monster_types() -> List[str]:
    with contextlib.closing(sqlite3.connect(db_location)) as conn:
        c = conn.cursor()

        c.execute('''SELECT DISTINCT type FROM monsters''')
        unique_types = [item[0] for item in c.fetchall()]

    unique_types.sort()
    return unique_types


def get_list_of_challenge_ratings() -> List[str]:
    with contextlib.closing(sqlite3.connect(db_location)) as conn:
        c = conn.cursor()

        c.execute('''SELECT DISTINCT cr FROM monsters''')
        unique_crs = [item[0] for item in c.fetchall()]

    unique_crs.sort(key=Fraction)
    return unique_crs


def get_list_of_alignments() -> List[str]:
    with contextlib.closing(sqlite3.connect(db_location)) as conn:
        c = conn.cursor()

        c.execute('''SELECT DISTINCT alignment FROM monsters''')
        unique_alignments = [item[0].lower()
                             for item in c.fetchall() if not " or " in item[0]]

    unique_alignments.sort()
    return unique_alignments


def get_list_of_sources() -> List[str]:
    with contextlib.closing(sqlite3.connect(db_location)) as conn:
        c = conn.cursor()

        c.execute('''SELECT DISTINCT source FROM monsters''')
        unique_sources = [item[0] for item in c.fetchall()]

    set_of_sources = set()
    for source_set in unique_sources:
        sources = source_set.split(',')
        for source in sources:
            set_of_sources.add(source.split(':')[0].strip())

    sources = list(set_of_sources)
    sources.sort()
    return sources


def get_list_of_monsters(parameters: Dict) -> List[Dict]:
    """Query the database for monsters matching the parameters passed and return a list

    Args:
        parameters (Dict): a dict of parameters, consisting of column names: [acceptable values]

    Returns:
        List[Tuple]: a list of dicts, each dict describing a single monster
    """

    if not parameters:
        parameters = {}

    try:
        environment_constraints = [param.split("_")[1] for param
                                   in parameters["environments"]]
    except KeyError:
        environment_constraints = []

    try:
        size_constraints = [param.split("_")[1] for param
                            in parameters["sizes"]]
    except KeyError:
        size_constraints = []

    try:
        source_constraints = [param.split("_")[1] for param
                              in parameters["sources"]]
    except KeyError:
        source_constraints = []

    try:
        type_constraints = [param.split("_")[1] for param
                            in parameters["types"]]
    except KeyError:
        type_constraints = []

    try:
        alignment_constraints = [param.split("_")[1] for param
                                 in parameters["alignments"]]
    except KeyError:
        alignment_constraints = []

    # Oh, this is clumsy, I hate this
    where_requirements = ""
    query_arguments = []
    query_from = "monsters"

    # SO
    # If we have size constraints, we construct a string of placeholders,
    # then put that into a IN subquery
    # and then append the constraints to the query_arguments list
    if environment_constraints != []:
        environment_query_placeholders = f"({', '.join(['?']*len(environment_constraints))})"
        where_requirements += f"environment IN {environment_query_placeholders} AND "
        query_arguments += environment_constraints

    if size_constraints != []:
        size_query_placeholders = f"({', '.join(['?']*len(size_constraints))})"
        where_requirements += f"size IN {size_query_placeholders} AND "
        query_arguments += size_constraints

    if source_constraints != []:
        query_from = "(SELECT * FROM monsters WHERE "
        for i in range(len(source_constraints)):
            query_from += "source LIKE ? OR "
            source_constraints[i] = f"%{source_constraints[i]}%"
        query_from = query_from[:-4]
        query_from += ")"
        query_arguments = source_constraints + query_arguments

    if type_constraints != []:
        type_query_placeholders = f"({', '.join(['?']*len(type_constraints))})"
        where_requirements += f"type IN {type_query_placeholders} AND "
        query_arguments += type_constraints

    if alignment_constraints != []:
        alignment_query_placeholders = f"({', '.join(['?']*len(alignment_constraints))})"
        where_requirements += f"alignment IN {alignment_query_placeholders} AND "
        query_arguments += alignment_constraints

    # If there are requirements, we add a WHERE to the start
    if where_requirements != "":
        where_requirements = ("WHERE ") + where_requirements
    # Take of the trailing " and "
    if where_requirements.endswith(" AND "):
        where_requirements = where_requirements[:-5]

    query_string = f'''SELECT name, cr, size, type, alignment, source FROM {query_from} {where_requirements} ORDER BY name asc LIMIT 20'''

    with contextlib.closing(sqlite3.connect(db_location)) as conn:
        c = conn.cursor()
        conn.set_trace_callback(print)

        if query_arguments:
            c.execute(query_string, (*query_arguments,))
        else:
            c.execute(query_string)
        monster_list = c.fetchall()

    monsters = []
    for monster in monster_list:
        monsters.append({"name": monster[0].strip(),
                         "cr": monster[1].strip(),
                         "size": monster[2].strip(),
                         "type": monster[3].strip(),
                         "alignment": monster[4].strip(),
                         "sources": monster[5].strip()
                         })

    return monsters
