import sys

from dotenv import load_dotenv

load_dotenv()

from crew import find_flights  # noqa: E402

if __name__ == "__main__":
    request = " ".join(sys.argv[1:]) or "Flights from San Francisco to New York on 21st November"
    print(find_flights(request))
