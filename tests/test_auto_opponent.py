"""
Test auto-opponent selection functionality
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from collectors.fixtures_collector import FixturesCollector
from collectors.teams_collector import get_teams_list


def test_fixtures_collector_init():
    """Test that fixtures collector initializes"""
    collector = FixturesCollector(league_id=2013)
    
    assert collector is not None
    assert collector.league_name == "Brasileirão Série A"
    
    print("✅ Fixtures collector initialized")


def test_get_fixtures_by_round():
    """Test fetching fixtures for a round"""
    collector = FixturesCollector(league_id=2013)
    
    fixtures = collector.get_fixtures_by_round(30)
    
    assert fixtures is not None
    assert isinstance(fixtures, list)
    
    if len(fixtures) > 0:
        fixture = fixtures[0]
        assert 'home_team' in fixture
        assert 'away_team' in fixture
        assert 'round' in fixture
        
        print(f"✅ Found {len(fixtures)} fixtures for round 30")
        print(f"   Example: {fixture['home_team']} vs {fixture['away_team']}")
    else:
        print("⚠️ No fixtures found (may be off-season)")


def test_find_opponent():
    """Test finding opponent for a team"""
    collector = FixturesCollector(league_id=2013)
    
    result = collector.find_opponent("Corinthians", 30, is_home=True)
    
    if result:
        assert 'opponent' in result
        assert 'is_home' in result
        assert result['is_home'] == True
        
        print(f"✅ Found opponent: Corinthians vs {result['opponent']}")
    else:
        print("⚠️ No match found (may be off-season or team not playing as home)")


def test_cache_functionality():
    """Test that cache works"""
    collector = FixturesCollector(league_id=2013)
    
    fixtures1 = collector.get_fixtures_by_round(30)
    
    fixtures2 = collector.get_fixtures_by_round(30)
    
    assert fixtures1 == fixtures2
    print("✅ Cache working correctly")


def test_get_teams_list():
    """Test fetching teams list"""
    teams = get_teams_list(league_id=2013)
    
    assert teams is not None
    assert isinstance(teams, list)
    assert len(teams) > 0
    
    print(f"✅ Found {len(teams)} teams")
    print(f"   Example teams: {', '.join(teams[:3])}")


def test_find_opponent_either_venue():
    """Test finding opponent regardless of venue"""
    collector = FixturesCollector(league_id=2013)
    
    result = collector.find_opponent("Palmeiras", 30, is_home=None)
    
    if result:
        assert 'opponent' in result
        assert 'is_home' in result
        
        venue = "home" if result['is_home'] else "away"
        print(f"✅ Found opponent: Palmeiras ({venue}) vs {result['opponent']}")
    else:
        print("⚠️ No match found (may be off-season)")


if __name__ == "__main__":
    print("🔍 Running auto-opponent selection tests...\n")
    
    try:
        test_fixtures_collector_init()
        test_get_fixtures_by_round()
        test_find_opponent()
        test_cache_functionality()
        test_get_teams_list()
        test_find_opponent_either_venue()
        
        print("\n🎉 ALL AUTO-OPPONENT TESTS PASSED!")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
