import unittest
from datetime import date
from guzi.models import User

from simulator.models import Simulator, UserGenerator


class TestUserGenerator(unittest.TestCase):
    """
    """
    def test_generate_user(self):
        user_generator = UserGenerator()

        user = user_generator.generate_random_user()

        self.assertIsInstance(user, User)

    def test_generate_adult_user(self):
        user_generator = UserGenerator()
        users = []

        for i in range(10):
            users.append(user_generator.generate_random_adult_user())

        for user in users:
            self.assertTrue(user.age() >= 18, "User {} (born {}) is only {} years old".format(user.id, user.birthdate, user.age()))


class TestSimulator(unittest.TestCase):
    """
    """
    def test_new_day_must_create_daily_guzis_in_users_wallets(self):
        """
        new_day should add the daily Guzis of all users. Here 1 each as the
        total_accumulated is always 0.
        """
        simulator = Simulator(date(2000, 1, 1))
        user_generator = UserGenerator()

        for i in range(10):
            simulator.add_user(user_generator.generate_random_adult_user())

        for i in range(10):
            self.assertEqual(len(simulator.user_pool[i].guzi_wallet), 0)
            self.assertEqual(len(simulator.user_pool[i].guza_wallet), 0)

        simulator.new_day()

        for i in range(10):
            self.assertEqual(len(simulator.user_pool[i].guzi_wallet), 1)
            self.assertEqual(len(simulator.user_pool[i].guza_wallet), 1)

    def test_new_day_must_check_balance_of_all_users(self):
        """
        a new_day should set the balance of each user back to 0 and add the
        bonuses to the users total_accumulated (which goes from 0 to 1)
        """
        simulator = Simulator(date(2000, 1, 1))
        user_generator = UserGenerator()

        for i in range(10):
            user = user_generator.generate_random_adult_user()
            user.balance.income.append("1234")
            simulator.add_user(user)

        for i in range(10):
            self.assertEqual(len(simulator.user_pool[i].total_accumulated), 0)

        simulator.new_day()

        for i in range(10):
            self.assertEqual(len(simulator.user_pool[i].total_accumulated), 1)

    def test_new_day_must_check_outdated_guzis_of_all_users(self):
        """
        new_day should move Guzis in guzi_wallet older than 30 days to the
        total_accumulated of it's owner
        """
        simulator = Simulator(date(2000, 1, 1))
        user_generator = UserGenerator()

        for i in range(10):
            user = user_generator.generate_random_adult_user()
            user.create_daily_guzis(date(2000, 1, 1))
            simulator.add_user(user)

        for i in range(10):
            self.assertEqual(len(simulator.user_pool[i].total_accumulated), 0)

        simulator.new_days(30)

        for i in range(10):
            self.assertEqual(len(simulator.user_pool[i].total_accumulated), 1)

    def test_new_day_must_create_daily_guzas_in_users_wallets(self):
        """
        new_day should add the daily Guzas of all users. Here 1 each as the
        total_accumulated is always 0.
        """
        simulator = Simulator(date(2000, 1, 1))
        user_generator = UserGenerator()

        for i in range(10):
            simulator.add_user(user_generator.generate_random_adult_user())

        for i in range(10):
            self.assertEqual(len(simulator.user_pool[i].guza_wallet), 0)
            self.assertEqual(len(simulator.user_pool[i].guza_wallet), 0)

        simulator.new_day()

        for i in range(10):
            self.assertEqual(len(simulator.user_pool[i].guza_wallet), 1)
            self.assertEqual(len(simulator.user_pool[i].guza_wallet), 1)

    def test_new_day_must_check_outdated_guzas_of_all_users(self):
        """
        new_day should move Guzas in guza_wallet older than 30 days to the
        guza_trashbin of it's owner
        """
        simulator = Simulator(date(2000, 1, 1))
        user_generator = UserGenerator()

        for i in range(1):
            simulator.add_user(user_generator.generate_random_adult_user())

        for i in range(1):
            self.assertEqual(len(simulator.user_pool[i].guza_wallet), 0)
            self.assertEqual(len(simulator.user_pool[i].guza_trashbin), 0)

        simulator.new_days(31)

        for i in range(1):
            # 31 because at 30, a Guzi was outdated and increased the daily earn
            # to 2/day
            self.assertEqual(len(simulator.user_pool[i].guza_wallet), 31)
            self.assertEqual(len(simulator.user_pool[i].guza_trashbin), 1)

    def test_new_day_multiple_times(self):
        simulator = Simulator(date(2000, 1, 1))
        user_generator = UserGenerator()

        for i in range(10):
            simulator.add_user(user_generator.generate_random_adult_user())

        for i in range(10):
            self.assertEqual(len(simulator.user_pool[i].guzi_wallet), 0)
            self.assertEqual(len(simulator.user_pool[i].guza_wallet), 0)

        simulator.new_day()
        simulator.new_day()
        simulator.new_day()

        self.assertEqual(simulator.current_date, date(2000, 1, 4))
        for i in range(10):
            self.assertEqual(len(simulator.user_pool[i].guzi_wallet), 3)
            self.assertEqual(len(simulator.user_pool[i].guza_wallet), 3)

    def test_new_days(self):
        """
        Running new_days(15) should increase guzi_wallet & guza_wallet of 
        15*1 (as total_accumulated = 0) = 15
        """
        simulator = Simulator(date(2000, 1, 1))
        user_generator = UserGenerator()

        for i in range(10):
            simulator.add_user(user_generator.generate_random_adult_user())

        for i in range(10):
            self.assertEqual(len(simulator.user_pool[i].guzi_wallet), 0)
            self.assertEqual(len(simulator.user_pool[i].guza_wallet), 0)

        simulator.new_days(15)

        self.assertEqual(simulator.current_date, date(2000, 1, 16))
        for i in range(10):
            self.assertEqual(len(simulator.user_pool[i].guzi_wallet), 15)
            self.assertEqual(len(simulator.user_pool[i].guza_wallet), 15)
