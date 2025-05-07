from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mindfuel.db"
db = SQLAlchemy(app)
CORS(app)


# Models
class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    tag = db.Column(db.String(80), nullable=True)


class Mood(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=False)
    energy = db.Column(db.Integer, nullable=True)
    note = db.Column(db.String(200), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# Routes
@app.route("/", methods=["GET"])
def index():
    return jsonify({"message": "Welcome to the MindFuel API!"}), 200


@app.route("/habit", methods=["POST"])
def log_habit():
    data = request.json
    habit = Habit(name=data["name"], tag=data.get("tag"))
    db.session.add(habit)
    db.session.commit()
    return jsonify({"message": "Habit logged."}), 201


@app.route("/mood", methods=["POST"])
def log_mood():
    data = request.json
    mood = Mood(score=data["score"], energy=data.get("energy"), note=data.get("note"))
    db.session.add(mood)
    db.session.commit()
    return jsonify({"message": "Mood logged."}), 201


@app.route("/stats", methods=["GET"])
def get_stats():
    habits = Habit.query.all()
    moods = Mood.query.all()

    habit_freq = defaultdict(int)
    for h in habits:
        habit_freq[h.name] += 1

    avg_mood = sum(m.score for m in moods) / len(moods) if moods else 0

    return jsonify(
        {"habit_frequencies": dict(habit_freq), "average_mood": round(avg_mood, 2)}
    )


@app.route("/timeline", methods=["GET"])
def get_timeline():
    habits = Habit.query.order_by(Habit.timestamp.desc()).limit(30).all()
    moods = Mood.query.order_by(Mood.timestamp.desc()).limit(30).all()

    return jsonify(
        {
            "habits": [
                {"name": h.name, "timestamp": h.timestamp.isoformat()} for h in habits
            ],
            "moods": [
                {
                    "score": m.score,
                    "energy": m.energy,
                    "timestamp": m.timestamp.isoformat(),
                }
                for m in moods
            ],
        }
    )


@app.route("/insights", methods=["GET"])
def get_insights():
    # Placeholder for advanced correlation logic
    return jsonify({"insights": "Feature coming soon. Track more data to unlock this."})


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
