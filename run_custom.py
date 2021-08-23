import os
import sys

from sc2.player import Bot
from sc2 import Race

sys.path.insert(1, "python-sc2")

from bot_loader import GameStarter, BotDefinitions
from version import update_version_txt

from SelfAssemblingWorkerDisassembler.self_assembling_worker_disassembler import SelfAssemblingWorkerDisassembler

def add_definitions(definitions: BotDefinitions):
    # definitions.add_bot(
    #     "emg", lambda params: Bot(Race.Terran, ExponentialMeatGrinder("2")), None
    # )
    definitions.add_bot(
        "sawd", lambda params: Bot(Race.Protoss, SelfAssemblingWorkerDisassembler("0")), None
    )
    # definitions.add_bot(
    #     "oracles", lambda params: Bot(Race.Protoss, Oracle("0")), None
    # )


def main():
    update_version_txt()
    root_dir = os.path.dirname(os.path.abspath(__file__))
    ladder_bots_path = os.path.join("Bots")
    ladder_bots_path = os.path.join(root_dir, ladder_bots_path)
    definitions: BotDefinitions = BotDefinitions(ladder_bots_path)
    add_definitions(definitions)
    starter = GameStarter(definitions)
    starter.play()


if __name__ == "__main__":
    main()
