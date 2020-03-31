from datetime import datetime, timedelta
from tinydb import where
from server.server_config import db, storage_file_location
import time


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


def add_new_user(user_id, _name, ):
    users = db.table('users')
    search = users.search(where('id') == user_id)
    if not search:
        users.insert(
            {'id': user_id, 'card_id': '', 'name': _name, 'enter_time': 0, 'work_time': 0})
        print(f'User {_name}  added successfully!')
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
            if not check_if_user_has_card(user_id):
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
        if check_if_user_has_card(user_id):
            users.update({'card_id': ''}, where('id') == user_id)
            print(f'User with given id {user_id} removed assignment successfully!')

        else:
            print(f'This user has no assigned cards!')

    else:
        print(f'There is no such user in database')


# double check and repair
def check_if_user_has_card(user_id):
    card_id = db.table('users').get(where('id') == user_id)
    return card_id["card_id"] != ''


def check_if_card_not_used(card_id):
    card_id = db.table('users').get(where('card_id') == card_id)
    return not card_id


# unfinished
def generate_report(user_id):
    location = storage_file_location("_".join(("logins", str(user_id))) + '.csv')
    f = open(location, "w+")
    logs = show_logs_and_time(user_id)
    print(logs)
    f.write(logs)
    f.close()
    print(f'\nFiled saved to {location}')


def show_logs_and_time(user_id):
    time_logs = db.table('time_logs')
    users = db.table('users')
    string = ""

    search = users.get(where('id') == user_id)
    if search:
        if check_if_user_has_card(user_id):
            logs = time_logs.search(where('card_id') == search["card_id"])
            print(search["work_time"], "\n")
            temp = str(timedelta(seconds=search["work_time"]))
            string += "Time statistics for user" + user_id
            for l in logs:
                string += l["card_id"] + "\t" + l["terminal"] + "\t" + l["date"] + "\n"
            string += "Total work time since last reset: " + temp

    return string


def log_card(card_id, terminal):
    terminals = db.table('terminals')
    search = terminals.search(where('id') == terminal)
    if not search:
        print(f'Unpermitted connection from {terminal} terminal.')
        return

    time_logs = db.table('time_logs')
    cards = db.table('cards')
    c_time = datetime.now()
    curr_time = c_time.__str__()
    if not db.table('cards').search(where('id') == card_id):
        print(f'Unregistered card {card_id} entry')
        cards.insert({'id': card_id})
        time_logs.insert({'card_id': card_id, 'terminal': terminal, 'date': curr_time})

    time_logs.insert({'card_id': card_id, 'terminal': terminal, 'date': curr_time})
    update_work_time(card_id, c_time)


def update_work_time(card_id, time_):
    users = db.table('users')
    search_user = users.search(where('card_id') == card_id)
    time_now = time_to_seconds(time_)
    print(time_now, "\n")
    if search_user:
        current_user = search_user[0]
        if current_user["enter_time"] == 0:
            users.update({'enter_time': time_now}, where('card_id') == card_id)
        else:
            work_time = time_now - current_user["enter_time"]
            all_time = current_user["work_time"] + work_time
            users.update({'work_time': all_time}, where('card_id') == card_id)
            print(current_user["work_time"], "\n")
            users.update({'enter_time': 0}, where('card_id') == card_id)
    else:
        print(f'There card is not registered to any user')


def reset_users_timesheet():
    print("Logs deleted and users work time has been reset")
    users = db.table('users')
    db.purge_table('time_logs')
    for u in users:
        u["enter_time"] = 0
        u["work_time"] = 0


def time_to_seconds(time_):
    return int(time_.hour) * 3600 + int(time_.minute) * 60 + int(time_.second)


def main():
    reset_users_timesheet()
    add_terminal("pool")
    log_card('13dfr', "pool")
    time.sleep(10)
    log_card('13dfr', "pool")
    # log_card('14asd', "pool")
    print(show_logs_and_time(123))


if __name__ == '__main__':
    main()


# unfinished

def display_menu():
    print('Possible actions. Press'
          '\n1 to add new terminal '
          '\n2 to delete terminal '
          '\n3 to add new user '
          '\n4 to delete  user '
          '\n5 to assign card to the user'
          '\n6 to remove card from the user'
          '\n7 to generate time report for specified user'
          '\n8 to clear logs database'
          '\n9 to end the program')
    while True:
        while True:
            try:
                user_choice = int(input('>'))
                break
            except ValueError:
                print('Enter right number ')

        if user_choice == 1:
            id_ = input('Enter id of terminal that you want to add: ')
            add_terminal(id_)
        elif user_choice == 2:
            id_ = input('Enter id of terminal that you want to delete: ')
            delete_terminal(id_)
        elif user_choice == 3:
            id_ = input('Enter id for new user: ')
            name = input('\nEnter name and surname for new user: ')
            add_new_user(id_, name)
        elif user_choice == 4:
            id_ = input('Enter id of user that you want to delete: ')
            delete_user(id_)
        elif user_choice == 5:
            id_ = input('Enter id of user that will receive card: ')
            card_id = input('\nEnter id of card that will be assigned: ')
            assign_card(id_, card_id)
        elif user_choice == 6:
            id_ = input('Enter id of user whose card you want to remove: ')
            delete_assigned_card(id_)
        elif user_choice == 7:
            id_ = input('Enter id of user whose report you want to see: ')
            delete_assigned_card(id_)
        elif user_choice == 9:
            print("Exiting the server")
            break
        else:
            print("There is no such command")
