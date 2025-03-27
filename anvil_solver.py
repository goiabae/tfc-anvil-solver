import sys
import enum
from itertools import product
from itertools import groupby
from typing import TypeVar

K = TypeVar('K')
V = TypeVar('V')

class Move(enum.Enum):
  HIT = 'hit'
  DRAW = 'draw'
  PUNCH = 'punch'
  BEND = 'bend'
  UPSET = 'upset'
  SHRINK = 'shrink'

STEP_TO_MOVE = {
  -3: Move.HIT,
  -6: Move.HIT,
  -9: Move.HIT,
  -15: Move.DRAW,
  +2: Move.PUNCH,
  +7: Move.BEND,
  +13: Move.UPSET,
  +16: Move.SHRINK
}

def reverse_mapping(m: dict[K, V]) -> dict[V, list[K]]:
  rm: dict[V, list[K]] = {}
  for k, v in m.items():
    rm.setdefault(v, []).append(k)
  return rm

MOVE_TO_STEPS = reverse_mapping(STEP_TO_MOVE)

MAX_STEP_COUNT = 16

# https://github.com/TerraFirmaCraft/TerraFirmaCraft/blob/1.21.x/src/main/java/net/dries007/tfc/common/component/forge/ForgeStep.java#L35
ANVIL_BOTTOM_BOUND = 1-1
ANVIL_TOP_BOUND = 150-1

def solve_aux(target: int, so_far: int, steps: tuple[int, ...], target_step_count) -> tuple[int, ...] | None:
  if so_far < ANVIL_BOTTOM_BOUND or so_far > ANVIL_TOP_BOUND or len(steps) > target_step_count:
    return None

  if so_far == target and target_step_count == len(steps):
    return steps

  for x in (+16, +13, +7, +2, -15, -9, -6, -3):
    solution = solve_aux(target, so_far + x, steps + (x,), target_step_count)
    if solution is not None:
      return solution

  return None

def solve(target: int, max_step_count, suffix) -> tuple[int, ...] | None:
  for target_step_count in range(0+1, max_step_count+1):
    solution = solve_aux(target, 0, tuple(), target_step_count)
    if solution is not None:
      return solution

  return None

def group_consecutive(lst):
    return [(len(list(group)), key) for key, group in groupby(lst)]

def choose_smallest(x, y) -> tuple[tuple[int, ...], tuple[int, ...]] | None:
  if x is None or y is None:
    return x or y
  xs, xl = x
  ys, yl = y
  return x if len(xs) < len(ys) else y

def usage():
  moves = ', '.join([m.value for m in Move])
  print(f"""Usage:
  anvil_solver.py <target> [third-to-last] [second-to-last] [last]

  <target>          Valor numerico final da bigorna

  [third-to-last]
  [second-to-last]
  [last]            Um de {moves}
""")

def main(argv) -> None:
  if len(argv) < 2:
    usage()
    return

  target = int(argv[1])
  required_last_hits = list(map(Move, argv[2:]))
  smallest = None

  for suffix in product(*map(lambda x: MOVE_TO_STEPS[x], required_last_hits)):
    even_smaller_step_count = min(MAX_STEP_COUNT - len(required_last_hits), smallest and len(smallest)-1 or MAX_STEP_COUNT)
    maybe_solution = solve(target -sum(suffix), even_smaller_step_count, suffix)
    smallest = choose_smallest(smallest, maybe_solution and (maybe_solution, suffix) or None)

  if smallest is None:
    print("No solutions found")
    return

  ss, sl = smallest
  solution = ss + sl

  def format_term(c, v):
    return ("" if v < 0 else "+") + str(v) + (f"*{c}" if c > 1 else "")

  terms = [format_term(c, v) for c, v in group_consecutive(solution)]

  print(f"Best solution for {target} with length {len(solution)}:")
  print(' '.join(terms))

if __name__ == "__main__":
  main(sys.argv)
