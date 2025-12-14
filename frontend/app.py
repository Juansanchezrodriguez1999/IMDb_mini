from flask import Flask, render_template, request, redirect
import requests
from dotenv import load_dotenv
import os
load_dotenv()

API_URL = os.getenv("API_URL")

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search")
def search():
    query = request.args.get("q")
    mode = request.args.get("mode")  

    if mode == "person":
        r = requests.get(f"{API_URL}/people/search", params={"name": query})
        results = r.json()
        return render_template("results_people.html", results=results, query=query)

    else:
        r = requests.get(f"{API_URL}/titles/search", params={"title": query})
        results = r.json()
        return render_template("results_titles.html", results=results, query=query)


@app.route("/person/<nconst>")
def person_detail(nconst):
    r = requests.get(f"{API_URL}/people/{nconst}")
    data = r.json()
    return render_template("person_detail.html", person=data)

@app.route("/resolve-person/<name>/<tconst>")
def resolve_person(name, tconst):
    r = requests.get(f"{API_URL}/people/search", params={"name": name})
    people = r.json()

    if not people:
        return "Actor no encontrado", 404

    for p in people:
        if "known_for_titles" in p and p["known_for_titles"]:
            if tconst in p["known_for_titles"]:
                return redirect(f"/person/{p['nconst']}")

    return redirect(f"/person/{people[0]['nconst']}")


@app.route("/title/<tconst>")
def title_detail(tconst):
    r = requests.get(f"{API_URL}/titles/{tconst}")
    data = r.json()
    return render_template("title_detail.html", title=data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

