# run.py
import sys
from input_translator.main import main

if __name__ == '__main__':
    # This ensures that when the bundled .exe runs, it calls your main function
    sys.exit(main())