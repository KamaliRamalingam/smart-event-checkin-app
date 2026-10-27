"""Test cases for Event Checkin App."""

import pytest
import json
from app import app, events, attendees


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def auth_client(client):
    """Create an authenticated test client."""
    with client.session_transaction() as sess:
        sess['user_id'] = 'admin'
    return client


class TestAuthentication:
    """Test authentication endpoints."""

    def test_login_page_loads(self, client):
        """Test login page is accessible."""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Welcome back' in response.data

    def test_login_with_valid_credentials(self, client):
        """Test login with correct credentials."""
        response = client.post('/login', data={
            'userId': 'admin',
            'password': 'admin'
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_login_with_invalid_credentials(self, client):
        """Test login with wrong password."""
        response = client.post('/login', data={
            'userId': 'admin',
            'password': 'wrongpassword'
        })
        assert response.status_code == 200
        assert b'Invalid credentials' in response.data

    def test_logout(self, auth_client):
        """Test logout functionality."""
        response = auth_client.get('/logout', follow_redirects=True)
        assert response.status_code == 200


class TestEventsAPI:
    """Test events API endpoints."""

    def test_get_events_with_auth(self, auth_client):
        """Test getting all events."""
        response = auth_client.get('/api/events')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) >= 2

    def test_get_events_with_search_filter(self, auth_client):
        """Test filtering events by search query."""
        response = auth_client.get('/api/events?q=Tech')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) > 0

    def test_get_events_with_type_filter(self, auth_client):
        """Test filtering events by type."""
        response = auth_client.get('/api/events?type=Conference')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) > 0
        assert data[0]['type'] == 'Conference'

    def test_create_event(self, auth_client):
        """Test creating a new event."""
        new_event = {
            'title': 'Test Event',
            'type': 'Workshop',
            'start_date': '2026-04-01',
            'end_date': '2026-04-02',
            'capacity': 50,
            'payment': 'Free',
            'status': 'Active',
            'description': 'Test event description'
        }
        response = auth_client.post('/api/events',
                                    data=json.dumps(new_event),
                                    content_type='application/json')
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True

    def test_get_event_details(self, auth_client):
        """Test getting event details."""
        event_id = events[0]['id']
        response = auth_client.get(f'/api/events/{event_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'event' in data

    def test_get_nonexistent_event(self, auth_client):
        """Test getting non-existent event."""
        response = auth_client.get('/api/events/NONEXISTENT')
        assert response.status_code == 404


class TestAttendeesAPI:
    """Test attendees API endpoints."""

    def test_get_attendees(self, auth_client):
        """Test getting all attendees."""
        response = auth_client.get('/api/attendees')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) >= 2

    def test_get_attendees_with_search(self, auth_client):
        """Test searching attendees by name."""
        response = auth_client.get('/api/attendees?q=John')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) > 0

    def test_get_checked_in_attendees(self, auth_client):
        """Test filtering checked-in attendees."""
        response = auth_client.get('/api/attendees?ci=yes')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) > 0
        assert data[0]['checked_in'] is True

    def test_create_attendee(self, auth_client):
        """Test creating a new attendee."""
        new_attendee = {
            'name': 'Test Attendee',
            'email': 'test@example.com',
            'company': 'Test Corp',
            'job': 'Test Engineer',
            'event_title': events[0]['title'],
            'diet': 'Vegetarian'
        }
        response = auth_client.post('/api/attendees',
                                    data=json.dumps(new_attendee),
                                    content_type='application/json')
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True

    def test_get_attendee_details(self, auth_client):
        """Test getting attendee details."""
        attendee_id = attendees[0]['id']
        response = auth_client.get(f'/api/attendees/{attendee_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == attendee_id


class TestCheckInAPI:
    """Test check-in functionality."""

    def test_check_in_attendee(self, auth_client):
        """Test checking in an attendee."""
        attendee_id = attendees[1]['id']
        response = auth_client.post(f'/api/attendees/{attendee_id}/checkin')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

    def test_check_in_nonexistent_attendee(self, auth_client):
        """Test checking in non-existent attendee."""
        response = auth_client.post('/api/attendees/NONEXISTENT/checkin')
        assert response.status_code == 404


class TestQRCodeAPI:
    """Test QR code generation."""

    def test_get_qrcode_png(self, auth_client):
        """Test getting QR code as PNG."""
        attendee_id = attendees[0]['id']
        response = auth_client.get(f'/api/qrcode/{attendee_id}')
        assert response.status_code == 200
        assert response.content_type == 'image/png'

    def test_get_qrcode_base64(self, auth_client):
        """Test getting QR code as base64."""
        attendee_id = attendees[0]['id']
        response = auth_client.get(f'/api/qrcode-base64/{attendee_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'qrcode' in data
        assert data['qrcode'].startswith('data:image/png;base64,')


class TestStatisticsAPI:
    """Test statistics endpoint."""

    def test_get_stats(self, auth_client):
        """Test getting statistics."""
        response = auth_client.get('/api/stats')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'total_events' in data
        assert 'total_regs' in data
        assert 'checked_in' in data
        assert 'checkin_rate' in data


class TestLogsAPI:
    """Test logs endpoints."""

    def test_get_activity_logs(self, auth_client):
        """Test getting activity logs."""
        response = auth_client.get('/api/logs')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_security_logs(self, auth_client):
        """Test getting security logs."""
        response = auth_client.get('/api/security-logs')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) > 0


class TestExportAPI:
    """Test export functionality."""

    def test_export_attendees_csv(self, auth_client):
        """Test exporting attendees as CSV."""
        response = auth_client.get('/api/export/attendees')
        assert response.status_code == 200
        assert 'text/csv' in response.content_type
        assert b'name' in response.data

    def test_export_logs_csv(self, auth_client):
        """Test exporting logs as CSV."""
        response = auth_client.get('/api/export/logs')
        assert response.status_code == 200
        assert 'text/csv' in response.content_type
        assert b'action' in response.data


class TestPublicRegistration:
    """Test public registration endpoint."""

    def test_public_register(self, client):
        """Test public registration without authentication."""
        registration_data = {
            'name': 'Public User',
            'email': 'public@example.com',
            'company': 'Public Corp',
            'job': 'Public Engineer',
            'event_title': events[0]['title'],
            'diet': 'None'
        }
        response = client.post('/api/public/register',
                               data=json.dumps(registration_data),
                               content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

    def test_public_register_invalid_event(self, client):
        """Test public registration with invalid event."""
        registration_data = {
            'name': 'Public User',
            'email': 'public@example.com',
            'event_title': 'NONEXISTENT EVENT'
        }
        response = client.post('/api/public/register',
                               data=json.dumps(registration_data),
                               content_type='application/json')
        assert response.status_code == 404


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
