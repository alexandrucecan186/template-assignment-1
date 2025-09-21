from pathlib import Path
from runner.runner import Runner

def main():
    # Build path to data/question_1a relative to this file
    data_dir = Path(__file__).resolve().parent.parent / "data" / "question_1a"
    Runner(str(data_dir)).run_single_simulation()

if __name__ == "__main__":
    main()
