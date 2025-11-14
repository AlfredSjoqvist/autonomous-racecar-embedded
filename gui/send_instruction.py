import socket


# RPi:ns IP här
EXTERN_IP = "172.20.10.4"

# Skriv samma port som du valt som MY_IP på RPi:n här
SENDER_PORT = 12302

"""
Send a message to EXTERN_IP via SENDER_PORT.
"""


def send():
    print(f"Connecting to {EXTERN_IP}:{SENDER_PORT}...")
    socketB = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socketB.connect((EXTERN_IP, SENDER_PORT))

    try:
        while True:
            message = input("Send message to RPi: ")

            if message.lower() == "exit":
                break

            socketB.send(message.encode())

    finally:
        socketB.close()
        print("Sender connection closed.")


send()
