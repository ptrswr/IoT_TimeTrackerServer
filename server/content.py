from datetime import datetime, timedelta
from tinydb import where
from server.server_config import db, storage_file_location


def add_terminal(terminal_id):
    terminals = db.table('terminals')
    search = terminals.search(where('id') == terminal_id)
    if not search:
        terminals.insert({'id': terminal_id})
        print(f'Terminal {terminal_id} added successfully!')
    else:
        print(f'Terminal with given id {terminal_id} alredy exists!')


def delete_terminal(terminal_id):
    terminals = db.table('terminals')
    search = terminals.search(where('id') == terminal_id)
    if search:
        terminals.remove(where('id') == terminal_id)
        print(f'Terminal with given id {terminal_id} removed successfully!')
    else:
        print(f'There is no such terminal in database')


def add_new_user(user_id, _name, _surname):
    users = db.table('users')
    search = users.search(where('id') == user_id)
    if not search:
        users.insert(
            {'id': user_id, 'card_id': '', 'name': _name, 'surname': _surname, 'enter_time': 0, 'work_time': 0})
        print(f'User {_name} {_surname} added successfully!')
    else:
        print(f'User with given id {user_id} alredy exists!')


def delete_user(user_id):
    users = db.table('users')
    search = users.search(where('id') == user_id)
    if search:
        users.remove(where('id') == user_id)
        print(f'User with given id {user_id} removed successfully!')
    else:
        print(f'There is no such user in database')


def assign_card(user_id, card_id):
    users = db.table('users')
    search = users.search(where('id') == user_id)
    if search:
        card_search = db.table('cards').search(where('id') == card_id)
        if card_search:
            if check_if_user_has_card(user_id):
                if check_if_card_not_used(card_id):
                    users.update({'card_id': card_id}, where('id') == user_id)
                    print(f'User with given id {user_id} assigned {card_id} successfully!')
                else:
                    print(f'Card {card_id} is already assigned to someone else!')


            else:
                print(f'User {user_id} has  already assigned card!')

        else:
            print(f'No such card {card_id} exists!')

    else:
        print(f'There is no such user in database')


def delete_assigned_card(user_id):
    users = db.table('users')
    search = users.search(where('id') == user_id)
    if search:
        if not check_if_user_has_card(user_id):
            users.update({'card_id': ''}, where('id') == user_id)
            print(f'User with given id {user_id} removed assignment successfully!')

        else:
            print(f'This user has no assigned cards!')

    else:
        print(f'There is no such user in database')

# double check and repair
def check_if_user_has_card(user_id):
    card_id = db.table('users').search(where('id') == user_id)
    return card_id[0]['card_id'] == ''


def check_if_card_not_used(card_id):
    card_id = db.table('users').search(where('id') == card_id)
    return card_id


# unfinished
def generate_raport(user_id):
    location = storage_file_location("_".join(("logins", user_id)) + '.csv')
    f = open(location, "w+")
    logs = show_logs_and_time(user_id)
    f.write(logs)
    f.close()
    print(f'Filed saved to {location}')


def show_logs_and_time(user_id):
    time_logs = db.table('time_logs')
    users = db.table('users')
    string = ""

    search = users.search(where('id') == user_id)
    if search:
        if check_if_user_has_card(user_id):
            logs = time_logs.search(where('card_id') == search[0]["card_id"])
            for l in logs:
                string += l["card_id"] + "\t" + l["terminal_id"] + "\t" + l["time"] + "\n"
            string += "Total work time: " + search["work_time"]

    return string


def log_card(card_id, terminal):
    terminals = db.table('terminals')
    search = terminals.search(where('id') == terminal)
    if not search:
        print(f'Unpermitted connection from {terminal} terminal.')
        return

    time_logs = db.table('time_logs')
    cards = db.table('cards')
    curr_time = datetime.now
    if not db.table('cards').search(where('id') == card_id):
        print(f'Unregistered card {card_id} entry')
        cards.insert({'id': card_id})
        time_logs.insert({'card_id': card_id, 'terminal': terminal, 'date': curr_time})

    time_logs.insert({'card_id': card_id, 'terminal': terminal, 'date': curr_time})
    update_work_time(card_id, terminal)


def update_work_time(card_id, time_now):
    users = db.table('users')
    search_user = users.search(where('card_id') == card_id)
    if search_user:
        current_user = search_user[0]
        if current_user["enter_time"] == 0:
            current_user["enter_time"] = time_now
        else:
            work_time = timedelta(time_now - current_user["enter_time"])
            current_user["work_time"] += work_time
            current_user["enter_time"] = 0  # zerowanie czasu wejscia
    else:
        print(f'There card is not registered to any user')

# unfinished
def display_menu():
    print('Possible actions. Press'
          '\n1 to add new user '
          '\n2 to assign card to the user'
          '\n3 to remove card from the user'
          '\n4 to generate time report for specified user'
          '\n9 to end the program')
