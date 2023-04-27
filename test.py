import requests

from helpers import match_finder, lookup


def main():
    player = "260823"
    match = "225921950"

    test = lookup(player)
    print(test)


if __name__ == "__main__":
    main()
