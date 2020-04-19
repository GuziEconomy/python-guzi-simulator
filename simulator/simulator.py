from datetime import date
from guzi.models import User

from models import Simulator, UserGenerator, GrapheDrawer, SimpleYearlyDeathGod


if __name__ == "__main__":
    simulator = Simulator()
    user_generator = UserGenerator()
    graph_drawer = GrapheDrawer(simulator)

    simulator.add_users(user_generator.generate_users(date(2010, 1, 1), 100))
    graph_drawer.add_point()
    
    for _ in range(10000):
        simulator.new_day()
        graph_drawer.add_point()

    plot = graph_drawer.draw("date", "guzis_on_road")
    plot.show()
