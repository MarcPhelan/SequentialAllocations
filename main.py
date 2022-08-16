from flask import Flask, render_template, session, request, redirect, url_for
import random
from utils import *

app = Flask(__name__)
app.config["SECRET_KEY"] = "setkey2"


@app.route('/', methods=["GET"])
def welcome():
    return render_template("index.html")


@app.route('/consent', methods=['POST'])
def consent():
    participant_id = request.form['id']

    session['participant_id'] = participant_id
    session['game_id'] = random.randrange(1, 1000000)
    session['game'] = random.randint(1, 2)

    return render_template("consent.html")


@app.route('/background', methods=['POST'])
def background():
    consent = request.form['consent']
    if consent == "no":
        return render_template('no-consent.html')
    else:
        return render_template(
            'background.html',
            game_flask=session['game']
        )


@app.route('/incentive', methods=['POST'])
def incentive():
    return render_template("incentive.html")


@app.route('/begin', methods=['GET', 'POST'])
def begin():

    session['task_counter'] = 0
    session['stock_changes'] = STOCK_CHANGES
    random.shuffle(session['stock_changes'])
    session['message'] = ''
    session['over'] = False
    session['current_wealth'] = STARTING_WEALTH

    session['bankrupt_round'] = None
    session['best_round'] = None
    session['best_round_wealth'] = 0

    print(session['stock_changes'])

    return render_template("begin.html")


@app.route('/transition', methods=['GET', 'POST'])
def transition():

    session['task_counter'] += 1

    heading = "You Completed This Section"
    para = f"Your Final Wealth Was: ζ{session['current_wealth']}."
    next = "Next Section"
    redirect_to = "game"

    if session['current_wealth'] <= 1:
        heading = "Bankrupt"
        para = "Your lost all your money. Press Continue to Proceed to Next Section."
        next = "Continue"
        if session['task_counter'] >= len(session['stock_changes']):
            redirect_to = "over"

        session['message'] = ""
        session['current_wealth'] = STARTING_WEALTH
        session['bankrupt_round'] = session['task_counter']

    if session['current_wealth'] > UPPER_WEALTH_BOUND:
        heading = "You Completed This Section"
        para = "Press Next Section to Continue."
        next = "Next Section"
        if session['task_counter'] >= len(session['stock_changes']):
            redirect_to = "over"

        session['message'] = ""
        session['current_wealth'] = STARTING_WEALTH

    elif session['task_counter'] >= len(session['stock_changes']):
        heading = "Completed"
        para = "You Completed All the Rounds. Press Continue to Preceed to Next Sections."
        next = "Continue"
        redirect_to = "over"
        if session['current_wealth'] > session['best_round_wealth']:
            session['best_round_wealth'] = session['current_wealth']
            session['best_round'] = session['task_counter']

    else:
        # NEXT SECTIONS
        session['message'] = ""
        if session['current_wealth'] > session['best_round_wealth']:
            session['best_round_wealth'] = session['current_wealth']
            session['best_round'] = session['task_counter']
        session['current_wealth'] = STARTING_WEALTH

    return render_template(
        "transition.html",
        heading=heading,
        para=para,
        next=next,
        redirect_to=redirect_to,
    )


@app.route("/game", methods=['GET', 'POST'])
def game():
    if request.method == 'GET':
        session['trial'] = 0
        return render_template(
            "game.html",
            wealth=session['current_wealth'],
            message=session['message'],
            game_flask=session['game']
        )

    elif request.method == 'POST':

        handle_game(session, request)

        max_trials = len(session['stock_changes'][session['task_counter']])

        if session['current_wealth'] < 1:
            # BANKRUPT
            return redirect("/transition")

        if session['current_wealth'] > UPPER_WEALTH_BOUND:
            # UPPER_WEALTH_BOUND
            return redirect("/transition")

        elif session['trial'] < max_trials:
            # PROCEED TO NEXT ROUND
            return render_template(
                f"game.html",
                wealth=session['current_wealth'],
                message=session['message'],
                game_flask=session['game']
            )

        else:
            # OUT OF ROUNDS, PROCEED TO NEXT SECTION
            return redirect("/transition")


@app.route("/over", methods=["GET"])
def over():
    return redirect("/questionnaire1")


@app.route("/questionnaire1", methods=["GET", "POST"])
def questionnaire1():
    return render_template("questionnaire1.html")


@app.route("/questionnaire2", methods=["POST"])
def questionnaire2():
    session['attention_check'] = request.form['attention']
    session['prob_estimate'] = request.form['prob_estimate']
    print(session)
    return render_template("questionnaire2.html")


@app.route("/end", methods=["GET", "POST"])
def end():
    session['strategy'] = request.form['strategy']
    session['describe_strategy'] = request.form['describe_strategy']

    payout = random.choice([1, 2, 3])
    session['payout'] = payout
    print(f"The payout game is: Game {payout}")

    return render_template(
        "end.html",
        payout_flask=session['payout']
    )


@app.route("/saving", methods=["POST"])
def savings():
    saveUserData(session)
    return redirect("/")


if __name__ == '__main__':
    app.run(debug=True)
