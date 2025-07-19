#!/usr/bin/env python3
"""
Bridge Platform Database Seeding Script
Creates sample data for local development and testing
"""

import sys
import os
from datetime import date, datetime, timedelta
from decimal import Decimal
import random

# Add the API app to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'apps', 'api'))

try:
    from sqlalchemy.orm import Session
    from app.db.base import engine
    from app.models.organization import Organization
    from app.models.player import Player
    from app.models.event import Event, Session as EventSession
    from app.models.result import Result, Rating, Masterpoint
    from app.models.bridge import Subscription
except ImportError as e:
    print(f"❌ Failed to import required modules: {e}")
    print("Make sure you're running this from the project root and dependencies are installed")
    sys.exit(1)

def seed_database():
    """Seed the database with sample bridge tournament data"""
    print("🌱 Starting database seeding...")
    
    # Create database session
    session = Session(bind=engine)
    
    try:
        # Check if data already exists
        existing_players = session.query(Player).count()
        if existing_players > 4:  # More than the default sample players
            print("📊 Database already contains data. Skipping seeding.")
            print(f"   Found {existing_players} players")
            return
        
        print("👥 Creating sample players...")
        
        # Sample player data based on real bridge player patterns
        sample_players = [
            {"number": 1005, "firstname": "Margaret", "lastname": "Chen", "email": "margaret.chen@email.com", "gender": "F"},
            {"number": 1006, "firstname": "David", "lastname": "Kumar", "email": "david.kumar@email.com", "gender": "M"},
            {"number": 1007, "firstname": "Sarah", "lastname": "Williams", "email": "sarah.williams@email.com", "gender": "F"},
            {"number": 1008, "firstname": "Michael", "lastname": "Zhang", "email": "michael.zhang@email.com", "gender": "M"},
            {"number": 1009, "firstname": "Linda", "lastname": "Taylor", "email": "linda.taylor@email.com", "gender": "F"},
            {"number": 1010, "firstname": "Robert", "lastname": "Lee", "email": "robert.lee@email.com", "gender": "M"},
            {"number": 1011, "firstname": "Jennifer", "lastname": "Wong", "email": "jennifer.wong@email.com", "gender": "F"},
            {"number": 1012, "firstname": "James", "lastname": "Thompson", "email": "james.thompson@email.com", "gender": "M"},
            {"number": 1013, "firstname": "Helen", "lastname": "Lim", "email": "helen.lim@email.com", "gender": "F"},
            {"number": 1014, "firstname": "Peter", "lastname": "Johnson", "email": "peter.johnson@email.com", "gender": "M"},
            {"number": 1015, "firstname": "Mary", "lastname": "Garcia", "email": "mary.garcia@email.com", "gender": "F"},
            {"number": 1016, "firstname": "Andrew", "lastname": "Wilson", "email": "andrew.wilson@email.com", "gender": "M"},
        ]
        
        players = []
        for player_data in sample_players:
            player = Player(
                **player_data,
                organization_id=1,
                status="active",
                joindate=date.today() - timedelta(days=random.randint(30, 1000)),
                mobile=f"+65 9{random.randint(100, 999)} {random.randint(1000, 9999)}",
                address=f"{random.randint(1, 999)} Bridge Street, Singapore {random.randint(100000, 999999)}"
            )
            session.add(player)
            players.append(player)
        
        session.commit()
        print(f"✅ Created {len(players)} sample players")
        
        print("🏆 Creating sample events...")
        
        # Sample events with different types
        sample_events = [
            {
                "name": "Weekly Duplicate - Monday Night",
                "type": "pairs",
                "start_date": date.today() - timedelta(days=7),
                "status": "completed"
            },
            {
                "name": "Club Championship 2024",
                "type": "pairs", 
                "start_date": date.today() - timedelta(days=14),
                "status": "completed"
            },
            {
                "name": "Novice Pairs Tournament",
                "type": "pairs",
                "start_date": date.today() - timedelta(days=3),
                "status": "completed"
            },
            {
                "name": "Teams of Four Championship",
                "type": "teams",
                "start_date": date.today() + timedelta(days=7),
                "status": "planned"
            },
            {
                "name": "Swiss Pairs - Weekend",
                "type": "swiss",
                "start_date": date.today() + timedelta(days=14),
                "status": "planned"
            }
        ]
        
        events = []
        for event_data in sample_events:
            event = Event(
                **event_data,
                organization_id=1,
                code=f"E{random.randint(100, 999)}",
                settings={"boards": 24, "movement": "mitchell"}
            )
            session.add(event)
            events.append(event)
        
        session.commit()
        print(f"✅ Created {len(events)} sample events")
        
        print("📊 Creating sample results...")
        
        # Create results for completed events
        completed_events = [e for e in events if e.status == "completed"]
        
        for event in completed_events:
            # Create a session for the event
            event_session = EventSession(
                event_id=event.id,
                session_number=1,
                date=event.start_date,
                status="completed",
                boards_played=24
            )
            session.add(event_session)
            session.commit()
            
            # Create results for random pairs
            num_pairs = random.randint(8, 12)
            available_players = players.copy()
            random.shuffle(available_players)
            
            for position in range(1, num_pairs + 1):
                if len(available_players) < 2:
                    break
                    
                player1 = available_players.pop()
                player2 = available_players.pop()
                
                # Generate realistic bridge scores
                base_percentage = random.uniform(30, 70)
                percentage = round(base_percentage + random.uniform(-5, 5), 2)
                score = round(percentage * 2.4, 2)  # Convert to matchpoints
                
                result = Result(
                    event_id=event.id,
                    session_id=event_session.id,
                    player_id=player1.id,
                    partner_id=player2.id,
                    pair_number=position,
                    position=position,
                    score=Decimal(str(score)),
                    percentage=Decimal(str(percentage)),
                    masterpoints_awarded=Decimal(str(random.uniform(0.5, 3.0)))
                )
                session.add(result)
                
                # Create masterpoint records
                for player in [player1, player2]:
                    masterpoint = Masterpoint(
                        player_id=player.id,
                        event_id=event.id,
                        organization_id=1,
                        award_type="local",
                        points=result.masterpoints_awarded,
                        awarded_date=event.start_date
                    )
                    session.add(masterpoint)
        
        session.commit()
        print("✅ Created sample results and masterpoints")
        
        print("🎯 Creating sample ratings...")
        
        # Create OpenSkill ratings for all players
        for player in players:
            # Initial rating
            mu = random.uniform(20, 30)  # OpenSkill mu parameter
            sigma = random.uniform(2, 4)  # OpenSkill sigma parameter
            
            rating = Rating(
                player_id=player.id,
                rating_type="openskill",
                date=datetime.now().date(),
                mu=Decimal(str(mu)),
                sigma=Decimal(str(sigma)),
                confidence_interval=Decimal(str(mu - 2 * sigma))
            )
            session.add(rating)
        
        session.commit()
        print("✅ Created sample ratings")
        
        print("💳 Creating sample subscriptions...")
        
        # Create subscriptions for players
        for player in players[:8]:  # Some players have subscriptions
            subscription = Subscription(
                player_id=player.id,
                type=random.choice(["full", "social", "student"]),
                expiry=datetime.now() + timedelta(days=random.randint(30, 365)),
                fee=random.choice([50, 75, 100, 150]),
                payment_date=datetime.now() - timedelta(days=random.randint(1, 30))
            )
            session.add(subscription)
        
        session.commit()
        print("✅ Created sample subscriptions")
        
        # Print summary
        print("\n📈 Database seeding completed!")
        print("📊 Summary:")
        print(f"   Players: {session.query(Player).count()}")
        print(f"   Events: {session.query(Event).count()}")
        print(f"   Results: {session.query(Result).count()}")
        print(f"   Ratings: {session.query(Rating).count()}")
        print(f"   Masterpoints: {session.query(Masterpoint).count()}")
        print(f"   Subscriptions: {session.query(Subscription).count()}")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    seed_database()