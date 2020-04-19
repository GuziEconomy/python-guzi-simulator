import string, random
from datetime import date, timedelta
from guzi.models import User


class UserGenerator:
    def generate_random_user(self, min_birth=date(1940, 1, 1), max_birth=date.today()):
        """
        Return a User instance with random birthdate and random id
        """
        randId = self._randomword(20)
        randBirthdate = self._random_date(min_birth, max_birth)
        
        return User(randId, randBirthdate)

    def generate_random_adult_user(self):
        return self.generate_random_user(date(1940, 1, 1), date.today()-18*timedelta(days=365, hours=6))

    def _random_date(self, start, end):
        """
        This function will return a random datetime between two datetime objects.
        """
        delta = end - start
        int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
        random_second = random.randrange(int_delta)
        return start + timedelta(seconds=random_second)

    def _randomword(self, length):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))


class Simulator:
    """
    Simulator 
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


class SimpleDeathGod:
    total_2019_population = 67028048
    total_2019_born = 758610
    total_2019_death = 614138

    def who_is_born(self, users):
        """
        return new users which should be born depending on the age of given
        users (meaning : can they be parents ?)
        """
        pass

    def who_is_dead(self, users):
        """
        return a list of users belonging to given users who should statisticaly
        die based on their age.
        """
        pass
