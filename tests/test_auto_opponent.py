"""
Test auto-opponent selection functionality
Uses mocked API responses to avoid hitting real API
"""
import sys
from pathlib import Path
from unittest.mock import patch, Mock
from datetime import datetime, timedelta

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from collectors.fixtures_collector import FixturesCollector
from collectors.teams_collector import get_teams_list


def test_fixtures_collector_init():
    """Test that fixtures collector initializes correctly"""
    collector = FixturesCollector(league_id=2013)
    
    assert collector is not None, "Collector should be initialized"
    assert collector.league_id == 2013, "League ID should be 2013"
    assert collector.league_name == "Brasileirão Série A", "League name should be set"
    assert collector.base_url == "https://api.football-data.org/v4", "Base URL should be set"
    assert collector._cache == {}, "Cache should be empty on init"
    
    print("✅ Fixtures collector initialization test passed")


def test_get_fixtures_by_round():
    """Test fetching fixtures for round 30 with mocked API response"""
    collector = FixturesCollector(league_id=2013)
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'matches': [
            {
                'homeTeam': {'name': 'SC Corinthians Paulista', 'id': 1234},
                'awayTeam': {'name': 'SE Palmeiras', 'id': 5678},
                'utcDate': '2025-10-20T19:00:00Z',
                'status': 'SCHEDULED'
            },
            {
                'homeTeam': {'name': 'CR Flamengo', 'id': 9012},
                'awayTeam': {'name': 'Fluminense FC', 'id': 3456},
                'utcDate': '2025-10-20T21:00:00Z',
                'status': 'SCHEDULED'
            }
        ]
    }
    
    with patch('requests.get', return_value=mock_response):
        fixtures = collector.get_fixtures_by_round(30)
    
    assert fixtures is not None, "Fixtures should not be None"
    assert isinstance(fixtures, list), "Should return a list"
    assert len(fixtures) == 2, f"Should return 2 fixtures, got {len(fixtures)}"
    assert fixtures[0]['home_team'] == 'SC Corinthians Paulista', "First fixture home team should be Corinthians"
    assert fixtures[0]['away_team'] == 'SE Palmeiras', "First fixture away team should be Palmeiras"
    assert fixtures[0]['round'] == 30, "Round should be 30"
    
    print(f"✅ Get fixtures by round test passed")
    print(f"   Found {len(fixtures)} fixtures for round 30")
    print(f"   Example: {fixtures[0]['home_team']} vs {fixtures[0]['away_team']}")


def test_find_opponent():
    """Test finding opponent for Corinthians in round 30"""
    collector = FixturesCollector(league_id=2013)
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'matches': [
            {
                'homeTeam': {'name': 'SC Corinthians Paulista', 'id': 1234},
                'awayTeam': {'name': 'SE Palmeiras', 'id': 5678},
                'utcDate': '2025-10-20T19:00:00Z',
                'status': 'SCHEDULED'
            },
            {
                'homeTeam': {'name': 'CR Flamengo', 'id': 9012},
                'awayTeam': {'name': 'Fluminense FC', 'id': 3456},
                'utcDate': '2025-10-20T21:00:00Z',
                'status': 'SCHEDULED'
            }
        ]
    }
    
    with patch('requests.get', return_value=mock_response):
        result = collector.find_opponent("Corinthians", 30, is_home=True)
    
    assert result is not None, "Should find opponent"
    assert 'opponent' in result, "Result should have opponent key"
    assert 'is_home' in result, "Result should have is_home key"
    assert result['is_home'] == True, "Corinthians should be home"
    assert result['opponent'] == 'SE Palmeiras', f"Opponent should be Palmeiras, got {result['opponent']}"
    assert 'fixture' in result, "Should include fixture data"
    
    print(f"✅ Find opponent test passed")
    print(f"   Corinthians vs {result['opponent']} (Corinthians is home)")


def test_cache_functionality():
    """Test that second call uses cache instead of API"""
    collector = FixturesCollector(league_id=2013)
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'matches': [
            {
                'homeTeam': {'name': 'SC Corinthians Paulista', 'id': 1234},
                'awayTeam': {'name': 'SE Palmeiras', 'id': 5678},
                'utcDate': '2025-10-20T19:00:00Z',
                'status': 'SCHEDULED'
            }
        ]
    }
    
    with patch('requests.get', return_value=mock_response) as mock_get:
        fixtures1 = collector.get_fixtures_by_round(30)
        assert mock_get.call_count == 1, "First call should hit API"
        
        fixtures2 = collector.get_fixtures_by_round(30)
        assert mock_get.call_count == 1, "Second call should NOT hit API (use cache)"
        
        assert fixtures1 == fixtures2, "Cached result should match original"
        assert len(fixtures2) == 1, "Should return cached fixture"
    
    print("✅ Cache functionality test passed")
    print(f"   First call: API hit, Second call: Cache used")


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
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'matches': [
            {
                'homeTeam': {'name': 'SC Corinthians Paulista', 'id': 1234},
                'awayTeam': {'name': 'SE Palmeiras', 'id': 5678},
                'utcDate': '2025-10-20T19:00:00Z',
                'status': 'SCHEDULED'
            }
        ]
    }
    
    with patch('requests.get', return_value=mock_response):
        result = collector.find_opponent("Palmeiras", 30, is_home=None)
    
    assert result is not None, "Should find opponent"
    assert 'opponent' in result, "Result should have opponent key"
    assert 'is_home' in result, "Result should have is_home key"
    
    venue = "home" if result['is_home'] else "away"
    print(f"✅ Find opponent (either venue) test passed")
    print(f"   Palmeiras ({venue}) vs {result['opponent']}")


def test_api_error_handling():
    """Test that API errors are handled gracefully"""
    collector = FixturesCollector(league_id=2013)
    
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = Exception("API Error")
    
    with patch('requests.get', return_value=mock_response):
        fixtures = collector.get_fixtures_by_round(30)
    
    assert isinstance(fixtures, list), "Should return a list even on error"
    assert len(fixtures) == 0, "Should return empty list on error"
    
    print("✅ API error handling test passed")
    print(f"   Returns empty list on API error (season ended scenario)")


if __name__ == "__main__":
    print("🔍 Running auto-opponent selection tests...\n")
    
    try:
        test_fixtures_collector_init()
        print()
        
        test_get_fixtures_by_round()
        print()
        
        test_find_opponent()
        print()
        
        test_cache_functionality()
        print()
        
        test_get_teams_list()
        print()
        
        test_find_opponent_either_venue()
        print()
        
        test_api_error_handling()
        print()
        
        print("🎉 ALL AUTO-OPPONENT TESTS PASSED!")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
