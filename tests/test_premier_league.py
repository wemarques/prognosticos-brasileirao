"""
Test suite for Premier League configuration
"""
import unittest
from leagues.premier_league import PremierLeague
from leagues.base_league import BaseLeague
from models.dixon_coles import DixonColesModel


class TestPremierLeagueImport(unittest.TestCase):
    """Test Premier League import functionality"""
    
    def test_premier_league_import(self):
        """Test that PremierLeague can be imported and instantiated"""
        pl = PremierLeague()
        self.assertIsNotNone(pl)
        self.assertIsInstance(pl, BaseLeague)
        print("✅ PremierLeague import OK")


class TestPremierLeagueParams(unittest.TestCase):
    """Test Premier League Dixon-Coles parameters"""
    
    def test_premier_league_params(self):
        """Test Premier League has correct Dixon-Coles parameters"""
        pl = PremierLeague()
        params = pl.get_dixon_coles_params()
        
        self.assertEqual(params['hfa'], 1.40)
        self.assertEqual(params['ava'], 0.88)
        self.assertEqual(params['league_avg_goals'], 2.82)
        self.assertEqual(params['rho'], -0.15)
        
        self.assertIn('hfa', params)
        self.assertIn('ava', params)
        self.assertIn('league_avg_goals', params)
        self.assertIn('rho', params)
        
        print("✅ PL params OK")
    
    def test_premier_league_name(self):
        """Test Premier League name is correct"""
        pl = PremierLeague()
        self.assertEqual(pl.get_league_name(), "Premier League")
        print("✅ PL name OK")
    
    def test_premier_league_country(self):
        """Test Premier League country code is correct"""
        pl = PremierLeague()
        self.assertEqual(pl.get_country(), "ENG")
        print("✅ PL country OK")
    
    def test_premier_league_teams_rounds(self):
        """Test Premier League teams and rounds"""
        pl = PremierLeague()
        self.assertEqual(pl.get_num_teams(), 20)
        self.assertEqual(pl.get_num_rounds(), 38)
        print("✅ PL teams/rounds OK")


class TestPremierLeagueStats(unittest.TestCase):
    """Test Premier League fallback statistics"""
    
    def test_premier_league_stats(self):
        """Test Premier League has complete fallback stats"""
        pl = PremierLeague()
        stats = pl.get_fallback_stats()
        
        self.assertIn('corners', stats)
        self.assertIn('cards', stats)
        
        corners = stats['corners']
        self.assertEqual(corners['home_avg'], 5.8)
        self.assertEqual(corners['away_avg'], 4.9)
        self.assertEqual(corners['std_dev'], 2.3)
        self.assertEqual(corners['over_8_5_prob'], 0.70)
        self.assertEqual(corners['over_9_5_prob'], 0.63)
        self.assertEqual(corners['over_10_5_prob'], 0.55)
        self.assertEqual(corners['over_11_5_prob'], 0.47)
        
        cards = stats['cards']
        self.assertEqual(cards['home_avg'], 2.1)
        self.assertEqual(cards['away_avg'], 2.3)
        self.assertEqual(cards['std_dev'], 1.2)
        self.assertEqual(cards['over_3_5_prob'], 0.58)
        self.assertEqual(cards['over_4_5_prob'], 0.45)
        self.assertEqual(cards['over_5_5_prob'], 0.32)
        self.assertEqual(cards['over_6_5_prob'], 0.20)
        
        print("✅ PL fallback stats OK")


class TestPremierLeagueAPIIds(unittest.TestCase):
    """Test Premier League API IDs"""
    
    def test_premier_league_api_ids(self):
        """Test Premier League has correct API IDs for each provider"""
        pl = PremierLeague()
        
        self.assertEqual(pl.get_api_league_id('football-data'), 'PL')
        self.assertEqual(pl.get_api_league_id('footystats'), '2')
        self.assertEqual(pl.get_api_league_id('odds-api'), 'soccer_epl')
        
        self.assertEqual(pl.get_api_league_id('unknown_provider'), '')
        
        print("✅ PL API IDs OK")


class TestDixonColesWithPremier(unittest.TestCase):
    """Test Dixon-Coles model works with Premier League"""
    
    def test_dixon_coles_with_premier(self):
        """Test Dixon-Coles model can be initialized with Premier League"""
        model = DixonColesModel('premier_league')
        
        self.assertIsNotNone(model)
        self.assertEqual(model.league.name, "Premier League")
        self.assertEqual(model.hfa, 1.40)
        self.assertEqual(model.league_avg_goals, 2.82)
        self.assertEqual(model.ava, 0.88)
        self.assertEqual(model.rho, -0.15)
        
        print("✅ Dixon-Coles with PL OK")
    
    def test_premier_league_params_different_from_brasileirao(self):
        """Test Premier League parameters are different from Brasileirão"""
        pl_model = DixonColesModel('premier_league')
        br_model = DixonColesModel('brasileirao')
        
        self.assertNotEqual(pl_model.hfa, br_model.hfa)
        self.assertNotEqual(pl_model.league_avg_goals, br_model.league_avg_goals)
        
        self.assertGreater(pl_model.hfa, br_model.hfa)
        self.assertGreater(pl_model.league_avg_goals, br_model.league_avg_goals)
        
        print("✅ PL params different from BR OK")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("TESTING PREMIER LEAGUE CONFIGURATION")
    print("="*60 + "\n")
    
    unittest.main(verbosity=2)
