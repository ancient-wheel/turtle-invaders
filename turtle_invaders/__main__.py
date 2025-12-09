import logging
from turtle_invaders.app import App

logging.basicConfig(format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def main():
    app = App()
    app.start()


if __name__ == "__main__":
    main()
