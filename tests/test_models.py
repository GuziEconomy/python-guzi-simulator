import unittest
from unittest.mock import MagicMock
from datetime import date
from guzi.models import GuziCreator

from simulator.models import Simulator, UserGenerator, SimpleYearlyDeathGod, GrapheDrawer, SimpleUser, RandomTrader


class TestSimpkeUser(unittest.TestCase):
    def test_daily_guzis(self):
        user = SimpleUser("", None)
        user.total_accumulated = 27

        expected = 4
        result = user.daily_guzis()

        self.assertEqual(result, expected)

    def test_outdate(self):
        user = SimpleUser("", None)
        user.guzi_wallet = 1

        user.outdate([GuziCreator.create_guzi(user, date(2000, 1, 1), 1)])

        self.assertEqual(user.guzi_wallet, 0)

    def test_pay(self):
        user = SimpleUser("", None)

        user.pay(["1", "2", "3"])

        self.assertEqual(user.balance["income"], 3)

    def test_spend_to_should_raise_error_if_amount_is_negative(self):
        user = SimpleUser("", None)

        with self.assertRaises(ValueError):
            user.spend_to(None, -10)

    def test_spend_to_should_raise_error_if_user_cant_afford_it(self):
        user = SimpleUser("", None)

        with self.assertRaises(ValueError):
            user.spend_to(None, 1)

    def test_spend_to_should_increase_total_accumulated_directly_if_target_is_self(self):
        user = SimpleUser("", None)
        user.guzi_wallet = 10

        user.spend_to(user, 10)

        self.assertEqual(user.guzi_wallet, 0)
        self.assertEqual(user.total_accumulated, 10)

    def test_spend_to_should_pay_target(self):
        source = SimpleUser("", None)
        source.guzi_wallet = 10
        target = SimpleUser("", None)
        target.pay = MagicMock()

        source.spend_to(target, 10)

        target.pay.assert_called_with([GuziCreator.create_guzi(source, date(2000, 1, 1), i) for i in range(10)])
        self.assertEqual(source.guzi_wallet, 0)

    def test_check_balance(self):
        user = SimpleUser("", None)
        user.balance["income"] = 10
        user.balance["outcome"] = 5

        user.check_balance()

        self.assertEqual(user.balance["income"], 5)
        self.assertEqual(user.total_accumulated, 5)

    def test_check_outdated_guzis(self):
        user = SimpleUser("", None)
        max_guzis = user.daily_guzis() * 30
        user.guzi_wallet = max_guzis + 5
        user.guza_wallet = max_guzis + 5

        user.check_outdated_guzis(None)

        self.assertEqual(user.guzi_wallet, max_guzis)
        self.assertEqual(user.guza_wallet, max_guzis)
        self.assertEqual(user.total_accumulated, 5)
        self.assertEqual(user.guza_trashbin, 5)

    def test_create_daily_guzis(self):
        user = SimpleUser("", None)
        user.total_accumulated = 27
        expected = 4

        user.create_daily_guzis(None)

        self.assertEqual(user.guzi_wallet, expected)
        self.assertEqual(user.guza_wallet, expected)


class TestUserGenerator(unittest.TestCase):
    """
    """
    def test_generate_user(self):
        user = UserGenerator.generate_user(date(2000, 1, 1))

        self.assertIsInstance(user, SimpleUser)
        self.assertEqual(user.birthdate, date(2000, 1, 1))

    def test_generate_users(self):
        users = UserGenerator.generate_users(date(2000, 1, 1), 10)

        self.assertEqual(len(users), 10)

    def test_generate_random_user(self):
        user = UserGenerator.generate_random_user()

        self.assertIsInstance(user, SimpleUser)

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
            self.assertEqual(simulator.user_pool[i].guzi_wallet, 0)
            self.assertEqual(simulator.user_pool[i].guza_wallet, 0)

        simulator.new_day()

        for i in range(10):
            self.assertEqual(simulator.user_pool[i].guzi_wallet, 1)
            self.assertEqual(simulator.user_pool[i].guza_wallet, 1)

    def test_new_day_must_check_balance_of_all_users(self):
        """
        a new_day should set the balance of each user back to 0 and add the
        bonuses to the users total_accumulated (which goes from 0 to 1)
        """
        simulator = Simulator(date(2000, 1, 1))

        for i in range(10):
            user = UserGenerator.generate_random_adult_user()
            user.balance["income"] += 1
            simulator.add_user(user)

        for i in range(10):
            self.assertEqual(simulator.user_pool[i].total_accumulated, 0)

        simulator.new_day()

        for i in range(10):
            self.assertEqual(simulator.user_pool[i].total_accumulated, 1)

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
            self.assertEqual(simulator.user_pool[i].total_accumulated, 0)

        simulator.new_days(31)

        for i in range(10):
            self.assertEqual(simulator.user_pool[i].total_accumulated, 1)

    def test_new_day_must_create_daily_guzas_in_users_wallets(self):
        """
        new_day should add the daily Guzas of all users. Here 1 each as the
        total_accumulated is always 0.
        """
        simulator = Simulator(date(2000, 1, 1))

        for i in range(10):
            simulator.add_user(UserGenerator.generate_random_adult_user())

        for i in range(10):
            self.assertEqual(simulator.user_pool[i].guza_wallet, 0)
            self.assertEqual(simulator.user_pool[i].guza_wallet, 0)

        simulator.new_day()

        for i in range(10):
            self.assertEqual(simulator.user_pool[i].guza_wallet, 1)
            self.assertEqual(simulator.user_pool[i].guza_wallet, 1)

    def test_new_day_must_check_outdated_guzas_of_all_users(self):
        """
        new_day should move Guzas in guza_wallet older than 30 days to the
        guza_trashbin of it's owner
        """
        simulator = Simulator(date(2000, 1, 1))

        for i in range(1):
            simulator.add_user(UserGenerator.generate_random_adult_user())

        for i in range(1):
            self.assertEqual(simulator.user_pool[i].guza_wallet, 0)

        simulator.new_days(31)

        for i in range(1):
            # 31 because at 30, a Guzi was outdated and increased the daily earn
            # to 2/day
            self.assertEqual(simulator.user_pool[i].guza_wallet, 31)

    def test_new_day_multiple_times(self):
        simulator = Simulator(date(2000, 1, 1))

        for i in range(10):
            simulator.add_user(UserGenerator.generate_random_adult_user())

        for i in range(10):
            self.assertEqual(simulator.user_pool[i].guzi_wallet, 0)
            self.assertEqual(simulator.user_pool[i].guza_wallet, 0)

        simulator.new_day()
        simulator.new_day()
        simulator.new_day()

        self.assertEqual(simulator.current_date, date(2000, 1, 4))
        for i in range(10):
            self.assertEqual(simulator.user_pool[i].guzi_wallet, 3)
            self.assertEqual(simulator.user_pool[i].guza_wallet, 3)

    def test_new_days(self):
        """
        Running new_days(15) should increase guzi_wallet & guza_wallet of 
        15*1 (as total_accumulated = 0) = 15
        """
        simulator = Simulator(date(2000, 1, 1))

        for i in range(10):
            simulator.add_user(UserGenerator.generate_random_adult_user())

        for i in range(10):
            self.assertEqual(simulator.user_pool[i].guzi_wallet, 0)
            self.assertEqual(simulator.user_pool[i].guza_wallet, 0)

        simulator.new_days(15)

        self.assertEqual(simulator.current_date, date(2000, 1, 16))
        for i in range(10):
            self.assertEqual(simulator.user_pool[i].guzi_wallet, 15)
            self.assertEqual(simulator.user_pool[i].guza_wallet, 15)


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

        population = god.give_birth(population)

        self.assertEqual(len(population), expected_result)

    def test_give_death_should_remove_correct_number_of_old(self):
        god = SimpleYearlyDeathGod()
        population = UserGenerator.generate_users(None, 1000)
        expected_result = 991 # 9 less

        population = god.give_death(population)

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

        simulator.add_user(SimpleUser(None, None))
        drawer.add_point()

        self.assertEqual(len(drawer.points["date"]), 1)
        self.assertEqual(drawer.points["date"][0], date.today())
        self.assertEqual(drawer.points["user_count"][0], 1)
        self.assertEqual(drawer.points["guzis_on_road"][0], 0)

    def test_add_point_should_save_different_points(self):
        simulator = Simulator(date(2000, 1, 1))
        drawer = GrapheDrawer(simulator)

        simulator.add_users(UserGenerator.generate_users(date(2000, 1, 1), 10))
        drawer.add_point()
        simulator.new_day()
        drawer.add_point()

        self.assertEqual(len(drawer.points["date"]), 2)
        self.assertEqual(drawer.points["date"][0], date(2000, 1, 1))
        self.assertEqual(drawer.points["date"][1], date(2000, 1, 2))
        self.assertEqual(drawer.points["user_count"][0], 10)
        self.assertEqual(drawer.points["user_count"][1], 10)
        self.assertEqual(drawer.points["guzis_on_road"][0], 0)
        self.assertEqual(drawer.points["guzis_on_road"][1], 10)

        simulator.new_days(10)
        drawer.add_point()

        self.assertEqual(len(drawer.points["date"]), 3)
        self.assertEqual(drawer.points["date"][2], date(2000, 1, 12))
        self.assertEqual(drawer.points["user_count"][2], 10)
        self.assertEqual(drawer.points["guzis_on_road"][2], 110)

    def test_add_graph_should_raise_error_on_different_x(self):
        drawer = GrapheDrawer(None)

        drawer.add_graph("date", "average_daily_guzi")
        with self.assertRaises(ValueError):
            drawer.add_graph("user_count", "guzis_on_road")

    def test_add_graph_shouldnd_duplicate_if_same_y_added_twice(self):
        drawer = GrapheDrawer(None)

        drawer.add_graph("date", "average_daily_guzi")
        drawer.add_graph("date", "average_daily_guzi")
        
        self.assertEqual(len(drawer.to_draw["y"]), 1)

    def test_draw_should_raise_error_if_no_x_set(self):
        drawer = GrapheDrawer(None)

        with self.assertRaises(ValueError):
            drawer.draw()

    def test_draw_should_raise_error_if_no_y_set(self):
        drawer = GrapheDrawer(None)

        drawer.to_draw = {"x": "ok", "y": []}

        with self.assertRaises(ValueError):
            drawer.draw()


class TestRandomTrader(unittest.TestCase):
    def test_init_should_set_the_user_pool(self):
        user_pool = ["a", "b"]
        trader = RandomTrader(user_pool)

        self.assertEqual(trader.user_pool, user_pool)

    def test_trade_guzis_with_count_should_reduce_N_guzi_wallet(self):
        user_pool = UserGenerator.generate_users(date(2000, 1, 1), 10)
        trader = RandomTrader(user_pool)
        for u in user_pool:
            for i in range(1, 10):
                u.create_daily_guzis(date(2000, 1, i))

        trader.trade_guzis(5)

        user_who_spended = 0
        for u in user_pool:
            if u.guzi_wallet < 10:
                user_who_spended += 1

        self.assertEqual(user_who_spended, 5)
