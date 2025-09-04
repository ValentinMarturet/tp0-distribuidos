import argparse


def generate_docker_compose_text(number):

    clients = generate_client_services(number)

    compose_template = f"""
name: tp0
services:
  server:
    container_name: server
    image: server:latest
    volumes:
      - ./server/config.ini:/config.ini
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
    networks:
      - testing_net

{clients}

networks:
  testing_net:
    ipam:
      driver: default
      config:
        - subnet: 172.25.125.0/24
"""
    return compose_template




def generate_client_services(number):
    services = ""

    for i in range(1, number + 1):
        client_template = f"""
  client{i}:
    container_name: client{i}
    image: client:latest
    volumes:
      - ./client/config.yaml:/config.yaml
      - ./client/data/agency-{i}.csv:/data/agency.csv
    entrypoint: /client
    environment:
      - CLI_ID={i}
      - BET_NAME=Santiago Lionel
      - BET_LASTNAME=Lorca
      - BET_DOCUMENT=30904465
      - BET_BIRTHDATE=1999-03-17
      - BET_NUMBER=7574
    networks:
      - testing_net
    depends_on:
      - server
"""

        services += client_template
    return services



def write_compose_file(file_path, number):
    compose_text = generate_docker_compose_text(number)
    with open(f"./{file_path}", 'w') as f:
        f.write(compose_text)



def __main__():
    parser = argparse.ArgumentParser(description="<name of docker compose file> <number of clients>")
    parser.add_argument("file", type=str, help="file name")
    parser.add_argument("number", type=int, help="number of clients")
    args = parser.parse_args()

    write_compose_file(args.file, args.number)
    print(f"Docker compose file '{args.file}' generated with {args.number} clients.")



if __name__ == "__main__":
    __main__()