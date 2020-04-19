from datetime import date
from guzi.models import User

from models import Simulator, UserGenerator, GrapheDrawer, SimpleYearlyDeathGod


POPULATION_SIZE = 10
DAYS = 2000

if __name__ == "__main__":
    simulator = Simulator()
    death_god = SimpleYearlyDeathGod()
    graph_drawer = GrapheDrawer(simulator)

    simulator.add_users(UserGenerator.generate_users(date(2010, 1, 1), POPULATION_SIZE))
    graph_drawer.add_point()
    
    year_counter = 0
    for i in range(DAYS):
        if year_counter >= 365:
            year_counter = 0
            death_god.give_birth(simulator.user_pool)
            death_god.give_death(simulator.user_pool)
        simulator.new_day()
        graph_drawer.add_point()
        year_counter += 1
        print("day {} => {} users for {} total guzis".format(i, len(simulator.user_pool), sum([len(u.guzi_wallet) for u in simulator.user_pool])))



    plot = graph_drawer.draw("date", "guzis_on_road")
    plot.show()
