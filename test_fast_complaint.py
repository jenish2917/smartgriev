"""
Test complaint submission speed after performance optimization
"""
import requests
import time

def test_complaint_speed():
    print("🧪 Testing Complaint Submission Speed...")
    print("=" * 60)
    
    # Use the correct multimodal endpoint that the frontend uses
    url = "http://127.0.0.1:8000/api/complaints/submit/"
    
    # Test data - simple complaint (without category for now)
    data = {
        "title": "Test Complaint - Speed Check",
        "description": "Testing if complaint submission is now instant",
        "priority": "medium",
        "urgency_level": "medium",
        "incident_address": "Test Location"
    }
    
    print(f"\n📝 Submitting complaint to: {url}")
    print(f"Data: {data['title']}")
    
    # Measure time
    start_time = time.time()
    
    try:
        response = requests.post(url, data=data, timeout=30)
        end_time = time.time()
        elapsed = end_time - start_time
        
        print(f"\n⏱️  Response Time: {elapsed:.2f} seconds")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print("✅ SUCCESS - Complaint submitted!")
            
            # Check response
            try:
                result = response.json()
                if 'complaint' in result:
                    complaint_id = result['complaint'].get('id', 'N/A')
                    print(f"🆔 Complaint ID: {complaint_id}")
                elif 'id' in result:
                    print(f"🆔 Complaint ID: {result['id']}")
            except:
                pass
            
            # Performance assessment
            print(f"\n⚡ PERFORMANCE ASSESSMENT:")
            if elapsed < 1:
                print(f"   ✅ EXCELLENT - {elapsed:.2f}s (Under 1 second!)")
            elif elapsed < 3:
                print(f"   ✅ GOOD - {elapsed:.2f}s (Under 3 seconds)")
            elif elapsed < 5:
                print(f"   ⚠️  ACCEPTABLE - {elapsed:.2f}s (Under 5 seconds)")
            else:
                print(f"   ❌ SLOW - {elapsed:.2f}s (Still needs optimization)")
            
        else:
            print(f"❌ FAILED - Status: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
    except requests.exceptions.Timeout:
        end_time = time.time()
        elapsed = end_time - start_time
        print(f"❌ TIMEOUT after {elapsed:.2f} seconds")
        print("   The request took too long and was cancelled")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_complaint_speed()
