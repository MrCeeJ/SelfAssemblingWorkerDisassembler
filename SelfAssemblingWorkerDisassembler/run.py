from SelfAssemblingWorkerDisassembler.self_assembling_worker_disassembler import SelfAssemblingWorkerDisassembler
from ladder import run_ladder_game

from sc2 import Race
from sc2.player import Bot

bot = Bot(Race.Protoss, SelfAssemblingWorkerDisassembler("0"))


def main():
    # Ladder game started by LadderManager
    print("Starting ladder game...")
    result, opponentid = run_ladder_game(bot)
    print(result, " against opponent ", opponentid)


if __name__ == '__main__':
    main()
