import socket


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("10.10.8.205", 5000))

    # set the instruction
    message = "SET BEEP"
    client.send(message.encode("utf-8"))

    # get the output from the server
    data = client.recv(1024)
    print("Message from Server :" + data.decode("utf-8"))

    client.close()


if __name__ == "__main__":
    main()
