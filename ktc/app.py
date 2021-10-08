# -*- coding: utf-8 -*-
"""
Contains the functions necessary for the Flask webapp.

Note that these almost all call functions in the api module; this is
a deliberate design decision to allow for the possibility of other
frontends in the future.
"""

import json
import os

from flask import Flask, jsonify, render_template, request

try:
    import api  # type: ignore
    import random_encounter_generator  # type: ignore
except ModuleNotFoundError:
    from ktc import api  # type: ignore
    from ktc import random_encounter_generator  # type: ignore

VERSION = "v0.4.1"

app = Flask(__name__)
path_to_database = os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.pardir, "data/monsters.db"))

db_location = path_to_database


@app.route("/", methods=["GET", "POST", "PUT"])
def home():
    """Renders the main encounter generator"""
    return render_template("index.html", version=VERSION)


@app.route("/index.html", methods=["GET", "POST", "PUT"])
def index():
    """Renders the main encounter generator"""
    return render_template("index.html", version=VERSION)


@app.route("/about.html", methods=["GET", "POST", "PUT"])
def about_page():
    """Renders the About page"""
    return render_template("about.html")


@app.route("/api/environments", methods=["GET"])
def get_environments():
    """Returns a list of all possible environments"""
    return jsonify(api.get_list_of_environments())


@app.route("/api/sizes", methods=["GET"])
def get_sizes():
    """Returns a list of all possible monster sizes"""
    return jsonify(api.get_list_of_sizes())


@app.route("/api/crs", methods=["GET"])
def get_crs():
    """Returns a list of all possible challenge ratings"""
    return jsonify(api.get_list_of_challenge_ratings())


@app.route("/api/sources", methods=["GET"])
def get_sources():
    """Returns a list of imported source titles"""
    return jsonify(api.get_list_of_sources())


@app.route("/api/types", methods=["GET"])
def get_types():
    """Returns a list of imported monster types"""
    return jsonify(api.get_list_of_monster_types())


@app.route("/api/alignments", methods=["GET"])
def get_alignments():
    """Returns a list of imported alignments"""
    return jsonify(api.get_list_of_alignments())


@app.route("/api/monsters", methods=["GET", "POST"])
def get_monsters():
    """Gets a list of monsters matching the passed parameters and returns them"""
    try:
        monster_parameters_string = request.values["params"]
        monster_parameters = json.loads(
            monster_parameters_string)
    except KeyError:
        monster_parameters = {}
    return jsonify(api.get_list_of_monsters(monster_parameters))


@app.route("/api/expthresholds", methods=["GET", "POST"])
def get_exp_thresholds():
    """Finds and returns the encounter difficulty thresholds for a party"""
    party = json.loads(request.values["party"])
    return jsonify(api.get_party_thresholds(party))


@app.route("/api/encounterxp", methods=["GET", "POST"])
def get_encounter_xp():
    """Calculate & return the XP generated by an encounter"""
    monsters = json.loads(request.values["monsters"])
    return jsonify(api.get_encounter_xp(monsters))


@app.route("/api/unofficialsources", methods=["GET"])
def get_unofficial_sources():
    """Get a list of unofficial sources"""
    return jsonify(api.get_unofficial_sources())


@app.route("/api/processCSV", methods=["GET", "POST"])
def process_csv():
    """Imports the CSV passed. Note that this should never occur"""
    csv_string = json.loads(request.values["csv"])
    key = json.loads(request.values["key"])
    source_name = api.ingest_custom_csv_string(csv_string, db_location, key)
    return jsonify({"name": source_name})


@app.route("/api/checksource", methods=["GET", "POST"])
def check_if_key_processed():
    """Checks if the existing key has been processed"""
    key = json.loads(request.values["key"])
    result = api.check_if_key_processed(key)
    return jsonify(result)


@app.route("/api/encountergenerator", methods=["GET", "POST"])
def generate_encounter():
    """Wrapper for the encounter generator function"""
    try:
        params = json.loads(request.values["params"])
    except:
        params = {"bing": "bong"}

    result = random_encounter_generator.generate(params)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
