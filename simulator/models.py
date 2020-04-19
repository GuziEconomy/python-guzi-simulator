import uuid
from datetime import date, timedelta
import matplotlib.pyplot as plt
import random

from guzi.models import User

def random_date(start, end):
    """
    This function will return a random datetime between two datetime objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return start + timedelta(seconds=random_second)

class UserGenerator:
    def generate_user(birthdate):
        randId = str(uuid.uuid4())

        return User(randId, birthdate)

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

    def who_is_born(self, population_size, date=date.today()):
        """
        return a list of new users prorated to given population size
        """
        return [UserGenerator.generate_user(date) for _ in range(self.how_much_born(population_size))]

    def who_is_dead(self, population):
        """
        return a list of users belonging to given population who should die
        Note : kill always the oldest, like a canicule or a coronavirus
        """
        return population[:self.how_much_die(len(population))]


class GrapheDrawer:
    """
    Get informations from a Simulator and draw them with matplotlib
    """
    def __init__(self, simulator):
        self.simulator = simulator
        self.points = []

    def add_point(self):
        self.points.append({
            "date": self.simulator.current_date,
            "user_count": len(self.simulator.user_pool),
            "guzis_on_road": self.simulator.guzis_on_road,
        })

    def draw(self, x_label, y_label):
        x_points = []
        y_points = []
        for p in self.points:
            x_points.append(p[x_label])
            y_points.append(p[y_label])

        x = array(x_points)
        y = array(y_points)

        plt.xlabel(x_label)
        plt.ylabel(y_label)

        plt.plot(x, y)
        return plt


class Simulator:
    """
    Simulator handles user pool and passing days
    """
    def __init__(self, start_date=date.today()):
        self.start_date = start_date
        self.current_date = start_date
        self.user_pool = []
        self.user_count = 0
        self.guzis_on_road = 0

    def add_user(self, user):
        self.user_pool.append(user)
        self.user_count += 1
        self.guzis_on_road += len(user.guzi_wallet)

    def add_users(self, users):
        for user in users:
            self.add_user(user)

    def new_day(self):
        self.guzis_on_road = 0
        self.current_date += timedelta(days=1)
        for user in self.user_pool:
            user.check_balance()
            user.check_outdated_guzis(self.current_date)
            user.create_daily_guzis(self.current_date)
            self.guzis_on_road += len(user.guzi_wallet)

    def new_days(self, days):
        for i in range(days):
            self.new_day()
