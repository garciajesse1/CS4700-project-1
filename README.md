High Level Approach:
1. Initialize a client socket and connect to the server. If the -s flag is provided, wrap the socket in a tls context.
2. Send the server the 'hello' message and store the game_id.
3. Send the hardcoded initial guess, get the returned marks, update the letter_bank, then start the guessing loop.
4. Wait for the 'bye' message from the server and grab the key from the response.
5. Print the key.

Challenges:
The main 2 challenges I faced were implementing the tls connection and debugging my wordle guessing algorithm.
The tls connection was tricky for me because I was not too informed on what it did and how it works. Following some python documentation led me to implementing the tls wrapper correctly, but I was still confused on what tls did. I then watched some youtube tutorials so I could learn more about it.
The wordle guessing algorithm I chose caused me problems because of a bug where the program would indefinitly try to find a word in the word_list with invalid letters that were marked '1' by the server response. I noticed this would only happen when there was one spot left and all other letters were correct and marked '2'. So I fixed the bug by hard coding a condition for this edge case. I was also using the wrong word list which would cause my program to send invalid words to the server and terminate the connection. This confused me for a bit.

Guessing Strategy:
The program starts with a common wordle starting word: 'crane'. There is a letter bank that stores remaining letters. If a guessed letter is returned with mark '0' then it is removed from the letter bank. The guessing function creates an array of five strings and assigns letters to their corresponding spots in the array if they were marked '2'. For all '0' marked spots, random letters from the letter bank are chosen. The letters marked '0' and marked '1' are then randomly assigned positions in the new word until a valid word is found. Letters not marked '0' are always present in the new word.

Testing Overview:
I used a lot of print statements to verify functionality then removed them before submitting the project.
There are also connection and other verification checks I use to confirm I am getting the correct data from the sockets I am using.

Resources:
- https://docs.python.org/3/library/ssl.html
- https://docs.python.org/3/library/argparse.html
- https://docs.python.org/3/library/socket.html#socket.socket.recv

AI was used only for clarifying questions. For example explaining to me how the tls certificates/handshakes work.