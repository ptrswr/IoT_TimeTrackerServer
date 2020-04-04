from datetime import datetime, timedelta
from tinydb import where
import random
from server_config import db, storage_file_location


def add_terminal(terminal_id):
    terminals = db.table('terminals')
    search_term = terminals.get(where('id') == terminal_id)
    if not search_term:
        terminals.insert({'id': terminal_id})
        print(f'Terminal {terminal_id} added successfully!')
    else:
        print(f'Terminal with given id {terminal_id} alredy exists!')


def delete_terminal(terminal_id):
    terminals = db.table('terminals')
    search_term = terminals.search(where('id') == terminal_id)
    if search_term:
        terminals.remove(where('id') == terminal_id)
        print(f'Terminal with given id {terminal_id} removed successfully!')
    else:
        print(f'There is no such terminal with id {terminal_id} in database')


def add_new_user(user_id, _name, ):
    users = db.table('users')
    search_user = users.get(where('id') == user_id)
    if not search_user:
        users.insert(
            {'id': user_id, 'card_id': '', 'name': _name, 'enter_time': 0, 'work_time': 0})
        print(f'User {_name}  added successfully!')
    else:
        print(f'User with given id {user_id} alredy exists!')


def delete_user(user_id):
    users = db.table('users')
    search_user = users.get(where('id') == user_id)
    if search_user:
        users.remove(where('id') == user_id)
        print(f'User with given id {user_id} removed successfully!')
    else:
        print(f'There is no such user in database')


def assign_card(user_id, card_id):
    users = db.table('users')
    search_user = users.get(where('id') == user_id)
    if search_user:
        card_search = db.table('cards').get(where('id') == card_id)
        if card_search:
            if not check_if_user_has_card(user_id):
                if check_if_card_not_used(card_id):
                    users.update({'card_id': card_id}, where('id') == user_id)
                    print(f'User with given id {user_id} assigned {card_id} successfully!')
                else:
                    print(f'Card {card_id} is already assigned to someone else!')

            else:
                print(f'User {user_id} already has assigned card!')

        else:
            print(f'No such card {card_id} exists!')

    else:
        print(f'There is no such user in database')


def delete_assigned_card(user_id):
    print(user_id)
    users = db.table('users')
    search_user = users.get(where('id') == user_id)
    if search_user:
        if check_if_user_has_card(user_id):
            users.update({'card_id': ''}, where('id') == user_id)
            print(f'User with given id {user_id} removed assignment successfully!')

        else:
            print(f'This user has no assigned cards!')
    else:
        print(f'There is no such user in database')


def check_if_user_has_card(user_id):
    card_id = db.table('users').get(where('id') == user_id)
    return card_id["card_id"] != ''


def check_if_card_not_used(card_id):
    card_id = db.table('users').get(where('card_id') == card_id)
    return not card_id


def generate_report(user_id):
    time_logs = db.table('time_logs')
    location = storage_file_location("_".join(("logins", user_id)) + '.csv')
    users = db.table('users')
    report = ""

    search_user = users.get(where('id') == user_id)
    if search_user:
        if check_if_user_has_card(user_id):
            f = open(location, "w+")
            logs = time_logs.search(where('card_id') == search_user["card_id"])
            temp = str(timedelta(seconds=search_user["work_time"]))
            report += "Time statistics for user " + user_id + " | Total work time of user: " + temp + "\n"
            for l in logs:
                report += l["card_id"] + "," + l["terminal"] + "," + l["date"] + ",\n"
            f.write(report)
            f.close()
            print(f'\nFiled saved to {location}')


def show_logs_and_time(user_id):
    time_logs = db.table('time_logs')
    users = db.table('users')
    report = ""

    search_user = users.get(where('id') == user_id)
    if search_user:
        if check_if_user_has_card(user_id):
            logs = time_logs.search(where('card_id') == search_user["card_id"])
            temp = str(timedelta(seconds=search_user["work_time"]))
            report += "Time statistics for user " + str(user_id) + "\n"
            for l in logs:
                report += l["card_id"] + "\t" + l["terminal"] + "\t" + l["date"] + "\n"
            report += "Total work time since last reset: " + temp

    return report


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
    update_work_time(card_id, c_time)


def update_work_time(card_id, time_):
    users = db.table('users')
    search_user = users.search(where('card_id') == card_id)
    time_now = time_to_seconds(time_)
    if search_user:
        current_user = search_user[0]
        if current_user["enter_time"] == 0:
            users.update({'enter_time': time_now}, where('card_id') == card_id)
        else:
            work_time = time_now - current_user["enter_time"]
            all_time = current_user["work_time"] + work_time
            users.update({'work_time': all_time}, where('card_id') == card_id)
            users.update({'enter_time': 0}, where('card_id') == card_id)
    else:
        print(f'This card is not registered to any user')


def reset_users_timesheet():
    print("Logs deleted and users work time has been reset")
    users = db.table('users')
    db.purge_table('time_logs')
    for u in users:
        u["enter_time"] = 0
        u["work_time"] = 0


def show_all_logs():
    time_logs = db.table('time_logs')
    output = ""
    for l in time_logs:
        output += l["card_id"] + "\t" + l["terminal"] + "\t" + l["date"] + "\n"
    print(output)


res = "%0.12d" % random.randint(0, 999999999999)


def choose_card_to_log():
    cards = db.table('cards')
    default_terminal = db.table('terminals').all()[0]["id"]

    print('\nPossible actions. Press'
          '\n1 to log random unregistred card '
          '\n2 to log random existing card '
          '\n3 to log new card by yourself')
    while True:
        try:
            user_choice = int(input('>'))
            break
        except ValueError:
            print('Enter right number ')

    if user_choice == 1:
        unreg_id = "%0.8d" % random.randint(0, 99999999)
        while cards.get(where('id') == unreg_id):
            unreg_id = "%0.8d" % random.randint(0, 99999999)

        print(f'logging random unregistred card with id: {unreg_id}')
        log_card(unreg_id, default_terminal)
    elif user_choice == 2:
        reg_id = random.randint(0, len(cards) - 1)
        print(f'logging random registred card with id: {cards.all()[reg_id]["id"]} ')
        log_card(cards.all()[reg_id]["id"], default_terminal)

    elif user_choice == 3:
        id_ = input('Enter id for card to log: ')
        log_card(id_, default_terminal)


def time_to_seconds(time_):
    return int(time_.hour) * 3600 + int(time_.minute) * 60 + int(time_.second)


def display_menu():
    while True:
        print('\nPossible actions. Press'
              '\n1 to add new terminal '
              '\n2 to delete terminal '
              '\n3 to add new user '
              '\n4 to delete  user '
              '\n5 to assign card to the user'
              '\n6 to remove card from the user'
              '\n7 to generate time report for specified user'
              '\n8 to clear logs database'
              '\n9 to show  all logs in database'
              '\n0 to end the program'
              '\n11 to log new card (temporary feature)')
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
            id__ = input('Enter id of user whose card you want to remove: ')
            delete_assigned_card(id__)
        elif user_choice == 7:
            id_ = input('Enter id of user whose report you want to see: ')
            generate_report(id_)
        elif user_choice == 8:
            print("Clearing logs database")
            reset_users_timesheet()
        elif user_choice == 9:
            print("Showing all the logs\n")
            show_all_logs()
        elif user_choice == 0:
            print("Exiting the server")
            break
        elif user_choice == 11:
            choose_card_to_log()
        else:
            print("There is no such command")


def main():
    display_menu()


if __name__ == '__main__':
    main()
