import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    # Step 1: Initialization of the starting point
    # Create the first node representing the source person
    start = Node(state=source, parent=None, action=None)
    
    # Frontier: This is the checklist of the nodes we will explore
    frontier = QueueFrontier() # FIFO
    frontier.add(start) # Add the start point to the frontier

    # Explored set: Keeps tracks of what have been explored alredy
    explored = set()
    frontier_states = {source}

    # Step 2: Main search loop.
    while not frontier.empty():    
        
        # First remove the next node from the frontier to explore
        node = frontier.remove()
        frontier_states.remove(node.state)

        # Then check if we reached our goal
        if node.state == target:

            # If we did... 
            path = [] # This will hold our final path as a list of (movie_id, person_id) tuples
            while node.parent is not None:
                # Node.action contains the (movie_id, person_id) that got us here, we add this step to our path
                path.append(node.action)
                # Move to the parent node
                node = node.parent
            # We built the path BUT Backwards (target -> Source)
            path.reverse() # Now source -> target
            return path # And just return it
        
        # Step 3: Mark this person as explored
        explored.add(node.state)
        
        # Step 4: Explore all the neighbors
        for movie_id, person_id in neighbors_for_person(node.state):

            # Only add if not alredy explored and they are not alredy in the frontier
            if person_id not in explored and person_id not in frontier_states:
                
                # Create a new node for this neighbor
                # - state: where we'd be
                # - parent: where we came from
                # - action: the movie_id and person_id pair that connects them
                child = Node(
                    state=person_id,
                    parent=node,
                    action=(movie_id, person_id)
                )
                
                # Add it to the frontier
                frontier.add(child)
                frontier_states.add(person_id)

    # Step 5: After exiting the loop with nothing, we've explored all reachable people and didn't find the target
    return None

def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
