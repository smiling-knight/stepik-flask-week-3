import random
from uuid import uuid4

from flask import Flask, render_template, abort
from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, RadioField
from wtforms.validators import InputRequired


from utils import JsonHandler, get_working_days

from dataset.data import days
from defaults import TEACHERS_COUNT_ON_MAIN

app = Flask(__name__)
# app.secret_key = uuid4().bytes
app.config['WTF_CSRF_ENABLED'] = False


class BookingForm(FlaskForm):
    clientWeekday = HiddenField()
    clientTime = HiddenField()
    clientTeacher = HiddenField()
    clientName = StringField(validators=[InputRequired(), ])
    clientPhone = StringField(validators=[InputRequired(), ])


class RequestForm(FlaskForm):
    goal = RadioField()
    time = RadioField()
    clientName = StringField(validators=[InputRequired(), ])
    clientPhone = StringField(validators=[InputRequired(), ])


@app.route("/")
def main():
    db = JsonHandler.read_db()
    goals = db["goals"]
    ts = db["teachers"]
    rand_ts = []
    for _ in range(TEACHERS_COUNT_ON_MAIN):
        id_ = random.randint(0, len(ts) - 1)
        rand_ts.append(ts[id_])
    return render_template("index.html", teachers=rand_ts, goals=goals)


@app.route("/goals/<goal_id>/")
def goals(goal_id):
    db = JsonHandler.read_db()
    if goal_id not in db["goals"]:
        abort(404)
    filtered_t = [t for t in db["teachers"] if goal_id in t["goals"]]
    filtered_t.sort(key=lambda x: x["rating"], reverse=True)
    return render_template(
        "goal.html", teachers=filtered_t, goal=db["goals"][goal_id]
    )


@app.route("/profiles/<profile_id>/")
def profile(profile_id):
    db = JsonHandler.read_db()
    teachers = db["teachers"]
    profile_id = int(profile_id)
    if profile_id not in [t["id"] for t in teachers]:
        abort(404)
    goals = db["goals"]
    t = teachers[profile_id]
    return render_template(
        "profile.html",
        teacher=t,
        goals=goals,
        schedule=get_working_days(t["free"]),
        days=days,
    )

@app.route("/request/")
def request():
    return render_template("request.html")


@app.route("/request_done/", methods=["POST"])
def request_done():
    request_form = RequestForm()
    JsonHandler.write_request(
            {
                "goal": request_form.goal.data,
                "time": request_form.time.data,
                "clientName": request_form.clientName.data,
                "clientPhone": request_form.clientPhone.data,
            }
        )
    return render_template("request_done.html", request_form=request_form)


@app.route("/booking/<profile_id>/<day>/<time>/")
def booking(profile_id, day, time):
    profile_id = int(profile_id)
    db = JsonHandler.read_db()
    teacher = db["teachers"][profile_id]
    rus_weekday = days[day]
    return render_template(
        "booking.html",
        teacher=teacher,
        weekday=str(day),
        time=str(time),
        rus_weekday=rus_weekday,
    )


@app.route("/booking_done/", methods=["POST"])
def booking_done():
    booking_form = BookingForm()
    if booking_form.validate_on_submit():
        db = JsonHandler.read_db()

        profile_id = int(booking_form.clientTeacher.data)
        teacher = db["teachers"][profile_id]
        teacher["free"][booking_form.clientWeekday.data][
            booking_form.clientTime.data
        ] = False

        JsonHandler.write_db(db)
        return render_template(
            "booking_done.html",
            rus_weekday=days[booking_form.clientWeekday.data],
            booking_form=booking_form,
        )
    else:
        return "Try one more time, please"


if __name__ == "__main__":
    app.run()
