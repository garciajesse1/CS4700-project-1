import socket
from socket import SocketType
import json
import random
import ssl
import argparse

with open('wordle_word_list.txt', 'r') as f:
    wordle_words = f.readlines()
WORDLE_WORDS = {word.strip() for word in wordle_words}

# telnet proj1.4700.network 27993
def client(port:int=None, hostname:str="proj1.4700.network", Northeastern_username:str="garcia.jesse1", s:bool=False):
    if len(hostname) < 1 or len(Northeastern_username) < 1:
        raise ValueError("Program requires a hostname and/or northeastern username")

    if port == None:
        if s == True:
            port = 27994
        else:
            port = 27993

    connection_result = 1
    # create the socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # connect the socket
    connect_tuple = (hostname, port)
    connection_result = sock.connect_ex(connect_tuple)

    if s:
        # default_context w/ no args uses local generated certificated
        context = ssl.create_default_context()
        sock = context.wrap_socket(sock, server_hostname=hostname)

    # Return error code and exit program if socket cannot connect to the server
    if connection_result != 0:
        raise Exception(f"Socket could not connect to server. Error code: {connection_result}")

    # server hangs if there is no \n terminator at the end of the sent data
    hello_message = f'{{"type": "hello", "northeastern_username": "{Northeastern_username}"}}\n'
    
    # receive game_id and store it
    hello_message_json_dict = send_data(sock, hello_message, s)
    game_id = hello_message_json_dict['id']

    # start gussing that guy
    chosen_guess = "crane"
    guess_message = f'{{"type": "guess", "id": "{game_id}", "word": "{chosen_guess}"}}\n'
    guess_message_json_dict = send_data(sock, guess_message, s)
    marks = guess_message_json_dict['guesses'][0]['marks']
    letter_bank = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 
               'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 
               's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    updated_letter_bank = update_letter_bank(chosen_guess, marks, letter_bank)
    guess_num = 0
    
    while True:
        # update chosen guess with the new one
        chosen_guess = get_next_guess(chosen_guess, marks, updated_letter_bank)
        # send next guess
        guess_message = f'{{"type": "guess", "id": "{game_id}", "word": "{chosen_guess}"}}\n'
        guess_message_json_dict = send_data(sock, guess_message, s)
        # increase guess_num so we view the most recent guess
        if guess_message_json_dict["type"] == "bye":
            break
        guess_num += 1
        
        try:
            marks = guess_message_json_dict['guesses'][guess_num]['marks']
        except KeyError:
            print("We key errored because guessed word was not known.")
            print("This should not happen now that I used the correct word list.")
            raise KeyError
        
        # update the letter bank to remove letters with mark '0'
        updated_letter_bank = update_letter_bank(chosen_guess, marks, updated_letter_bank)
        
    sock.close()
    print(guess_message_json_dict["flag"])

"""
    Removes only letters in letter bank that have a mark 0 from the server response.
    
    Args:
    - chosen_guess: The previously chosen guess.
    - letter_bank: The previous bank of letters.
    Returns:
    - The updated letter bank.
"""
def update_letter_bank(chosen_guess:str, marks:list, letter_bank:list):
    chosen_guess_list = list(chosen_guess)
    updated_letter_bank = letter_bank.copy()
    for idx, char in enumerate(chosen_guess_list):
        if marks[idx] == 0 and char in updated_letter_bank:
                updated_letter_bank.remove(char)
    
    return updated_letter_bank

"""
    Gets the next wordle guess. 
    Letters that have mark 1 (in word but wrong place) or mark 2 (in correct place) 
    will always be present in the next guess.
    
    Args:
    - prev_guess: the previous wordle guess.
    - marks: the returned marks list.
    - letter_bank: current bank of unused letters available.
    Returns:
    - The next wordle guess as a string.
"""
def get_next_guess(chosen_guess:str, marks:list, letter_bank:list) -> str:
    chosen_guess_list = list(chosen_guess)
    
    available_idxs = [0, 1, 2, 3, 4]
    mark_1_letters = []
    mark_0_letters = []
    next_guess = ["", "", "", "", ""]
    for idx, char in enumerate(chosen_guess_list):
        # letter in right spot
        if marks[idx] == 2:
            # replace blank spot with char
            next_guess.pop(idx)
            next_guess.insert(idx, char)
            available_idxs.remove(idx)
        # letter in wrong spot
        elif marks[idx] == 1:
            # choose another random spot for the letter
            mark_1_letters.append(char)
        elif marks[idx] == 0:
            mark_0_letters.append(random.choice(letter_bank))
    
    # randomize available letters until a legal word forms.
    final_next_guess = ""
    while final_next_guess not in WORDLE_WORDS:
        
        # weird edge case where my program hangs when there is 1 available spot and 
        # all others are filled with mark '2' letters
        if len(available_idxs) == 1:
            idx = available_idxs[0]
            temp_next_guess = next_guess.copy()
            temp_next_guess[idx] = random.choice(letter_bank)
            
            final_next_guess = ""
            for char in temp_next_guess:
                final_next_guess = final_next_guess + char
            continue
            
        # randomize letters in each '0' marked spot
        for char in mark_0_letters:
            mark_0_letters.pop(0)
            mark_0_letters.append(random.choice(letter_bank))
        temp_available_idxs = available_idxs.copy()
        temp_next_guess = next_guess.copy()
        
        next_chosen_letters = mark_1_letters.copy() + mark_0_letters.copy()
        # randomize order of letters in each non '2' marked spot
        for char in next_chosen_letters:
            rand_idx = random.choice(temp_available_idxs)
            temp_next_guess.pop(rand_idx)
            temp_next_guess.insert(rand_idx, char)
            temp_available_idxs.remove(rand_idx)
        
        # turn temp_next_guess into a string and check if valid
        final_next_guess = ""
        for char in temp_next_guess:
            final_next_guess = final_next_guess + char
        
    return final_next_guess

"""
    Sends a message to the server and returns the received json string formatted as a dict.
    
    Args: 
    - socket: the socket to send and receive data from.
    - message: the string message in json format ending with a \n terminator.
    Returns:
    - The full string received from the server formatted as a dict.
"""
def send_data(socket:SocketType, message:str, s:str) -> dict | None:    
    # encode the message to bytes:
    message = message.encode("utf-8")
    
    if s != None:
        pass
    # send it
    socket.sendall(message)
    
    # receive message back
    BYTE_AMOUNT = 1024
    
    full_message = ""
    while "\n" not in full_message:
        # after each recv call, bytes are removed from the received buffer. so new data is always returned.
        bytes_received = socket.recv(BYTE_AMOUNT)
        
        if len(bytes_received.decode("utf-8")) < 1:
            print(f"No bytes were received from server socket. Bytes received: {bytes_received}")
            return None

        decoded_received_json = bytes_received.decode("utf-8")
        
        full_message = full_message + decoded_received_json
    
    json_data = json.loads(full_message)
    
    return json_data

if __name__ == "__main__":
    # positional arguments dont have a - in front of the name
    parser = argparse.ArgumentParser(description="The cool project 1 parser.")
    parser.add_argument("-p", type=int, help="port number")
    # on-off flag: "store_true"
    parser.add_argument("-s", action="store_true", help="flag to use tls")
    parser.add_argument("hostname", type=str, help="hostname")
    parser.add_argument("Northeastern_username", type=str, help="northeastern username")

    args = parser.parse_args()
    
    client(args.p, args.hostname, args.Northeastern_username, args.s)