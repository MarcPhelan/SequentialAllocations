import csv

STARTING_WEALTH = 200
#UPPER_WEALTH_BOUND = 2500
UPPER_WEALTH_BOUND = 400
MULTIPLIER = 2

STOCK_CHANGES = [
    [2, 1, 1, 2,  1, 2],
    [1, 2, 1],
    [2, 1, 1, 1, 2]
]

STOCK_NAMES = ["ABC", "XYZ"]

GAME_DATA_URL = 'static/data/GameData.csv'
BANKRUPT_DATA_URL = 'static/data/BankruptData.csv'
USER_DATA_URL = 'static/data/UserData.csv'

GAME_FILED_NAMES = ['GameID', 'Game', 'Block', 'Round', 'Wealth',
                    'AmountBet', 'FractionBet', 'SideBet', 'Outcome', 'Result']
BANKRUPT_FIELD_NAMES = ['GameID', 'Game', 'Block', 'Round',
                        'Wealth', 'AmountBet', 'FractionBet', 'SideBet', 'Outcome', 'Result']
USER_FIELD_NAMES = ['ParticipantID', 'GameID', 'Game', 'Payout Game',
                    'AttentionCheck', 'ProbEstimate', 'Strategy', 'DescribeStrategy']


def saveUserData(session):

    with open(USER_DATA_URL, 'a', newline='') as userfile:
        writer = csv.DictWriter(userfile, fieldnames=USER_FIELD_NAMES)
        writer.writerow({
            'ParticipantID': session['participant_id'],
            'GameID': session['game_id'],
            'Game': session['game'],
            'Payout Game': session['payout'],
            'AttentionCheck': session['attention_check'],
            'ProbEstimate': session['prob_estimate'],
            'Strategy': session['strategy'],
            'DescribeStrategy': session['describe_strategy']
        })


def handle_game(session, request):

    if session['game'] == 1:
        handle_game_1(session, request)
    else:
        handle_game_2(session, request)

    session['trial'] += 1


def handle_game_1(session, request):

    both_stock_invested = [
        None,  # empty to create space
        0,     # invested in ABC
        0      # invested in XYZ
    ]
    current_wealth = session['current_wealth']
    task_counter = session['task_counter']
    current_stock = session['stock_changes'][task_counter]
    outcome = (current_stock[session['trial']])

    amount_invested = int(request.form['amount_invested'])
    stock_invested = int(request.form.get('stock_invested'))
    both_stock_invested[stock_invested] = amount_invested
    print(f"both stock invest is : {both_stock_invested}")

    session['message'] = f"{STOCK_NAMES[outcome-1]} increased in value. "

    if stock_invested == 1:
        fraction_invested = round(
            amount_invested / session['current_wealth'], 3)
    else:
        fraction_invested = 0 - \
            round(amount_invested / session['current_wealth'], 3)

    if amount_invested == 0:         # invested nothing
        result = current_wealth
        net_result = amount_invested
        current_wealth = current_wealth
        session['message'] += "You invested Nothing."
    elif stock_invested == outcome:  # invested on up going stock
        result = (MULTIPLIER * amount_invested)
        net_result = round(result - amount_invested)
        current_wealth = current_wealth + net_result
        session['message'] += "You gained ζ" + str(net_result) + "."
    else:                            # invested on down going stock
        result = amount_invested
        net_result = 0 - result
        current_wealth = round(current_wealth - result)
        session['message'] += "You lost ζ" + str(result) + "."

    session['current_wealth'] = current_wealth

    if current_wealth <= 1:
        # WRITE TO BANKRUPT CSV
        with open(BANKRUPT_DATA_URL, 'a', newline='') as bankrupt_file:
            writer = csv.DictWriter(
                bankrupt_file, fieldnames=BANKRUPT_FIELD_NAMES)
            writer.writerow({
                'GameID': session['game_id'],
                'Game': session['game'],
                'Block': (session['task_counter'] + 1),
                'Round': (session['trial'] + 1),
                'Wealth': session['current_wealth'],
                'AmountBet': amount_invested,
                'FractionBet': fraction_invested,
                'SideBet': stock_invested,
                'Outcome': outcome,
                'Result': net_result
            })

    # WRITING TO GAME DATA
    with open(GAME_DATA_URL, 'a', newline='') as game_file:
        writer = csv.DictWriter(game_file, fieldnames=GAME_FILED_NAMES)
        writer.writerow({
            'GameID': session['game_id'],
            'Game': session['game'],
            'Block': (session['task_counter'] + 1),
            'Round': (session['trial'] + 1),
            'Wealth': session['current_wealth'],
            'AmountBet': amount_invested,
            'FractionBet': fraction_invested,
            'SideBet': stock_invested,
            'Outcome': outcome,
            'Result': net_result
        })


def handle_game_2(session, request):
    both_stock_invested = [
        None,  # empty to create space
        0,     # invested in ABC
        0      # invested in XYZ
    ]
    current_wealth = session['current_wealth']
    current_stock = session['stock_changes'][session['task_counter']]
    outcome = (current_stock[session['trial']])
    fraction_invested = 0

    ABC_invested = int(request.form.get('ABC_invested'))
    XYZ_invested = int(request.form.get('XYZ_invested'))
    net_investment = ABC_invested - XYZ_invested

    both_stock_invested[1] = ABC_invested
    both_stock_invested[2] = XYZ_invested

    session['message'] = f"{STOCK_NAMES[outcome-1]} increased in value. "

    if net_investment > 0:  # net investment on ABC
        stock_invested = 1
        amount_invested = net_investment
        fraction_invested = round(amount_invested / current_wealth, 3)
    elif net_investment == 0:
        amount_invested = net_investment
        stock_invested = 3
    else:
        stock_invested = 2
        amount_invested = abs(net_investment)
        fraction_invested = 0 - round(amount_invested / current_wealth, 3)

    if amount_invested == 0:  # no investment
        result = current_wealth
        net_result = amount_invested
        current_wealth = current_wealth
        session['message'] += "You invested Nothing."
    elif outcome == stock_invested:  # invested on stock that went up
        result = (MULTIPLIER * amount_invested)
        net_result = round(result - amount_invested)
        current_wealth = current_wealth + net_result
        session['message'] += "You gained ζ" + str(net_result) + "."
    else:  # invested on stock that went down
        result = amount_invested
        net_result = 0 - result
        current_wealth = round(current_wealth - result)
        session['message'] += "You lost ζ" + str(result) + "."

    session['current_wealth'] = current_wealth

    if current_wealth <= 1:
        # WRITE TO BANKRUPT CSV
        with open(BANKRUPT_DATA_URL, 'a', newline='') as bankrupt_file:
            writer = csv.DictWriter(
                bankrupt_file, fieldnames=BANKRUPT_FIELD_NAMES)
            writer.writerow({
                'GameID': session['game_id'],
                'Game': session['game'],
                'Block': (session['task_counter'] + 1),
                'Round': (session['trial'] + 1),
                'Wealth': session['current_wealth'],
                'AmountBet': amount_invested,
                'FractionBet': fraction_invested,
                'SideBet': stock_invested,
                'Outcome': outcome,
                'Result': net_result
            })

    # WRITING TO GAME DATA
    with open(GAME_DATA_URL, 'a', newline='') as game_file:
        writer = csv.DictWriter(game_file, fieldnames=GAME_FILED_NAMES)
        writer.writerow({
            'GameID': session['game_id'],
            'Game': session['game'],
            'Block': (session['task_counter'] + 1),
            'Round': (session['trial'] + 1),
            'Wealth': session['current_wealth'],
            'AmountBet': amount_invested,
            'FractionBet': fraction_invested,
            'SideBet': stock_invested,
            'Outcome': outcome,
            'Result': net_result
        })
