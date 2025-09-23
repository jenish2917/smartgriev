#!/usr/bin/env python3
"""
SmartGriev System Health Monitor
===============================

Advanced monitoring system that tracks:
- API performance metrics
- Database health
- Server resources
- User activity
- Error rates
- System alerts
"""

import asyncio
import aiohttp
import psutil
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import sqlite3
import os
from pathlib import Path

class SystemHealthMonitor:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_url = "http://127.0.0.1:8000"
        self.frontend_url = "http://localhost:3000"
        self.db_path = self.project_root / "backend" / "db.sqlite3"
        
        # Health thresholds
        self.thresholds = {
            'cpu_usage': 80,
            'memory_usage': 85,
            'disk_usage': 90,
            'api_response_time': 1000,  # ms
            'error_rate': 5,  # percentage
            'concurrent_users': 1000,
        }
        
        # Metrics storage
        self.metrics = {
            'timestamp': [],
            'cpu_usage': [],
            'memory_usage': [],
            'disk_usage': [],
            'api_response_times': [],
            'error_counts': [],
            'active_users': [],
            'complaint_submissions': [],
        }
    
    async def check_api_health(self) -> Dict[str, Any]:
        """Check API endpoint health and response times"""
        endpoints = [
            '/api/complaints/api/health/',
            '/api/complaints/departments/',
            '/api/complaints/',
            '/api/auth/verify-token/',
        ]
        
        results = {}
        
        async with aiohttp.ClientSession() as session:
            for endpoint in endpoints:
                try:
                    start_time = time.time()
                    async with session.get(f"{self.backend_url}{endpoint}", timeout=5) as response:
                        response_time = (time.time() - start_time) * 1000
                        
                        results[endpoint] = {
                            'status': response.status,
                            'response_time_ms': round(response_time, 2),
                            'healthy': response.status == 200 and response_time < self.thresholds['api_response_time']
                        }
                except Exception as e:
                    results[endpoint] = {
                        'status': 'error',
                        'response_time_ms': None,
                        'healthy': False,
                        'error': str(e)
                    }
        
        return results
    
    async def check_frontend_health(self) -> Dict[str, Any]:
        """Check frontend application health"""
        try:
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.get(self.frontend_url, timeout=5) as response:
                    response_time = (time.time() - start_time) * 1000
                    content = await response.text()
                    
                    return {
                        'status': response.status,
                        'response_time_ms': round(response_time, 2),
                        'healthy': response.status == 200 and 'id="root"' in content,
                        'react_detected': 'id="root"' in content,
                        'size_kb': len(content.encode('utf-8')) / 1024
                    }
        except Exception as e:
            return {
                'status': 'error',
                'response_time_ms': None,
                'healthy': False,
                'error': str(e)
            }
    
    def check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage"""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        
        # Network I/O
        network = psutil.net_io_counters()
        
        return {
            'cpu': {
                'usage_percent': cpu_percent,
                'cores': psutil.cpu_count(),
                'healthy': cpu_percent < self.thresholds['cpu_usage']
            },
            'memory': {
                'usage_percent': memory_percent,
                'total_gb': round(memory.total / (1024**3), 2),
                'available_gb': round(memory.available / (1024**3), 2),
                'healthy': memory_percent < self.thresholds['memory_usage']
            },
            'disk': {
                'usage_percent': disk_percent,
                'total_gb': round(disk.total / (1024**3), 2),
                'free_gb': round(disk.free / (1024**3), 2),
                'healthy': disk_percent < self.thresholds['disk_usage']
            },
            'network': {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            }
        }
    
    def check_database_health(self) -> Dict[str, Any]:
        """Check database health and statistics"""
        if not os.path.exists(self.db_path):
            return {
                'healthy': False,
                'error': 'Database file not found'
            }
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check database size
            db_size = os.path.getsize(self.db_path) / (1024 * 1024)  # MB
            
            # Count records in main tables
            tables_info = {}
            main_tables = [
                'complaints_complaint',
                'complaints_department',
                'auth_user',
                'authentication_otpverification'
            ]
            
            for table in main_tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    tables_info[table] = count
                except sqlite3.OperationalError:
                    tables_info[table] = 'table_not_found'
            
            # Recent activity (complaints in last 24 hours)
            cursor.execute("""
                SELECT COUNT(*) FROM complaints_complaint 
                WHERE created_at > datetime('now', '-1 day')
            """)
            recent_complaints = cursor.fetchone()[0] if cursor.fetchone() else 0
            
            conn.close()
            
            return {
                'healthy': True,
                'size_mb': round(db_size, 2),
                'tables': tables_info,
                'recent_activity': {
                    'complaints_24h': recent_complaints
                }
            }
            
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e)
            }
    
    def calculate_system_score(self, health_data: Dict[str, Any]) -> int:
        """Calculate overall system health score (0-100)"""
        score = 100
        
        # API health (30% weight)
        api_healthy = sum(1 for endpoint in health_data['api'].values() if endpoint.get('healthy', False))
        api_total = len(health_data['api'])
        api_score = (api_healthy / api_total) * 30 if api_total > 0 else 0
        
        # Frontend health (20% weight)
        frontend_score = 20 if health_data['frontend'].get('healthy', False) else 0
        
        # System resources (30% weight)
        resources = health_data['system_resources']
        resource_score = 0
        if resources['cpu']['healthy']: resource_score += 10
        if resources['memory']['healthy']: resource_score += 10
        if resources['disk']['healthy']: resource_score += 10
        
        # Database health (20% weight)
        db_score = 20 if health_data['database'].get('healthy', False) else 0
        
        total_score = api_score + frontend_score + resource_score + db_score
        return int(total_score)
    
    def generate_alerts(self, health_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate system alerts based on health data"""
        alerts = []
        
        # API alerts
        for endpoint, data in health_data['api'].items():
            if not data.get('healthy', False):
                alerts.append({
                    'type': 'error',
                    'category': 'api',
                    'message': f"API endpoint {endpoint} is unhealthy",
                    'details': data,
                    'severity': 'high'
                })
        
        # Resource alerts
        resources = health_data['system_resources']
        if not resources['cpu']['healthy']:
            alerts.append({
                'type': 'warning',
                'category': 'resources',
                'message': f"High CPU usage: {resources['cpu']['usage_percent']}%",
                'severity': 'medium'
            })
        
        if not resources['memory']['healthy']:
            alerts.append({
                'type': 'warning',
                'category': 'resources',
                'message': f"High memory usage: {resources['memory']['usage_percent']}%",
                'severity': 'medium'
            })
        
        if not resources['disk']['healthy']:
            alerts.append({
                'type': 'error',
                'category': 'resources',
                'message': f"High disk usage: {resources['disk']['usage_percent']}%",
                'severity': 'high'
            })
        
        # Database alerts
        if not health_data['database'].get('healthy', False):
            alerts.append({
                'type': 'error',
                'category': 'database',
                'message': "Database is unhealthy",
                'details': health_data['database'],
                'severity': 'high'
            })
        
        return alerts
    
    async def run_health_check(self) -> Dict[str, Any]:
        """Run comprehensive health check"""
        print("🏥 Running SmartGriev System Health Check...")
        
        start_time = time.time()
        
        # Collect all health data
        health_data = {
            'timestamp': datetime.now().isoformat(),
            'api': await self.check_api_health(),
            'frontend': await self.check_frontend_health(),
            'system_resources': self.check_system_resources(),
            'database': self.check_database_health(),
        }
        
        # Calculate overall health score
        health_score = self.calculate_system_score(health_data)
        health_data['overall_score'] = health_score
        health_data['status'] = 'healthy' if health_score >= 80 else 'degraded' if health_score >= 60 else 'unhealthy'
        
        # Generate alerts
        alerts = self.generate_alerts(health_data)
        health_data['alerts'] = alerts
        
        # Add timing
        health_data['check_duration_ms'] = round((time.time() - start_time) * 1000, 2)
        
        return health_data
    
    def print_health_report(self, health_data: Dict[str, Any]):
        """Print formatted health report"""
        print("\n" + "="*60)
        print("🏥 SMARTGRIEV SYSTEM HEALTH REPORT")
        print("="*60)
        print(f"📅 Timestamp: {health_data['timestamp']}")
        print(f"🎯 Overall Score: {health_data['overall_score']}/100")
        print(f"📊 Status: {health_data['status'].upper()}")
        print(f"⏱️ Check Duration: {health_data['check_duration_ms']}ms")
        
        # API Health
        print("\n🔧 API HEALTH:")
        for endpoint, data in health_data['api'].items():
            status = "✅" if data.get('healthy') else "❌"
            response_time = data.get('response_time_ms', 'N/A')
            print(f"  {status} {endpoint}: {response_time}ms")
        
        # Frontend Health
        frontend = health_data['frontend']
        frontend_status = "✅" if frontend.get('healthy') else "❌"
        print(f"\n⚛️ FRONTEND HEALTH:")
        print(f"  {frontend_status} Status: {frontend.get('status', 'Unknown')}")
        print(f"  📊 Response Time: {frontend.get('response_time_ms', 'N/A')}ms")
        
        # System Resources
        print(f"\n💻 SYSTEM RESOURCES:")
        resources = health_data['system_resources']
        cpu_status = "✅" if resources['cpu']['healthy'] else "❌"
        mem_status = "✅" if resources['memory']['healthy'] else "❌"
        disk_status = "✅" if resources['disk']['healthy'] else "❌"
        
        print(f"  {cpu_status} CPU: {resources['cpu']['usage_percent']}%")
        print(f"  {mem_status} Memory: {resources['memory']['usage_percent']}%")
        print(f"  {disk_status} Disk: {resources['disk']['usage_percent']}%")
        
        # Database Health
        db = health_data['database']
        db_status = "✅" if db.get('healthy') else "❌"
        print(f"\n🗄️ DATABASE HEALTH:")
        print(f"  {db_status} Status: {'Healthy' if db.get('healthy') else 'Unhealthy'}")
        if db.get('size_mb'):
            print(f"  📊 Size: {db['size_mb']} MB")
        
        # Alerts
        alerts = health_data['alerts']
        if alerts:
            print(f"\n🚨 ALERTS ({len(alerts)}):")
            for alert in alerts:
                icon = "🔴" if alert['severity'] == 'high' else "🟡"
                print(f"  {icon} {alert['message']}")
        else:
            print(f"\n🟢 NO ALERTS - System is operating normally")
        
        print("\n" + "="*60)
    
    def save_health_data(self, health_data: Dict[str, Any]):
        """Save health data to file for historical tracking"""
        health_dir = self.project_root / "monitoring" / "health_logs"
        health_dir.mkdir(parents=True, exist_ok=True)
        
        # Save daily log
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = health_dir / f"health_{today}.json"
        
        # Load existing data or create new
        if log_file.exists():
            with open(log_file, 'r') as f:
                daily_data = json.load(f)
        else:
            daily_data = []
        
        # Append new data
        daily_data.append(health_data)
        
        # Save updated data
        with open(log_file, 'w') as f:
            json.dump(daily_data, f, indent=2)
        
        print(f"📁 Health data saved to: {log_file}")

async def main():
    monitor = SystemHealthMonitor()
    
    # Run health check
    health_data = await monitor.run_health_check()
    
    # Print report
    monitor.print_health_report(health_data)
    
    # Save data
    monitor.save_health_data(health_data)
    
    # Return overall status
    return health_data['overall_score'] >= 80

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)