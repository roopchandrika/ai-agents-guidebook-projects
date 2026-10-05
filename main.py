import sys

from dotenv import load_dotenv

load_dotenv()

from crew import find_hotels  # noqa: E402

if __name__ == "__main__":
    request = " ".join(sys.argv[1:]) or "Hotels in Paris from 10 to 14 December for 2 adults"
    print(find_hotels(request))
