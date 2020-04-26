import uuid
from datetime import date, timedelta
import matplotlib.pyplot as plt
import random
from pylab import array

from guzi.models import User, GuziCreator, Company

def random_date(start, end):
    """
    This function will return a random datetime between two datetime objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return start + timedelta(seconds=random_second)


class SimpleUser(User):
    """A User but light in memory usage"""
    def __init__(self, id, birthdate):
        self.id = id
        self.birthdate = birthdate
        self.guzi_wallet = 0
        self.guza_wallet = 0
        self.total_accumulated = 0
        self.guza_trashbin = 0
        self.balance = {"income": 0, "outcome": 0}

    def daily_guzis(self):
        return int(self.total_accumulated ** (1/3) + 1)

    def outdate(self, guzis):
        for guzi in guzis:
            if self._is_guzi(guzi):
                self.guzi_wallet -= 1
                self.total_accumulated += 1
            if self._is_guza(guzi):
                self.guza_wallet -= 1

    def pay(self, guzis):
        self.balance["income"] += len(guzis)

    def spend_to(self, target, amount):
        if amount < 0:
            raise ValueError("Cannot spend negative amount")
        if amount > self.guzi_wallet:
            raise ValueError("User cannot pay this amount")
        if target is self:
            self.total_accumulated += amount
        else:
            target.pay([GuziCreator.create_guzi(self, date(2000, 1, 1), i) for i in range(amount)])
        self.guzi_wallet -= amount

    def give_guzas_to(self, target, amount):
        if amount < 0:
            raise ValueError("Cannot give negative amount")
        if amount > self.guza_wallet:
            raise ValueError("User cannot give this amount")
        if not isinstance(target, Company):
            raise ValueError("Can only give Guzas to Company, not {}".format(type(target)))
        target.add_guzas([GuziCreator.create_guza(self, date(2000, 1, 1), i) for i in range(amount)])
        self.guza_wallet -= amount
        self.balance["outcome"] += amount

    def check_balance(self):
        difference = self.balance["income"] - self.balance["outcome"]
        if difference > 0:
            self.balance["income"] -= difference
            self.total_accumulated += difference

    def check_outdated_guzis(self, date):
        number_of_guzis_to_add = self.daily_guzis()
        difference_guzi = self.guzi_wallet - number_of_guzis_to_add*30
        difference_guza = self.guza_wallet - number_of_guzis_to_add*30

        if difference_guzi > 0:
            self.guzi_wallet -= difference_guzi
            self.total_accumulated += difference_guzi
        if difference_guza > 0:
            self.guza_wallet -= difference_guza
            self.guza_trashbin += difference_guza

    def create_daily_guzis(self, date):
        number_of_guzis_to_add = self.daily_guzis()
        self.guzi_wallet += number_of_guzis_to_add
        self.guza_wallet += number_of_guzis_to_add


class UserGenerator:
    def generate_user(birthdate):
        randId = str(uuid.uuid4())

        return SimpleUser(randId, birthdate)

    def generate_users(birthdate, count):
        return [UserGenerator.generate_user(birthdate) for _ in range(count)]

    def generate_random_user(min_birth=date(1940, 1, 1), max_birth=date.today()):
        """
        Return a User instance with random birthdate and random id
        """
        randBirthdate = random_date(min_birth, max_birth)
        
        return UserGenerator.generate_user(randBirthdate)

    def generate_random_adult_user():
        return UserGenerator.generate_random_user(date(1940, 1, 1), date.today()-18*timedelta(days=365, hours=6))


class SimpleYearlyDeathGod:
    total_2019_population = 67028048
    total_2019_born = 758610
    total_2019_death = 614138

    def how_much_born(self, population_size):
        """
        return the number of new births should happen prorated to given
        population_size
        """
        return int(self.total_2019_born * population_size / self.total_2019_population)

    def how_much_die(self, population_size):
        """
        return the number of dead should happen prorated to given
        population_size
        """
        return int(self.total_2019_death * population_size / self.total_2019_population)

    def give_birth(self, population, date=date.today()):
        """
        Add to the list new users prorated to given population size
        """
        for _ in range(self.how_much_born(len(population))):
            population.append(UserGenerator.generate_user(date))
        return population

    def give_death(self, population):
        """
        return a list of users belonging to given population who should die
        Note : kill always the oldest, like a canicule or a coronavirus
        """
        death_count = self.how_much_die(len(population))
        return population[death_count:]


class GrapheDrawer:
    """
    Get informations from a Simulator and draw them with matplotlib
    """
    def __init__(self, simulator):
        self.simulator = simulator
        self.points = {
            "date": [],
            "user_count": [],
            "average_daily_guzi": [],
            "guzis_on_road": [],
        }
        self.to_draw = {"x": None, "y": []}
        self.colors = ["b-", "r-", "g-", "y-", "o-"]


    def add_point(self):
        self.points["date"].append(self.simulator.current_date)
        self.points["user_count"].append(len(self.simulator.user_pool))
        self.points["average_daily_guzi"].append(sum([u.daily_guzis() for u in self.simulator.user_pool])/len(self.simulator.user_pool))
        self.points["guzis_on_road"].append(sum([u.guzi_wallet for u in self.simulator.user_pool]))

    def add_graph(self, x, y):
        if self.to_draw["x"] is not None and x != self.to_draw["x"]:
            raise ValueError("Cannot add different x ({} != {})".format(self.to_draw["x"], x))
        self.to_draw["x"] = x
        if y not in self.to_draw["y"]:
            self.to_draw["y"].append(y)

    def draw(self):
        graph_count = len(self.to_draw["y"])
        if self.to_draw["x"] is None:
            raise ValueError("You need to set an 'x' using add_graph(x,y) before calling draw()")
        if graph_count == 0:
            raise ValueError("You need to set an 'y' using add_graph(x,y) before calling draw()")

        fig, host = plt.subplots()
        if graph_count > 2:
            fig.subplots_adjust(right=0.75*(graph_count-2))

        p, = host.plot(
            self.points[self.to_draw["x"]],
            self.points[self.to_draw["y"][0]],
        self.colors[0], label=self.to_draw["y"][0])

        host.set_xlabel(self.to_draw["x"])
        host.set_ylabel(self.to_draw["y"][0])
        host.yaxis.label.set_color(p.get_color())

        for i in range(1, len(self.to_draw["y"])):
            par = host.twinx()
            par.spines["right"].set_position(("axes", 1 + 0.2*(i-1)))
            p, = par.plot(
                self.points[self.to_draw["x"]],
                self.points[self.to_draw["y"][i]],
                self.colors[i%len(self.colors)], label=self.to_draw["y"][i])
            par.set_ylabel(self.to_draw["y"][i])
            par.yaxis.label.set_color(p.get_color())


        return plt


class RandomTrader:
    """
    Handle paiements between users randomly
    """
    def __init__(self, user_pool, company_pool=[]):
        self.user_pool = user_pool
        self.company_pool = company_pool

    def trade_guzis(self, k=0):
        """
        make paiements from k users, default 0
        If k=0, each user makes a paiement <= it's wallet size
        """
        if k == 0:
            k = len(self.user_pool)
        users = random.sample(self.user_pool, k=k)
        for u in users:
            u.spend_to(random.choice(self.user_pool), random.randrange(1, u.guzi_wallet))

    def trade_guzas(self, k=0):
        """
        Give guzas from k users to companies in company_pool
        If k=0, each user makes a give <= it's wallet size
        """
        users = random.sample(self.user_pool, k=k)
        for u in users:
            u.give_guzas_to()

class Simulator:
    """
    Simulator handles user pool and passing days
    """
    def __init__(self, start_date=date.today()):
        self.start_date = start_date
        self.current_date = start_date
        self.user_pool = []

    def add_user(self, user):
        self.user_pool.append(user)

    def add_users(self, users):
        for user in users:
            self.add_user(user)

    def new_day(self):
        self.current_date += timedelta(days=1)
        for user in self.user_pool:
            user.check_balance()
            user.check_outdated_guzis(self.current_date)
            user.create_daily_guzis(self.current_date)

    def new_days(self, days):
        for i in range(days):
            self.new_day()
