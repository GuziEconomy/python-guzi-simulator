import argparse
from datetime import date

from models import Simulator, UserGenerator, GrapheDrawer, SimpleYearlyDeathGod


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simulate Guzi interactions')
    parser.add_argument('-u', type=int, dest='user_count', required=True,
                       help='number of users to simulate')
    parser.add_argument('-d', type=int, dest='days', default=365,
                       help='number of days simulation should last')
    parser.add_argument('-f', type=int, dest='frequency', default=1,
                       help='days between each graph point')
    parser.add_argument('-x', type=str, dest='x', help='x axe', choices=["date", "guzis_on_road", "average_daily_guzi", "user_count"])
    parser.add_argument('-y', type=str, dest='y', nargs='+', help='y axe', choices=["date", "guzis_on_road", "average_daily_guzi", "user_count"])

    args = parser.parse_args()
    print(args)

    simulator = Simulator()
    death_god = SimpleYearlyDeathGod()
    graph_drawer = GrapheDrawer(simulator)

    simulator.add_users(UserGenerator.generate_users(date(2010, 1, 1), args.user_count))
    graph_drawer.add_point()
    
    day_counter = 0
    for i in range(args.days):
        if day_counter % 365 == 0:
            simulator.user_pool = death_god.give_birth(simulator.user_pool)
            simulator.user_pool = death_god.give_death(simulator.user_pool)

        if day_counter % args.frequency == 0:
            graph_drawer.add_point()
            print("day {} (year {})=> {} users for {} total guzis, jonhy total {} earns daily {}".format(
                day_counter,
                int(day_counter/365.25),
                len(simulator.user_pool),
                sum([u.guzi_wallet for u in simulator.user_pool]),
                simulator.user_pool[0].total_accumulated,
                int(simulator.user_pool[0].total_accumulated ** (1/3) + 1)))
        simulator.new_day()
        day_counter += 1

    if args.x and args.y:
        for y in args.y:
            graph_drawer.add_graph(args.x, y)

        plot = graph_drawer.draw()
        plot.show()
