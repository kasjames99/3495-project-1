#!/usr/bin/env python3
import requests
import time
import threading
import argparse
import random
from concurrent.futures import ThreadPoolExecutor
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LoadTester:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.auth_token = None
        
    def login(self):
        """Authenticate and get a token"""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json={"username": self.username, "password": self.password},
                timeout=5
            )
            response.raise_for_status()
            self.auth_token = response.json().get("token")
            return True
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False
    
    def submit_data(self):
        """Submit random data to the data entry service"""
        if not self.auth_token:
            if not self.login():
                return False
        
        try:
            # Generate random data
            data = {
                "value": random.uniform(0, 100)
            }
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = self.session.post(
                f"{self.base_url}/data/data_entry",
                data=data,
                headers=headers,
                timeout=5
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Data submission failed: {e}")
            return False
    
    def view_results(self):
        """Fetch results from the results service"""
        if not self.auth_token:
            if not self.login():
                return False
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = self.session.get(
                f"{self.base_url}/results/results",
                headers=headers,
                timeout=5
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Results fetch failed: {e}")
            return False

def worker(tester, action, iteration):
    """Worker function for the thread pool"""
    if action == "data":
        result = tester.submit_data()
    else:  # action == "results"
        result = tester.view_results()
    
    return result

def run_load_test(base_url, users, duration, ramp_up):
    """Run the load test with specified parameters"""
    logger.info(f"Starting load test with {users} users for {duration} seconds")
    
    # Create user sessions
    testers = []
    for i in range(users):
        # In a real scenario, you might want to use different credentials
        tester = LoadTester(base_url, f"user{i}", "password")
        testers.append(tester)
    
    # Track metrics
    successful_requests = 0
    failed_requests = 0
    start_time = time.time()
    
    # Gradually add load if ramp_up is enabled
    active_users = 1 if ramp_up else users
    
    with ThreadPoolExecutor(max_workers=users) as executor:
        while time.time() - start_time < duration:
            # Increase users if ramping up
            if ramp_up:
                elapsed = time.time() - start_time
                active_users = min(users, int((elapsed / ramp_up) * users) + 1)
            
            # Submit tasks to thread pool
            futures = []
            for i in range(active_users):
                # Randomly choose between data submission and results viewing
                action = random.choice(["data", "results"])
                future = executor.submit(worker, testers[i], action, i)
                futures.append(future)
            
            # Process results
            for future in futures:
                result = future.result()
                if result:
                    successful_requests += 1
                else:
                    failed_requests += 1
            
            # Short delay to avoid overwhelming system
            time.sleep(0.1)
    
    # Print results
    total_time = time.time() - start_time
    logger.info("\nLoad Test Results:")
    logger.info(f"Total time: {total_time:.2f} seconds")
    logger.info(f"Successful requests: {successful_requests}")
    logger.info(f"Failed requests: {failed_requests}")
    logger.info(f"Requests per second: {successful_requests / total_time:.2f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load test for microservices application")
    parser.add_argument("--url", default="http://localhost", help="Base URL of the application")
    parser.add_argument("--users", type=int, default=10, help="Number of concurrent users")
    parser.add_argument("--duration", type=int, default=60, help="Test duration in seconds")
    parser.add_argument("--ramp-up", type=int, default=30, help="Ramp-up period in seconds (0 for no ramp-up)")
    
    args = parser.parse_args()
    run_load_test(args.url, args.users, args.duration, args.ramp_up)