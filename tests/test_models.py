import unittest
from datetime import date
from guzi.models import User

from simulator.models import Simulator, UserGenerator, SimpleYearlyDeathGod, GrapheDrawer


class TestUserGenerator(unittest.TestCase):
    """
    """
    def test_generate_user(self):
        user = UserGenerator.generate_user(date(2000, 1, 1))

        self.assertIsInstance(user, User)
        self.assertEqual(user.birthdate, date(2000, 1, 1))

    def test_generate_users(self):
        users = UserGenerator.generate_users(date(2000, 1, 1), 10)

        self.assertEqual(len(users), 10)

    def test_generate_random_user(self):
        user = UserGenerator.generate_random_user()

        self.assertIsInstance(user, User)

    def test_generate_random_adult_user(self):
        users = []

        for i in range(10):
            users.append(UserGenerator.generate_random_adult_user())

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

        for i in range(10):
            simulator.add_user(UserGenerator.generate_random_adult_user())

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

        for i in range(10):
            user = UserGenerator.generate_random_adult_user()
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

        for i in range(10):
            user = UserGenerator.generate_random_adult_user()
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

        for i in range(10):
            simulator.add_user(UserGenerator.generate_random_adult_user())

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

        for i in range(1):
            simulator.add_user(UserGenerator.generate_random_adult_user())

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

        for i in range(10):
            simulator.add_user(UserGenerator.generate_random_adult_user())

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

        for i in range(10):
            simulator.add_user(UserGenerator.generate_random_adult_user())

        for i in range(10):
            self.assertEqual(len(simulator.user_pool[i].guzi_wallet), 0)
            self.assertEqual(len(simulator.user_pool[i].guza_wallet), 0)

        simulator.new_days(15)

        self.assertEqual(simulator.current_date, date(2000, 1, 16))
        for i in range(10):
            self.assertEqual(len(simulator.user_pool[i].guzi_wallet), 15)
            self.assertEqual(len(simulator.user_pool[i].guza_wallet), 15)


class TestSimpleYearlyDeathGod(unittest.TestCase):
    def test_how_much_born_should_make_a_good_prorata(self):
        god = SimpleYearlyDeathGod()
        population_size = 10000
        expected_result = 113

        born_number = god.how_much_born(population_size)

        self.assertEqual(born_number, expected_result)

    def test_how_much_die_should_make_a_good_prorata(self):
        god = SimpleYearlyDeathGod()
        population_size = 10000
        expected_result = 91

        born_number = god.how_much_die(population_size)

        self.assertEqual(born_number, expected_result)

    def test_give_birth_should_add_correct_number_of_children(self):
        god = SimpleYearlyDeathGod()
        population = UserGenerator.generate_users(None, 1000)
        expected_result = 1011

        god.give_birth(population)

        self.assertEqual(len(population), expected_result)

    def test_give_death_should_remove_correct_number_of_old(self):
        god = SimpleYearlyDeathGod()
        population = UserGenerator.generate_users(None, 1000)
        expected_result = 991 # 9 less

        god.give_death(population)

        self.assertEqual(len(population), expected_result)

    def test_give_death_should_remove_none_for_small_size(self):
        god = SimpleYearlyDeathGod()
        population = UserGenerator.generate_users(None, 5)

        god.give_death(population)

        self.assertEqual(len(population), 5)


class TestGrapheDrawer(unittest.TestCase):
    def test_add_point_should_save_simulator_infos(self):
        simulator = Simulator()
        drawer = GrapheDrawer(simulator)

        simulator.add_user(User(None, None))
        drawer.add_point()

        self.assertEqual(len(drawer.points), 1)
        self.assertEqual(drawer.points[0]["date"], date.today())
        self.assertEqual(drawer.points[0]["user_count"], 1)
        self.assertEqual(drawer.points[0]["guzis_on_road"], 0)

    def test_add_point_should_save_different_points(self):
        simulator = Simulator(date(2000, 1, 1))
        drawer = GrapheDrawer(simulator)

        simulator.add_users(UserGenerator.generate_users(date(2000, 1, 1), 10))
        drawer.add_point()
        simulator.new_day()
        drawer.add_point()

        self.assertEqual(len(drawer.points), 2)
        self.assertEqual(drawer.points[0]["date"], date(2000, 1, 1))
        self.assertEqual(drawer.points[1]["date"], date(2000, 1, 2))
        self.assertEqual(drawer.points[0]["user_count"], 10)
        self.assertEqual(drawer.points[1]["user_count"], 10)
        self.assertEqual(drawer.points[0]["guzis_on_road"], 0)
        self.assertEqual(drawer.points[1]["guzis_on_road"], 10)

        simulator.new_days(10)
        drawer.add_point()

        self.assertEqual(len(drawer.points), 3)
        self.assertEqual(drawer.points[2]["date"], date(2000, 1, 12))
        self.assertEqual(drawer.points[2]["user_count"], 10)
        self.assertEqual(drawer.points[2]["guzis_on_road"], 110)
