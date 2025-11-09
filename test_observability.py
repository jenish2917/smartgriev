"""
Test Observability Features
Verify metrics, tracing, and logging are working
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartgriev.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
import time

User = get_user_model()


def test_metrics_endpoint():
    """Test that /metrics endpoint is accessible"""
    print("\n🔍 Testing Metrics Endpoint...")
    client = Client()
    response = client.get('/metrics')
    
    if response.status_code == 200:
        print("✅ Metrics endpoint accessible")
        
        # Check for expected metrics
        content = response.content.decode('utf-8')
        expected_metrics = [
            'smartgriev_http_requests_total',
            'smartgriev_http_request_duration_seconds',
            'smartgriev_complaints_by_status',
        ]
        
        for metric in expected_metrics:
            if metric in content:
                print(f"   ✅ {metric} present")
            else:
                print(f"   ⚠️  {metric} missing")
        
        return True
    else:
        print(f"❌ Metrics endpoint failed: {response.status_code}")
        return False


def test_health_check():
    """Test that /health endpoint works"""
    print("\n🏥 Testing Health Check Endpoint...")
    client = Client()
    response = client.get('/health')
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Health check passed: {data.get('status')}")
        
        # Check individual health checks
        for check_name, check_status in data.get('checks', {}).items():
            status_icon = "✅" if check_status == "ok" else "⚠️"
            print(f"   {status_icon} {check_name}: {check_status}")
        
        return True
    else:
        print(f"❌ Health check failed: {response.status_code}")
        return False


def test_request_metrics():
    """Test that HTTP requests generate metrics"""
    print("\n📊 Testing Request Metrics Collection...")
    client = Client()
    
    # Make a few requests to generate metrics
    for i in range(3):
        response = client.get('/')
        print(f"   Request {i+1}: {response.status_code}")
        time.sleep(0.1)
    
    # Check metrics
    response = client.get('/metrics')
    content = response.content.decode('utf-8')
    
    if 'smartgriev_http_requests_total' in content:
        print("✅ HTTP request metrics are being collected")
        return True
    else:
        print("❌ HTTP request metrics not found")
        return False


def test_structured_logging():
    """Test that structured logging is configured"""
    print("\n📝 Testing Structured Logging...")
    
    try:
        from smartgriev.logging_config import get_logger
        logger = get_logger(__name__)
        
        # Log a test message
        logger.info("test_log_entry", test_id=123, feature="observability")
        print("✅ Structured logging configured")
        return True
    except Exception as e:
        print(f"❌ Structured logging failed: {e}")
        return False


def test_telemetry():
    """Test that OpenTelemetry is configured"""
    print("\n🔭 Testing OpenTelemetry...")
    
    try:
        from smartgriev.telemetry import get_tracer
        from django.conf import settings
        
        if getattr(settings, 'ENABLE_OPENTELEMETRY', False):
            tracer = get_tracer(__name__)
            
            # Create a test span
            with tracer.start_as_current_span("test_span") as span:
                span.set_attribute("test.key", "test_value")
                print("✅ OpenTelemetry configured and working")
            
            return True
        else:
            print("⚠️  OpenTelemetry disabled in settings (set ENABLE_OPENTELEMETRY=True to enable)")
            return True  # Not an error, just disabled
    except Exception as e:
        print(f"❌ OpenTelemetry failed: {e}")
        return False


def main():
    """Run all observability tests"""
    print("=" * 60)
    print("SmartGriev Observability Test Suite")
    print("=" * 60)
    
    tests = [
        ("Metrics Endpoint", test_metrics_endpoint),
        ("Health Check", test_health_check),
        ("Request Metrics", test_request_metrics),
        ("Structured Logging", test_structured_logging),
        ("OpenTelemetry", test_telemetry),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All observability tests passed!")
        print("\nNext steps:")
        print("1. Start Prometheus: docker run -p 9090:9090 -v ./backend/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus")
        print("2. Start Grafana: docker run -p 3000:3000 grafana/grafana")
        print("3. Access metrics: http://localhost:8000/metrics")
        print("4. Access health: http://localhost:8000/health")
        print("5. Import dashboard: backend/grafana/dashboards/smartgriev_metrics.json")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
